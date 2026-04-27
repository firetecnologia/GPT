from pathlib import Path

import streamlit as st

from modules.reports import list_report_types
from modules.templates import TEMPLATE_DIR, create_template, extract_placeholders_from_docx, list_templates


def render_modelos() -> None:
    st.title("Modelos de relatório")
    report_types = list_report_types()
    if not report_types:
        st.warning("Cadastre um tipo de ensaio antes de cadastrar modelos.")
        return

    options = {f"{r['name']} ({r['code']})": r for r in report_types}

    with st.form("novo_modelo"):
        model_name = st.text_input("Nome do modelo *")
        selected_type = st.selectbox("Tipo de ensaio *", list(options.keys()))
        version = st.number_input("Versão", min_value=1, step=1)
        accepts_photos = st.checkbox("Aceita fotos", value=True)
        accepts_results_table = st.checkbox("Aceita tabela de resultados", value=True)
        file = st.file_uploader("Upload do template DOCX", type=["docx"])

        required_fields_txt = st.text_input("Campos obrigatórios (vírgula) - opcional")
        optional_fields_txt = st.text_input("Campos opcionais (vírgula) - opcional")

        submitted = st.form_submit_button("Salvar modelo")
        if submitted:
            if not model_name or not file:
                st.error("Nome e arquivo DOCX são obrigatórios.")
                return

            TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
            file_path = TEMPLATE_DIR / file.name
            file_path.write_bytes(file.getbuffer())

            detected = extract_placeholders_from_docx(str(file_path))
            if detected:
                st.info(f"Placeholders detectados: {', '.join(detected)}")

            required_fields = [f.strip() for f in required_fields_txt.split(",") if f.strip()]
            optional_fields = [f.strip() for f in optional_fields_txt.split(",") if f.strip()]

            if not required_fields and detected:
                required_fields = detected

            create_template(
                {
                    "report_type_id": options[selected_type]["id"],
                    "name": model_name,
                    "file_path": str(file_path),
                    "version": int(version),
                    "required_fields": required_fields,
                    "optional_fields": optional_fields,
                    "accepts_photos": accepts_photos,
                    "accepts_results_table": accepts_results_table,
                }
            )
            st.success("Modelo salvo com sucesso.")
            st.rerun()

    st.subheader("Modelos cadastrados")
    st.dataframe(list_templates(), use_container_width=True)
