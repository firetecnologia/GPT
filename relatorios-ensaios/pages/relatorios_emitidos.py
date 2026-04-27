from pathlib import Path

import streamlit as st

from modules.reports import get_report_detail, list_reports


def render_relatorios_emitidos() -> None:
    st.title("Relatórios emitidos")
    reports = list_reports()
    st.dataframe(reports, use_container_width=True)

    if not reports:
        return

    report_map = {f"{r['report_number']} - {r['client_name']}": r for r in reports}
    selected = st.selectbox("Selecionar relatório para ações", list(report_map.keys()))
    row = report_map[selected]

    doc_path = row.get("generated_docx_path")
    if doc_path and Path(doc_path).exists():
        with open(doc_path, "rb") as fp:
            st.download_button("Baixar DOCX", fp.read(), file_name=Path(doc_path).name)

    detail = get_report_detail(row["id"])
    if st.button("Duplicar para novo rascunho"):
        st.session_state["duplicate_report"] = detail
        st.success("Dados copiados para a tela Novo relatório.")
