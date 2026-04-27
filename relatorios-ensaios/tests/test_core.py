import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path

from modules.database import execute, init_db, rows
from modules.reports import next_report_number, suggest_conclusion
from modules.templates import extract_placeholders_from_docx


class CoreLogicTest(unittest.TestCase):
    def setUp(self):
        init_db()
        if not rows("SELECT id FROM clients WHERE id = 1"):
            execute("INSERT INTO clients (id, name) VALUES (1, 'Cliente Teste')")
        if not rows("SELECT id FROM works WHERE id = 1"):
            execute("INSERT INTO works (id, client_id, name) VALUES (1, 1, 'Obra Teste')")
        if not rows("SELECT id FROM technicians WHERE id = 1"):
            execute("INSERT INTO technicians (id, name) VALUES (1, 'Tec Teste')")
        if not rows("SELECT id FROM report_types WHERE id = 1"):
            execute("INSERT INTO report_types (id, name, code) VALUES (1, 'SPDA', 'SPDA')")
        if not rows("SELECT id FROM report_templates WHERE id = 1"):
            execute(
                """
                INSERT INTO report_templates (id, report_type_id, name, file_path)
                VALUES (1, 1, 'Template', 'data/templates/template.docx')
                """
            )

    def test_suggest_conclusion(self):
        ok = suggest_conclusion([{"status": "Atende"}, {"status": "Atende"}])
        not_ok = suggest_conclusion([{"status": "Não atende"}])
        self.assertIn("atendem", ok.lower())
        self.assertIn("não atendem", not_ok.lower())

    def test_next_report_number(self):
        execute("DELETE FROM reports WHERE report_number = ?", ("REL-2026-SPDA-001",))
        execute(
            """
            INSERT INTO reports (
                report_number, report_type_id, template_id, client_id, work_id, technician_id,
                date_test, date_issue, status, general_data_json
            ) VALUES (?, 1, 1, 1, 1, 1, '2026-01-01', '2026-01-01', 'Emitido', '{}')
            """,
            ("REL-2026-SPDA-001",),
        )
        nxt = next_report_number("spda", date(2026, 4, 27))
        self.assertEqual(nxt, "REL-2026-SPDA-002")

    def test_extract_placeholders_from_docx(self):
        with tempfile.TemporaryDirectory() as tmp:
            docx_path = Path(tmp) / "sample.docx"
            with zipfile.ZipFile(docx_path, "w") as archive:
                archive.writestr("word/document.xml", "<w:t>{{ cliente_nome }}</w:t><w:t>{{ data_ensaio }}</w:t>")
            fields = extract_placeholders_from_docx(str(docx_path))
            self.assertEqual(fields, ["cliente_nome", "data_ensaio"])


if __name__ == "__main__":
    unittest.main()
