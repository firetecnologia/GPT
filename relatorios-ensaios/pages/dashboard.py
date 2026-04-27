import streamlit as st

from modules.reports import list_reports


def render_dashboard() -> None:
    st.title("Dashboard")
    reports = list_reports()

    total = len(reports)
    drafts = len([r for r in reports if r["status"] == "Rascunho"])
    month = len([r for r in reports if str(r["date_issue"])[:7] == str(st.session_state.get("today_month", ""))])

    c1, c2, c3 = st.columns(3)
    c1.metric("Relatórios emitidos", total)
    c2.metric("Rascunhos", drafts)
    c3.metric("Emitidos no mês", month)

    st.subheader("Últimos relatórios")
    st.dataframe(reports[:10], use_container_width=True)
