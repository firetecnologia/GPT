"""Gerenciamento de modelos DOCX."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

from modules.database import dump_json, execute, load_json, rows

BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = BASE_DIR / "data" / "templates"

PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}")


def extract_placeholders_from_docx(file_path: str) -> list[str]:
    """Extrai placeholders `{{ campo }}` de um DOCX sem depender de python-docx."""
    path = Path(file_path)
    if not path.exists():
        return []

    try:
        with zipfile.ZipFile(path) as archive:
            xml_parts = []
            for member in archive.namelist():
                if member.startswith("word/") and member.endswith(".xml"):
                    xml_parts.append(archive.read(member).decode("utf-8", errors="ignore"))
        raw_xml = "\n".join(xml_parts)
    except zipfile.BadZipFile:
        return []

    found = PLACEHOLDER_RE.findall(raw_xml)
    cleaned = sorted({item.strip() for item in found if item.strip()})
    return cleaned


def list_templates(active_only: bool = False):
    where = "WHERE t.active = 1" if active_only else ""
    records = rows(
        f"""
        SELECT t.*, rt.name AS report_type_name, rt.code AS report_type_code
        FROM report_templates t
        JOIN report_types rt ON rt.id = t.report_type_id
        {where}
        ORDER BY t.created_at DESC
        """
    )
    for r in records:
        r["required_fields"] = load_json(r.get("required_fields_json"), [])
        r["optional_fields"] = load_json(r.get("optional_fields_json"), [])
    return records


def create_template(payload: dict):
    return execute(
        """
        INSERT INTO report_templates (
            report_type_id, name, file_path, version, required_fields_json,
            optional_fields_json, accepts_photos, accepts_results_table, active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            payload.get("report_type_id"),
            payload.get("name"),
            payload.get("file_path"),
            payload.get("version", 1),
            dump_json(payload.get("required_fields", [])),
            dump_json(payload.get("optional_fields", [])),
            int(payload.get("accepts_photos", True)),
            int(payload.get("accepts_results_table", True)),
        ),
    )
