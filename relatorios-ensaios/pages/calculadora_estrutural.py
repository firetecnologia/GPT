import math

import streamlit as st

from modules.database import rows


NBR_HINTS = {
    "Concreto armado": [
        "NBR 6118 (Projeto de estruturas de concreto)",
        "NBR 6120 (Ações para cálculo de estruturas)",
        "NBR 6123 (Ações do vento em edificações)",
    ],
    "Aço": [
        "NBR 8800 (Projeto de estruturas de aço e mistas)",
        "NBR 6120 (Ações para cálculo de estruturas)",
    ],
    "Madeira": [
        "NBR 7190 (Projeto de estruturas de madeira)",
        "NBR 6120 (Ações para cálculo de estruturas)",
    ],
}


def _calc_viga_biapoiada(q_kN_m: float, l_m: float) -> dict[str, float]:
    momento = q_kN_m * (l_m**2) / 8
    cortante = q_kN_m * l_m / 2
    flecha = (5 * q_kN_m * (l_m**4)) / 384
    return {"momento": momento, "cortante": cortante, "flecha_rel": flecha}


def render_calculadora_estrutural() -> None:
    st.title("Calculadora Estrutural (pré-dimensionamento)")
    st.warning(
        "Ferramenta para estimativas iniciais. Sempre validar em projeto executivo por engenheiro civil habilitado."
    )

    tipo = st.selectbox("Tipo de estrutura", list(NBR_HINTS.keys()))
    st.caption("Referências normativas sugeridas:")
    for item in NBR_HINTS[tipo]:
        st.write(f"- {item}")

    st.subheader("Cálculo rápido: Viga biapoiada com carga distribuída")
    col1, col2 = st.columns(2)
    with col1:
        vao = st.number_input("Vão (m)", min_value=0.5, value=5.0, step=0.1)
    with col2:
        carga = st.number_input("Carga distribuída q (kN/m)", min_value=0.1, value=10.0, step=0.1)

    if st.button("Calcular"):
        result = _calc_viga_biapoiada(carga, vao)
        st.success("Resultados calculados")
        st.metric("Momento fletor máximo (kN.m)", f"{result['momento']:.2f}")
        st.metric("Esforço cortante máximo (kN)", f"{result['cortante']:.2f}")
        st.metric("Indicador relativo de flecha", f"{result['flecha_rel']:.2f}")

    st.subheader("Leitura de projeto em PDF")
    pdf_file = st.file_uploader("Envie um PDF de projeto", type=["pdf"])
    if pdf_file is not None:
        try:
            from pypdf import PdfReader

            reader = PdfReader(pdf_file)
            pages_to_read = min(len(reader.pages), 5)
            texto = "\n".join((reader.pages[i].extract_text() or "") for i in range(pages_to_read))
            st.info(f"PDF carregado com {len(reader.pages)} página(s). Prévia das primeiras {pages_to_read}.")
            st.text_area("Texto extraído", value=texto[:5000], height=250)
        except Exception as exc:
            st.error(f"Falha ao ler PDF: {exc}")

    st.subheader("Bibliografia de referência")
    st.write("- ARAÚJO, José Milton de. Curso de Concreto Armado.")
    st.write("- PINHEIRO, Libânio M. Fundamentos do Concreto e Projeto de Edifícios.")
    st.write("- PFEIL, Walter. Estruturas de Aço: Dimensionamento Prático.")

    st.subheader("Tipos de ensaio cadastrados (base interna)")
    tipos = rows("SELECT name, code FROM report_types ORDER BY name")
    if tipos:
        st.dataframe(tipos, use_container_width=True)
    else:
        st.caption("Nenhum tipo de ensaio cadastrado ainda.")
