"""Aplicação Streamlit do gerador de relatórios de ensaios."""

from datetime import date

import streamlit as st

from modules.auth import authenticate, ensure_default_admin
from modules.database import init_db
from pages.calculadora_estrutural import render_calculadora_estrutural
from pages.clientes import render_clientes
from pages.configuracoes import render_configuracoes
from pages.dashboard import render_dashboard
from pages.equipamentos import render_equipamentos
from pages.modelos import render_modelos
from pages.novo_relatorio import render_novo_relatorio
from pages.obras import render_obras
from pages.relatorios_emitidos import render_relatorios_emitidos
from pages.responsaveis import render_responsaveis
from pages.tipos_ensaio import render_tipos_ensaio


st.set_page_config(page_title="Relatórios de Ensaios", layout="wide")

init_db()
ensure_default_admin()
st.session_state["today_month"] = date.today().strftime("%Y-%m")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")
    with st.form("login_form"):
        email = st.text_input("E-mail", value="firetecnologia@gmail.com")
        password = st.text_input("Senha", type="password", value="1234")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            if authenticate(email, password):
                st.session_state.logged_in = True
                st.success("Login realizado com sucesso.")
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
    st.stop()

st.sidebar.title("Menu")
menu = st.sidebar.radio(
    "Navegação",
    [
        "Dashboard",
        "Novo relatório",
        "Relatórios emitidos",
        "Clientes",
        "Obras",
        "Modelos",
        "Tipos de ensaio",
        "Equipamentos",
        "Responsáveis técnicos",
        "Calculadora estrutural",
        "Configurações",
    ],
)

if menu == "Dashboard":
    render_dashboard()
elif menu == "Novo relatório":
    render_novo_relatorio()
elif menu == "Relatórios emitidos":
    render_relatorios_emitidos()
elif menu == "Clientes":
    render_clientes()
elif menu == "Obras":
    render_obras()
elif menu == "Modelos":
    render_modelos()
elif menu == "Tipos de ensaio":
    render_tipos_ensaio()
elif menu == "Equipamentos":
    render_equipamentos()
elif menu == "Responsáveis técnicos":
    render_responsaveis()
elif menu == "Calculadora estrutural":
    render_calculadora_estrutural()
elif menu == "Configurações":
    render_configuracoes()
