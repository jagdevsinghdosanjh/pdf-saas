import io
from pdf2image import convert_from_bytes
import pytesseract

def pdf_to_ocr_text(file_bytes: bytes, dpi: int = 200) -> str:
    images = convert_from_bytes(file_bytes, dpi=dpi)
    texts = []
    for img in images:
        text = pytesseract.image_to_string(img)
        texts.append(text)
    return "\n\n".join(texts)
