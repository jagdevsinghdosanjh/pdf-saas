from io import BytesIO
import pikepdf


def protect_pdf(pdf_bytes: bytes, password: str) -> bytes:
    src = pikepdf.Pdf.open(BytesIO(pdf_bytes))
    out_buf = BytesIO()
    src.save(out_buf, encryption=pikepdf.Encryption(user=password, owner=password))
    return out_buf.getvalue()


def unlock_pdf(pdf_bytes: bytes, password: str) -> bytes:
    src = pikepdf.Pdf.open(BytesIO(pdf_bytes), password=password)
    out_buf = BytesIO()
    src.save(out_buf)
    return out_buf.getvalue()
