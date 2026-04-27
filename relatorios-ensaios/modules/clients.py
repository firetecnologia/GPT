"""CRUD de clientes."""

from modules.database import execute, rows


def list_clients():
    return rows("SELECT * FROM clients ORDER BY created_at DESC")


def create_client(payload: dict):
    return execute(
        """
        INSERT INTO clients (name, document, contact_name, phone, email, address, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.get("name"),
            payload.get("document"),
            payload.get("contact_name"),
            payload.get("phone"),
            payload.get("email"),
            payload.get("address"),
            payload.get("notes"),
        ),
    )
