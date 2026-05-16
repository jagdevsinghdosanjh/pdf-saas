from io import BytesIO
import pikepdf

def compress_pdf(pdf_bytes: bytes) -> bytes:
    input_pdf = BytesIO(pdf_bytes)
    output_pdf = BytesIO()

    with pikepdf.open(input_pdf) as pdf:
        pdf.save(
            output_pdf,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            linearize=True,
        )

    return output_pdf.getvalue()
