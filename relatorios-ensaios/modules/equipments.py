"""CRUD de equipamentos."""

from modules.database import execute, rows


def list_equipments():
    return rows("SELECT * FROM equipments ORDER BY created_at DESC")


def create_equipment(payload: dict):
    return execute(
        """
        INSERT INTO equipments (
            name, brand, model, serial_number, calibration_certificate,
            calibration_date, calibration_valid_until, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.get("name"),
            payload.get("brand"),
            payload.get("model"),
            payload.get("serial_number"),
            payload.get("calibration_certificate"),
            payload.get("calibration_date"),
            payload.get("calibration_valid_until"),
            payload.get("notes"),
        ),
    )
