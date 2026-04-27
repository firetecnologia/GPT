"""Funções utilitárias para processamento de imagens."""

from pathlib import Path
from PIL import Image, ImageOps


def process_image(input_path: str, output_path: str, max_width: int = 1600, quality: int = 85) -> str:
    img = Image.open(input_path)
    img = ImageOps.exif_transpose(img)

    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height))

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "JPEG", quality=quality, optimize=True)
    return output_path
