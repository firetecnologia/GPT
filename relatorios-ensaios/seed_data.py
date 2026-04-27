"""Popula dados de exemplo (fake) para teste rápido do MVP."""

from datetime import date

from modules.database import init_db
from modules.clients import create_client
from modules.works import create_work
from modules.technicians import create_technician
from modules.equipments import create_equipment
from modules.reports import create_report_type


def run() -> None:
    init_db()

    client_id = create_client(
        {
            "name": "Construtora Exemplo LTDA",
            "document": "00.000.000/0001-00",
            "contact_name": "João da Silva",
            "phone": "(11) 99999-0000",
            "email": "contato@construtoraexemplo.com",
            "address": "Av. Exemplo, 100 - São Paulo/SP",
            "notes": "Cliente fake para testes",
        }
    )

    create_work(
        {
            "client_id": client_id,
            "name": "Edifício Alpha",
            "address": "Rua Teste, 200",
            "city": "São Paulo",
            "state": "SP",
            "building_type": "Residencial",
            "contact_person": "Maria Souza",
            "notes": "Obra de exemplo",
        }
    )

    create_technician(
        {
            "name": "Eng. Carlos Teste",
            "profession": "Engenheiro Civil",
            "registration_number": "CREA 123456",
            "role": "Responsável técnico",
            "email": "carlos@empresa.com",
            "phone": "(11) 98888-0000",
            "signature_path": "",
        }
    )

    create_equipment(
        {
            "name": "Terrômetro Digital",
            "brand": "Marca X",
            "model": "TX-100",
            "serial_number": "SN-12345",
            "calibration_certificate": "CERT-001",
            "calibration_date": str(date.today()),
            "calibration_valid_until": str(date.today().replace(year=date.today().year + 1)),
            "notes": "Equipamento fake",
        }
    )

    try:
        create_report_type(
            {
                "name": "SPDA / Aterramento",
                "code": "SPDA",
                "description": "Relatório técnico de aterramento",
                "default_objective": "Registrar medições do sistema de aterramento.",
                "default_methodology": "Medições em campo com equipamento calibrado.",
                "default_conclusion_ok": "Todos os pontos atenderam aos critérios definidos.",
                "default_conclusion_not_ok": "Há pontos não conformes que requerem adequação.",
            }
        )
    except Exception:
        pass


if __name__ == "__main__":
    run()
    print("Dados de exemplo inseridos com sucesso.")
