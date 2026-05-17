from io import BytesIO
import pikepdf
from typing import List


def split_pdf(pdf_bytes: bytes, pages_per_chunk: int = 10) -> List[bytes]:
    src = pikepdf.Pdf.open(BytesIO(pdf_bytes))
    outputs: List[bytes] = []

    for start in range(0, len(src.pages), pages_per_chunk):
        dst = pikepdf.Pdf.new()
        for p in range(start, min(start + pages_per_chunk, len(src.pages))):
            dst.pages.append(src.pages[p])
        buf = BytesIO()
        dst.save(buf)
        outputs.append(buf.getvalue())

    return outputs
