import streamlit as st

from modules.technicians import create_technician, list_technicians


def render_responsaveis() -> None:
    st.title("Responsáveis técnicos")
    with st.form("novo_resp"):
        name = st.text_input("Nome completo *")
        profession = st.text_input("Formação")
        registration_number = st.text_input("CREA/CAU")
        role = st.text_input("Cargo")
        email = st.text_input("E-mail")
        phone = st.text_input("Telefone")
        submitted = st.form_submit_button("Salvar responsável")
        if submitted:
            if not name:
                st.error("Nome é obrigatório.")
            else:
                create_technician(locals())
                st.success("Responsável cadastrado.")
                st.rerun()

    st.dataframe(list_technicians(), use_container_width=True)
