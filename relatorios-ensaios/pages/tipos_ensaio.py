import streamlit as st

from modules.reports import create_report_type, list_report_types


def render_tipos_ensaio() -> None:
    st.title("Tipos de ensaio")
    with st.form("novo_tipo"):
        name = st.text_input("Nome do tipo *")
        code = st.text_input("Código curto (ex: SPDA) *").upper()
        description = st.text_area("Descrição")
        default_objective = st.text_area("Objetivo padrão")
        default_methodology = st.text_area("Metodologia padrão")
        default_conclusion_ok = st.text_area("Conclusão padrão (atende)")
        default_conclusion_not_ok = st.text_area("Conclusão padrão (não atende)")
        submitted = st.form_submit_button("Salvar tipo")
        if submitted:
            if not name or not code:
                st.error("Nome e código são obrigatórios.")
            else:
                try:
                    create_report_type(locals())
                    st.success("Tipo de ensaio cadastrado.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Erro ao cadastrar: {exc}")

    st.dataframe(list_report_types(), use_container_width=True)
