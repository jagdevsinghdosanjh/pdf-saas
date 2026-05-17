from io import BytesIO
import pikepdf
from typing import List


def extract_pages(pdf_bytes: bytes, page_numbers: List[int]) -> bytes:
    src = pikepdf.Pdf.open(BytesIO(pdf_bytes))
    dst = pikepdf.Pdf.new()

    for p in page_numbers:
        idx = p - 1
        if 0 <= idx < len(src.pages):
            dst.pages.append(src.pages[idx])

    out_buf = BytesIO()
    dst.save(out_buf)
    return out_buf.getvalue()
