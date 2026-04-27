"""Regras de negócio dos relatórios."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from modules.database import execute, execute_many, rows, dump_json, load_json

BASE_DIR = Path(__file__).resolve().parents[1]
GENERATED_DIR = BASE_DIR / "data" / "generated_reports"


STATUS_VALUES = ["Rascunho", "Em revisão", "Emitido", "Revisado", "Cancelado"]


def list_report_types():
    return rows("SELECT * FROM report_types ORDER BY created_at DESC")


def create_report_type(payload: dict):
    return execute(
        """
        INSERT INTO report_types (
            name, code, description, default_objective, default_methodology,
            default_conclusion_ok, default_conclusion_not_ok
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.get("name"),
            payload.get("code"),
            payload.get("description"),
            payload.get("default_objective"),
            payload.get("default_methodology"),
            payload.get("default_conclusion_ok"),
            payload.get("default_conclusion_not_ok"),
        ),
    )


def next_report_number(report_type_code: str, report_date: date) -> str:
    year = report_date.year
    prefix = f"REL-{year}-{report_type_code.upper()}"
    result = rows(
        "SELECT report_number FROM reports WHERE report_number LIKE ? ORDER BY report_number DESC LIMIT 1",
        (f"{prefix}-%",),
    )
    seq = 1
    if result:
        last = result[0]["report_number"].split("-")[-1]
        if last.isdigit():
            seq = int(last) + 1
    return f"{prefix}-{seq:03d}"


def suggest_conclusion(results: list[dict], text_ok: str | None = None, text_not_ok: str | None = None) -> str:
    statuses = {str(r.get("status", "")).strip().lower() for r in results}
    if statuses and statuses.issubset({"atende"}):
        return text_ok or (
            "Com base nas verificações realizadas, conclui-se que os itens avaliados "
            "atendem aos critérios técnicos adotados para este ensaio."
        )
    if "não atende" in statuses:
        return text_not_ok or (
            "Foram identificados itens que não atendem aos critérios técnicos adotados. "
            "Recomenda-se adequação e nova verificação."
        )
    return "Conclusão preliminar gerada. Revise manualmente antes de emitir o relatório."


def create_report(payload: dict, results_data: list[dict], photos_data: list[dict]) -> int:
    report_id = execute(
        """
        INSERT INTO reports (
            report_number, report_type_id, template_id, client_id, work_id, technician_id,
            date_test, date_issue, status, general_data_json, conclusion, observations, generated_docx_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.get("report_number"),
            payload.get("report_type_id"),
            payload.get("template_id"),
            payload.get("client_id"),
            payload.get("work_id"),
            payload.get("technician_id"),
            payload.get("date_test"),
            payload.get("date_issue"),
            payload.get("status", "Emitido"),
            dump_json(payload.get("general_data", {})),
            payload.get("conclusion"),
            payload.get("observations"),
            payload.get("generated_docx_path"),
        ),
    )

    if results_data:
        execute_many(
            """
            INSERT INTO report_results (
                report_id, item_number, location, measured_value, reference_value,
                unit, acceptance_criteria, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    report_id,
                    row.get("item_number"),
                    row.get("location"),
                    row.get("measured_value"),
                    row.get("reference_value"),
                    row.get("unit"),
                    row.get("acceptance_criteria"),
                    row.get("status"),
                    row.get("notes"),
                )
                for row in results_data
            ],
        )

    if photos_data:
        execute_many(
            """
            INSERT INTO report_photos (report_id, image_path, caption, category, display_order, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    report_id,
                    row.get("image_path"),
                    row.get("caption"),
                    row.get("category"),
                    row.get("display_order"),
                    row.get("notes"),
                )
                for row in photos_data
            ],
        )

    return report_id


def list_reports():
    data = rows(
        """
        SELECT r.*, rt.name AS report_type_name, c.name AS client_name,
               w.name AS work_name, t.name AS technician_name
        FROM reports r
        JOIN report_types rt ON rt.id = r.report_type_id
        JOIN clients c ON c.id = r.client_id
        JOIN works w ON w.id = r.work_id
        JOIN technicians t ON t.id = r.technician_id
        ORDER BY r.created_at DESC
        """
    )
    return data


def get_report_detail(report_id: int):
    report = rows("SELECT * FROM reports WHERE id = ?", (report_id,))
    if not report:
        return None
    base = report[0]
    base["general_data"] = load_json(base.get("general_data_json"), {})
    base["results"] = rows("SELECT * FROM report_results WHERE report_id = ? ORDER BY id", (report_id,))
    base["photos"] = rows("SELECT * FROM report_photos WHERE report_id = ? ORDER BY display_order, id", (report_id,))
    return base
