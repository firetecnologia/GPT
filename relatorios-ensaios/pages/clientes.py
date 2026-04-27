import streamlit as st

from modules.clients import create_client, list_clients


def render_clientes() -> None:
    st.title("Clientes")
    with st.form("novo_cliente"):
        st.subheader("Cadastrar cliente")
        name = st.text_input("Nome/Razão social *")
        document = st.text_input("CPF/CNPJ")
        contact_name = st.text_input("Contato principal")
        phone = st.text_input("Telefone")
        email = st.text_input("E-mail")
        address = st.text_area("Endereço")
        notes = st.text_area("Observações")
        submitted = st.form_submit_button("Salvar cliente")
        if submitted:
            if not name:
                st.error("Nome é obrigatório.")
            else:
                create_client(locals())
                st.success("Cliente cadastrado.")
                st.rerun()

    st.subheader("Lista de clientes")
    st.dataframe(list_clients(), use_container_width=True)
