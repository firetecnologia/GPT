"""CRUD de responsáveis técnicos."""

from modules.database import execute, rows


def list_technicians():
    return rows("SELECT * FROM technicians ORDER BY created_at DESC")


def create_technician(payload: dict):
    return execute(
        """
        INSERT INTO technicians (name, profession, registration_number, role, email, phone, signature_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.get("name"),
            payload.get("profession"),
            payload.get("registration_number"),
            payload.get("role"),
            payload.get("email"),
            payload.get("phone"),
            payload.get("signature_path"),
        ),
    )
