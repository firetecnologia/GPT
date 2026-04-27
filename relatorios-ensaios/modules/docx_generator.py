"""Geração de relatórios DOCX via docxtpl."""

from __future__ import annotations

from pathlib import Path

from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage


def generate_report_docx(template_path: str, output_path: str, context: dict, photos: list[dict]) -> str:
    doc = DocxTemplate(template_path)

    prepared_photos = []
    for photo in photos:
        image_path = photo.get("image_path")
        inline_img = InlineImage(doc, image_path, width=Mm(120)) if image_path else ""
        prepared_photos.append(
            {
                "imagem": inline_img,
                "legenda": photo.get("caption", ""),
                "categoria": photo.get("category", ""),
                "observacao": photo.get("notes", ""),
            }
        )

    context["fotos"] = prepared_photos

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.render(context)
    doc.save(output_path)
    return output_path
