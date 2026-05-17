from io import BytesIO
from typing import List
import fitz  # PyMuPDF
from PIL import Image


def pdf_to_images(pdf_bytes: bytes, dpi: int = 144) -> List[bytes]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images: List[bytes] = []

    for page in doc:
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buf = BytesIO()
        img.save(buf, format="PNG")
        images.append(buf.getvalue())

    doc.close()
    return images
