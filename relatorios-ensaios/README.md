# Relatórios de Ensaios da Construção Civil (MVP)

Aplicação web em **Python + Streamlit** para criar, preencher, organizar e exportar relatórios técnicos de ensaios em **DOCX editável**.

## ✅ O que o MVP já entrega

- Login simples (usuário administrador).
- Dashboard com visão rápida de relatórios.
- CRUDs principais:
  - Clientes
  - Obras
  - Responsáveis técnicos
  - Equipamentos
  - Tipos de ensaio
  - Modelos de relatório DOCX
- Tela **Novo relatório** com fluxo guiado:
  1. Dados gerais
  2. Campos dinâmicos do modelo
  3. Tabela de resultados
  4. Upload de fotos
  5. Observações e conclusão automática editável
  6. Revisão e geração
- Geração de `.docx` com `docxtpl`.
- Histórico em **Relatórios emitidos** com download do DOCX.
- Banco SQLite com tabelas mínimas do projeto.

---

## Estrutura de pastas

```text
relatorios-ensaios/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── seed_data.py
├── create_sample_template.py
├── data/
│   ├── database.db
│   ├── uploads/
│   ├── generated_reports/
│   └── templates/
├── modules/
└── pages/
```

---

## Requisitos

- Python 3.10+
- pip

## Instalação local

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Executar localmente

```bash
streamlit run app.py
```

Login padrão do MVP:

- **E-mail:** `admin@empresa.com`
- **Senha:** `admin123`

> Altere depois no banco para produção.

---

## Criar dados de exemplo

```bash
python seed_data.py
```

Esse script cria:

- Cliente exemplo
- Obra exemplo
- Responsável técnico exemplo
- Equipamento exemplo
- Tipo de ensaio exemplo

## Criar modelo DOCX exemplo

```bash
python create_sample_template.py
```

Arquivo gerado:

- `data/templates/modelo_exemplo.docx`

Depois, acesse **Modelos** no sistema e faça o upload desse arquivo.

---

## Como cadastrar placeholders no Word

No template `.docx`, use placeholders Jinja:

```text
{{ cliente_nome }}
{{ obra_nome }}
{{ data_ensaio }}
{{ responsavel_tecnico }}
{{ conclusao }}
```

Para listas:

```text
{% for item in resultados %}
Item {{ item.item_number }} - {{ item.location }}
{% endfor %}
```

Para fotos:

```text
{% for foto in fotos %}
{{ foto.imagem }}
Figura {{ loop.index }} — {{ foto.legenda }}
{% endfor %}
```

---

## Fluxo recomendado de uso

1. Cadastre clientes.
2. Cadastre obras.
3. Cadastre responsáveis técnicos.
4. Cadastre equipamentos.
5. Cadastre tipos de ensaio.
6. Cadastre modelos DOCX.
7. Vá em **Novo relatório**.
8. Preencha dados, resultados e fotos.
9. Revise conclusão.
10. Clique em **Gerar relatório DOCX**.
11. Baixe o arquivo em Word e edite se necessário.

---

## Deploy inicial (simples)

Você pode publicar no:

- Streamlit Community Cloud
- Render
- Railway

Passos gerais:

1. Subir projeto no GitHub.
2. Conectar o repositório ao serviço de deploy.
3. Definir comando de start:
   - `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Garantir persistência do banco/arquivos (volume ou storage externo) em produção.

---

## Segurança e observações

- O MVP usa autenticação simples para acelerar implantação inicial.
- Senhas são armazenadas com hash (`passlib[bcrypt]`).
- Não versione uploads reais e relatórios gerados.
- Em produção, recomendamos migrar para PostgreSQL e storage dedicado.

---

## Evoluções futuras sugeridas

- Exportação em PDF
- Assinatura digital
- Controle de revisão avançado
- Fluxo de aprovação interna
- Compartilhamento com cliente
- Integrações com nuvem (Drive/S3)

