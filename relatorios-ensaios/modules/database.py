"""Camada de banco de dados (SQLite) para o MVP de relatórios."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "database.db"


def get_conn() -> sqlite3.Connection:
    """Retorna conexão SQLite com row_factory como dict-like."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Cria tabelas mínimas necessárias para o MVP."""
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            document TEXT,
            contact_name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS works (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            state TEXT,
            building_type TEXT,
            contact_person TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            profession TEXT,
            registration_number TEXT,
            role TEXT,
            email TEXT,
            phone TEXT,
            signature_path TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS equipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            model TEXT,
            serial_number TEXT,
            calibration_certificate TEXT,
            calibration_date TEXT,
            calibration_valid_until TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS report_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            description TEXT,
            default_objective TEXT,
            default_methodology TEXT,
            default_conclusion_ok TEXT,
            default_conclusion_not_ok TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS report_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            required_fields_json TEXT NOT NULL DEFAULT '[]',
            optional_fields_json TEXT NOT NULL DEFAULT '[]',
            accepts_photos INTEGER NOT NULL DEFAULT 1,
            accepts_results_table INTEGER NOT NULL DEFAULT 1,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(report_type_id) REFERENCES report_types(id)
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_number TEXT NOT NULL UNIQUE,
            report_type_id INTEGER NOT NULL,
            template_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            work_id INTEGER NOT NULL,
            technician_id INTEGER NOT NULL,
            date_test TEXT NOT NULL,
            date_issue TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Rascunho',
            general_data_json TEXT NOT NULL DEFAULT '{}',
            conclusion TEXT,
            observations TEXT,
            generated_docx_path TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(report_type_id) REFERENCES report_types(id),
            FOREIGN KEY(template_id) REFERENCES report_templates(id),
            FOREIGN KEY(client_id) REFERENCES clients(id),
            FOREIGN KEY(work_id) REFERENCES works(id),
            FOREIGN KEY(technician_id) REFERENCES technicians(id)
        );

        CREATE TABLE IF NOT EXISTS report_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            item_number TEXT,
            location TEXT,
            measured_value TEXT,
            reference_value TEXT,
            unit TEXT,
            acceptance_criteria TEXT,
            status TEXT,
            notes TEXT,
            FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS report_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            caption TEXT,
            category TEXT,
            display_order INTEGER,
            notes TEXT,
            FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS technical_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            standard_reference TEXT,
            min_value REAL,
            max_value REAL,
            unit TEXT,
            comparison_rule TEXT,
            text_when_ok TEXT,
            text_when_not_ok TEXT,
            notes TEXT,
            FOREIGN KEY(report_type_id) REFERENCES report_types(id)
        );

        CREATE TABLE IF NOT EXISTS company_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            company_name TEXT,
            cnpj TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            logo_path TEXT,
            footer_text TEXT,
            technical_disclaimer TEXT
        );
        """
    )

    conn.commit()
    conn.close()


def rows(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    conn = get_conn()
    data = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    return data


def execute(query: str, params: tuple[Any, ...] = ()) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def execute_many(query: str, params_list: list[tuple[Any, ...]]) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.executemany(query, params_list)
    conn.commit()
    conn.close()


def upsert_company_settings(data: dict[str, Any]) -> None:
    payload = (
        data.get("company_name"),
        data.get("cnpj"),
        data.get("address"),
        data.get("phone"),
        data.get("email"),
        data.get("website"),
        data.get("logo_path"),
        data.get("footer_text"),
        data.get("technical_disclaimer"),
    )
    execute(
        """
        INSERT INTO company_settings (id, company_name, cnpj, address, phone, email, website, logo_path, footer_text, technical_disclaimer)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            company_name=excluded.company_name,
            cnpj=excluded.cnpj,
            address=excluded.address,
            phone=excluded.phone,
            email=excluded.email,
            website=excluded.website,
            logo_path=excluded.logo_path,
            footer_text=excluded.footer_text,
            technical_disclaimer=excluded.technical_disclaimer
        """,
        payload,
    )


def get_company_settings() -> dict[str, Any]:
    items = rows("SELECT * FROM company_settings WHERE id = 1")
    return items[0] if items else {}


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def load_json(data: str | None, default: Any) -> Any:
    if not data:
        return default
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return default
