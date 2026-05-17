from io import BytesIO
import pikepdf
from typing import List


def rotate_pages(pdf_bytes: bytes, page_numbers: List[int], angle: int) -> bytes:
    pdf = pikepdf.Pdf.open(BytesIO(pdf_bytes))

    for p in page_numbers:
        idx = p - 1
        if 0 <= idx < len(pdf.pages):
            page = pdf.pages[idx]
            current = page.get("/Rotate", 0)
            page["/Rotate"] = (current + angle) % 360

    out_buf = BytesIO()
    pdf.save(out_buf)
    return out_buf.getvalue()
