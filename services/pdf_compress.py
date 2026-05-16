import io
import pikepdf

def compress_pdf(file_bytes: bytes) -> bytes:
    input_pdf = io.BytesIO(file_bytes)
    output_pdf = io.BytesIO()
    with pikepdf.Pdf.open(input_pdf) as pdf:
        pdf.save(output_pdf, optimize_version=True)
    return output_pdf.getvalue()
