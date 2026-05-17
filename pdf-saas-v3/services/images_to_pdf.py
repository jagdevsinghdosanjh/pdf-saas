from io import BytesIO
from typing import List
from PIL import Image


def images_to_pdf(image_files: List[bytes]) -> bytes:
    pil_images = []
    for img_bytes in image_files:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        pil_images.append(img)

    if not pil_images:
        raise ValueError("No images provided.")

    buf = BytesIO()
    first, *rest = pil_images
    first.save(buf, format="PDF", save_all=True, append_images=rest)
    return buf.getvalue()
