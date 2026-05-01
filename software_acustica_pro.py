import cv2
import numpy as np
import pandas as pd
from scipy.ndimage import label


class SoftwareAcusticaPro:
    def __init__(self):
        # Banco de Dados de Engenharia de Materiais (Propriedades Físicas)
        self.materiais = pd.DataFrame(
            {
                "nome": ["Alvenaria_14", "Concreto_15", "Drywall_Simples", "Vidro_6mm"],
                "densidade_kg_m3": [1200, 2400, 800, 2500],
                "modulo_young_pa": [3.5e9, 30e9, 2.5e9, 70e9],
                "resistencia_mpa": [3.0, 25.0, 0.5, 50.0],
                "amortecimento": [0.015, 0.005, 0.03, 0.001],
                "espessura_m": [0.14, 0.15, 0.10, 0.006],
            }
        ).set_index("nome")

        # Parâmetros NBR 15575 (Limites de Desempenho Mínimo)
        self.norma_15575 = {
            "parede_externa": 30,  # Rw
            "entre_unidades": 45,  # Rw
            "entre_dormitorios": 45,  # Rw
        }

    # --- PILAR 1: VISÃO COMPUTACIONAL (PDF -> GEOMETRIA) ---
    def processar_geometria(self, imagem_planta):
        """Identifica ambientes e paredes automaticamente."""
        gray = cv2.cvtColor(imagem_planta, cv2.COLOR_BGR2GRAY)
        # Detecção de bordas para identificar paredes
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Identificar salas (espaços vazios fechados por paredes)
        inv_edges = cv2.bitwise_not(edges)
        lab, n_features = label(inv_edges)

        # Extração de dimensões (exemplo simplificado de escala)
        ambientes = []
        for i in range(1, n_features + 1):
            area = np.sum(lab == i)
            if area > 1000:  # Filtra ruídos pequenos
                ambientes.append({"id": i, "area_pixels": area})

        return ambientes, edges

    # --- PILAR 2: MOTOR DE FÍSICA ACÚSTICA (CÁLCULO DE TRANSMISSÃO) ---
    def calcular_perda_transmissao(self, material_nome, frequencia):
        """Calcula isolamento considerando Massa, Rigidez e Ressonância."""
        m = self.materiais.loc[material_nome]
        massa_sup = m["densidade_kg_m3"] * m["espessura_m"]

        # 1. Lei da Massa (Isolamento Aéreo)
        r_massa = 20 * np.log10(massa_sup * frequencia) - 47

        # 2. Frequência Crítica (Ressonância)
        # B = Rigidez à flexão: (E * h^3) / (12 * (1 - v^2))
        b = (m["modulo_young_pa"] * (m["espessura_m"] ** 3)) / 10.9
        fc = (343**2 / (2 * np.pi)) * np.sqrt(massa_sup / b)

        # Ajuste de ressonância: se a freq está perto da fc, o isolamento cai
        if 0.8 * fc < frequencia < 1.2 * fc:
            r_total = r_massa - 15  # Queda por ressonância
        else:
            r_total = r_massa

        return max(r_total, 0)

    def simulacao_vibracao_estrutural(self, material_origem, material_destino):
        """Analisa a transferência de ruído por vibração (Flanking)."""
        # Simplificação do Kij (Índice de redução de vibração em junções)
        # Quanto maior a diferença de rigidez, maior a perda na transmissão
        e1 = self.materiais.loc[material_origem, "modulo_young_pa"]
        e2 = self.materiais.loc[material_destino, "modulo_young_pa"]
        kij = 10 * np.log10(e1 / e2) if e1 > e2 else 5
        return abs(kij)

    # --- ORQUESTRADOR FINAL ---
    def executar_diagnostico(self, imagem, tipo_parede="entre_unidades"):
        # 1. Obter dados da planta
        ambientes, _mapa = self.processar_geometria(imagem)

        # 2. Simular para uma faixa de frequências (125Hz a 4000Hz)
        freqs = [125, 250, 500, 1000, 2000, 4000]
        resultados = []

        for f in freqs:
            r = self.calcular_perda_transmissao("Alvenaria_14", f)
            resultados.append(r)

        rw_final = np.mean(resultados)  # Média simplificada para Rw

        # 3. Validar NBR 15575
        meta = self.norma_15575[tipo_parede]
        status = "CONFORME" if rw_final >= meta else "NÃO CONFORME"

        return {
            "Ambientes Detectados": len(ambientes),
            "Rw Calculado (Aéreo)": round(rw_final, 2),
            "Meta Normativa": meta,
            "Eficiência": status,
            "Risco de Ressonância": "Baixo" if rw_final > meta + 5 else "Alto",
        }


# --- EXEMPLO DE EXECUÇÃO ---
# software = SoftwareAcusticaPro()
# report = software.executar_diagnostico(imagem_da_planta_em_array)
# print(report)
