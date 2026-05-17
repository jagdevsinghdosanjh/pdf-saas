from io import BytesIO
import pikepdf
from typing import List


def merge_pdfs(files: List[bytes]) -> bytes:
    output_pdf = pikepdf.Pdf.new()

    for file_bytes in files:
        with pikepdf.open(BytesIO(file_bytes)) as src:
            output_pdf.pages.extend(src.pages)

    out_buf = BytesIO()
    output_pdf.save(out_buf)
    return out_buf.getvalue()
