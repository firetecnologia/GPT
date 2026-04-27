"""CRUD de obras."""

from modules.database import execute, rows


def list_works():
    return rows(
        """
        SELECT w.*, c.name AS client_name
        FROM works w
        JOIN clients c ON c.id = w.client_id
        ORDER BY w.created_at DESC
        """
    )


def create_work(payload: dict):
    return execute(
        """
        INSERT INTO works (client_id, name, address, city, state, building_type, contact_person, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.get("client_id"),
            payload.get("name"),
            payload.get("address"),
            payload.get("city"),
            payload.get("state"),
            payload.get("building_type"),
            payload.get("contact_person"),
            payload.get("notes"),
        ),
    )
