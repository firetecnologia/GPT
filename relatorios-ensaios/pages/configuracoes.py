import streamlit as st

from modules.database import get_company_settings, upsert_company_settings


def render_configuracoes() -> None:
    st.title("Configurações da empresa")
    current = get_company_settings()

    with st.form("company_settings"):
        company_name = st.text_input("Nome da empresa", value=current.get("company_name", ""))
        cnpj = st.text_input("CNPJ", value=current.get("cnpj", ""))
        address = st.text_input("Endereço", value=current.get("address", ""))
        phone = st.text_input("Telefone", value=current.get("phone", ""))
        email = st.text_input("E-mail", value=current.get("email", ""))
        website = st.text_input("Site", value=current.get("website", ""))
        footer_text = st.text_area("Rodapé padrão", value=current.get("footer_text", ""))
        technical_disclaimer = st.text_area(
            "Texto de responsabilidade técnica", value=current.get("technical_disclaimer", "")
        )
        submitted = st.form_submit_button("Salvar configurações")

        if submitted:
            upsert_company_settings(locals())
            st.success("Configurações salvas.")
