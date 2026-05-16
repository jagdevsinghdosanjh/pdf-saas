import io
from pypdf import PdfWriter, PdfReader

def merge_pdfs(files: list[bytes]) -> bytes:
    writer = PdfWriter()
    for fb in files:
        reader = PdfReader(io.BytesIO(fb))
        for page in reader.pages:
            writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()
