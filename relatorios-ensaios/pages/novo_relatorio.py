from __future__ import annotations

from datetime import date
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from modules.clients import list_clients
from modules.docx_generator import generate_report_docx
from modules.equipments import list_equipments
from modules.image_utils import process_image
from modules.reports import create_report, list_report_types, next_report_number, suggest_conclusion
from modules.templates import list_templates
from modules.technicians import list_technicians
from modules.works import list_works

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
GENERATED_DIR = BASE_DIR / "data" / "generated_reports"

PHOTO_CATEGORIES = [
    "Fachada/local da obra",
    "Equipamento utilizado",
    "Execução do ensaio",
    "Ponto de medição",
    "Resultado encontrado",
    "Não conformidade",
    "Detalhe técnico",
    "Evidência geral",
]


def _default_results_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "item_number": "01",
                "location": "",
                "measured_value": "",
                "reference_value": "",
                "unit": "",
                "acceptance_criteria": "",
                "status": "Atende",
                "notes": "",
            }
        ]
    )


def _safe_index(options: list[str], value: str | None) -> int:
    if not value or value not in options:
        return 0
    return options.index(value)


def render_novo_relatorio() -> None:
    st.title("Novo relatório")

    duplicate_data = st.session_state.get("duplicate_report")

    clients = list_clients()
    works = list_works()
    techs = list_technicians()
    equips = list_equipments()
    types = list_report_types()
    templates = list_templates(active_only=True)

    if not all([clients, works, techs, types, templates]):
        st.warning("Cadastre clientes, obras, responsáveis, tipos e modelos antes de emitir relatório.")
        return

    type_options = {f"{t['name']} ({t['code']})": t for t in types}
    client_options = {f"{c['name']} (ID {c['id']})": c for c in clients}
    work_options = {f"{w['name']} - {w['client_name']}": w for w in works}
    tech_options = {f"{t['name']} ({t.get('registration_number') or 'sem registro'})": t for t in techs}
    equip_options = {f"{e['name']} ({e.get('serial_number') or 's/n'})": e for e in equips}

    pre_type = None
    pre_client = None
    pre_work = None
    pre_tech = None
    pre_results = _default_results_df()
    pre_dynamic = {}

    if duplicate_data:
        pre_dynamic = duplicate_data.get("general_data", {})
        pre_results = pd.DataFrame(duplicate_data.get("results") or _default_results_df().to_dict(orient="records"))
        for label, data in type_options.items():
            if data["id"] == duplicate_data.get("report_type_id"):
                pre_type = label
        for label, data in client_options.items():
            if data["id"] == duplicate_data.get("client_id"):
                pre_client = label
        for label, data in work_options.items():
            if data["id"] == duplicate_data.get("work_id"):
                pre_work = label
        for label, data in tech_options.items():
            if data["id"] == duplicate_data.get("technician_id"):
                pre_tech = label
        st.info("Modo duplicação ativo: os dados foram pré-preenchidos para ajuste.")

    with st.form("novo_relatorio_form"):
        st.subheader("1) Dados gerais")
        type_labels = list(type_options.keys())
        selected_type_label = st.selectbox("Tipo de ensaio *", type_labels, index=_safe_index(type_labels, pre_type))
        selected_type = type_options[selected_type_label]

        templates_for_type = [tp for tp in templates if tp["report_type_id"] == selected_type["id"]]
        if not templates_for_type:
            st.error("Não há modelo ativo para esse tipo de ensaio.")
            st.form_submit_button("Gerar relatório DOCX", disabled=True)
            return

        template_options = {f"{tp['name']} v{tp['version']}": tp for tp in templates_for_type}
        selected_template_label = st.selectbox("Modelo de relatório *", list(template_options.keys()))
        selected_template = template_options[selected_template_label]

        client_labels = list(client_options.keys())
        work_labels = list(work_options.keys())
        tech_labels = list(tech_options.keys())

        selected_client_label = st.selectbox("Cliente *", client_labels, index=_safe_index(client_labels, pre_client))
        selected_work_label = st.selectbox("Obra *", work_labels, index=_safe_index(work_labels, pre_work))
        date_test = st.date_input("Data do ensaio *", value=date.today())
        date_issue = st.date_input("Data de emissão *", value=date.today())
        selected_tech_label = st.selectbox("Responsável técnico *", tech_labels, index=_safe_index(tech_labels, pre_tech))
        selected_equip_labels = st.multiselect("Equipamentos utilizados", list(equip_options.keys()))

        st.subheader("2) Campos específicos")
        dynamic_data = {}
        for field in selected_template["required_fields"]:
            dynamic_data[field] = st.text_input(f"{field} *", value=pre_dynamic.get(field, ""))
        for field in selected_template["optional_fields"]:
            dynamic_data[field] = st.text_input(field, value=pre_dynamic.get(field, ""))

        st.subheader("3) Resultados")
        results_df = st.data_editor(
            pre_results,
            num_rows="dynamic",
            use_container_width=True,
            key="results_editor",
        )

        st.subheader("4) Fotos")
        uploads = st.file_uploader(
            "Faça upload de fotos",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
        )

        st.subheader("5) Observações e conclusão")
        observations = st.text_area("Observações técnicas", value=(duplicate_data or {}).get("observations", ""))

        statuses = [str(v).strip().lower() for v in results_df["status"].tolist() if str(v).strip()]
        auto_conclusion = suggest_conclusion(
            results_df.to_dict(orient="records"),
            selected_type.get("default_conclusion_ok"),
            selected_type.get("default_conclusion_not_ok"),
        )
        conclusion = st.text_area(
            "Conclusão (editável)",
            value=(duplicate_data or {}).get("conclusion", auto_conclusion),
        )

        st.subheader("6) Revisão")
        st.write(f"Resultados preenchidos: **{len(results_df)}**")
        st.write(f"Fotos carregadas: **{len(uploads) if uploads else 0}**")
        st.write(f"Situações informadas: **{', '.join(sorted(set(statuses))) if statuses else 'sem status'}**")

        submitted = st.form_submit_button("Gerar relatório DOCX")

    if not submitted:
        return

    required_errors = []
    for field in selected_template["required_fields"]:
        if not str(dynamic_data.get(field, "")).strip():
            required_errors.append(f"Campo obrigatório não preenchido: {field}")
    if selected_template["accepts_results_table"] and results_df.empty:
        required_errors.append("O modelo exige ao menos uma linha de resultado.")
    if selected_template["accepts_photos"] and not uploads:
        required_errors.append("O modelo exige ao menos uma foto.")

    if required_errors:
        for msg in required_errors:
            st.error(msg)
        return

    selected_client = client_options[selected_client_label]
    selected_work = work_options[selected_work_label]
    selected_tech = tech_options[selected_tech_label]
    selected_equips = [equip_options[label] for label in selected_equip_labels]

    report_number = next_report_number(selected_type["code"], date_test)

    saved_photos = []
    if uploads:
        for idx, up in enumerate(uploads, start=1):
            ext = Path(up.name).suffix.lower() or ".jpg"
            raw_path = UPLOAD_DIR / f"{uuid4().hex}{ext}"
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(up.getbuffer())
            final_path = UPLOAD_DIR / f"{uuid4().hex}.jpg"
            process_image(str(raw_path), str(final_path))
            raw_path.unlink(missing_ok=True)
            saved_photos.append(
                {
                    "image_path": str(final_path),
                    "caption": f"Foto {idx}",
                    "category": PHOTO_CATEGORIES[(idx - 1) % len(PHOTO_CATEGORIES)],
                    "display_order": idx,
                    "notes": "",
                }
            )

    results_data = results_df.fillna("").to_dict(orient="records")
    equipment_text = ", ".join(
        [f"{e['name']} ({e.get('brand', '')} {e.get('model', '')})".strip() for e in selected_equips]
    )

    context = {
        "report_number": report_number,
        "cliente_nome": selected_client["name"],
        "obra_nome": selected_work["name"],
        "obra_endereco": selected_work.get("address", ""),
        "data_ensaio": str(date_test),
        "responsavel_tecnico": selected_tech["name"],
        "registro_responsavel": selected_tech.get("registration_number", ""),
        "tipo_ensaio": selected_type["name"],
        "objetivo": selected_type.get("default_objective") or dynamic_data.get("objetivo", ""),
        "metodologia": selected_type.get("default_methodology") or dynamic_data.get("metodologia", ""),
        "equipamentos_utilizados": equipment_text,
        "resultados": results_data,
        "conclusao": conclusion,
        "observacoes": observations,
        **dynamic_data,
    }

    safe_client = selected_client["name"].replace(" ", "_")
    safe_work = selected_work["name"].replace(" ", "_")
    output_path = GENERATED_DIR / f"{report_number}_{safe_client}_{safe_work}.docx"

    generate_report_docx(
        template_path=selected_template["file_path"],
        output_path=str(output_path),
        context=context,
        photos=saved_photos,
    )

    report_id = create_report(
        payload={
            "report_number": report_number,
            "report_type_id": selected_type["id"],
            "template_id": selected_template["id"],
            "client_id": selected_client["id"],
            "work_id": selected_work["id"],
            "technician_id": selected_tech["id"],
            "date_test": str(date_test),
            "date_issue": str(date_issue),
            "status": "Emitido",
            "general_data": dynamic_data,
            "conclusion": conclusion,
            "observations": observations,
            "generated_docx_path": str(output_path),
        },
        results_data=results_data,
        photos_data=saved_photos,
    )

    st.session_state.pop("duplicate_report", None)

    st.success(f"Relatório gerado com sucesso! Nº {report_number} (ID interno {report_id}).")
    with open(output_path, "rb") as fp:
        st.download_button("Baixar DOCX gerado", fp.read(), file_name=output_path.name)
