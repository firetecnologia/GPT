import streamlit as st

from modules.clients import list_clients
from modules.works import create_work, list_works


def render_obras() -> None:
    st.title("Obras")
    clients = list_clients()
    if not clients:
        st.warning("Cadastre ao menos um cliente antes de cadastrar obras.")
        return

    client_options = {f"{c['name']} (ID {c['id']})": c["id"] for c in clients}
    with st.form("nova_obra"):
        st.subheader("Cadastrar obra")
        selected = st.selectbox("Cliente vinculado *", list(client_options.keys()))
        name = st.text_input("Nome da obra *")
        address = st.text_input("Endereço")
        city = st.text_input("Cidade")
        state = st.text_input("Estado")
        building_type = st.text_input("Tipo de edificação")
        contact_person = st.text_input("Responsável pelo acompanhamento")
        notes = st.text_area("Observações")
        submitted = st.form_submit_button("Salvar obra")
        if submitted:
            if not name:
                st.error("Nome da obra é obrigatório.")
            else:
                create_work(
                    {
                        "client_id": client_options[selected],
                        "name": name,
                        "address": address,
                        "city": city,
                        "state": state,
                        "building_type": building_type,
                        "contact_person": contact_person,
                        "notes": notes,
                    }
                )
                st.success("Obra cadastrada.")
                st.rerun()

    st.subheader("Lista de obras")
    st.dataframe(list_works(), use_container_width=True)
