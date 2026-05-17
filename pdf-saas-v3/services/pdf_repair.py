from io import BytesIO
import pikepdf


def repair_pdf(pdf_bytes: bytes) -> bytes:
    src = pikepdf.Pdf.open(BytesIO(pdf_bytes))
    out_buf = BytesIO()
    src.save(out_buf, linearize=True)
    return out_buf.getvalue()
