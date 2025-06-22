from PIL import Image as PILImage
import os

def convert_image(image_path: str, target_format: str) -> str:
    """Конвертирует изображение в указанный формат (jpg или png)."""
    if target_format.lower() not in ["jpg", "png"]:
        raise ValueError("Поддерживаются только форматы JPG и PNG")

    output_path = image_path.rsplit(".", 1)[0] + f".{target_format.lower()}"
    with PILImage.open(image_path) as img:
        if target_format.lower() == "jpg":
            # Конвертация в RGB, если изображение в RGBA (PNG)
            if img.mode == "RGBA":
                img = img.convert("RGB")
        img.save(output_path, target_format.upper())
    return output_path

def get_image_metadata(image_path: str):
    """Получает метаданные изображения (размер, разрешение)."""
    with PILImage.open(image_path) as img:
        width, height = img.size
    size = os.path.getsize(image_path)
    return size, width, height