import pikepdf
from io import BytesIO

def compress_pdf(pdf_bytes):
    try:
        input_pdf = BytesIO(pdf_bytes)
        output_pdf = BytesIO()

        with pikepdf.open(input_pdf) as pdf:
            pdf.save(
                output_pdf,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                linearize=True
            )

        return output_pdf.getvalue()

    except Exception as e:
        print("Compression error:", e)
        return None

# import io
# import pikepdf


# def compress_pdf(file_bytes: bytes) -> bytes:
#     input_pdf = io.BytesIO(file_bytes)
#     output_pdf = io.BytesIO()
#     with pikepdf.Pdf.open(input_pdf) as pdf:
#         pdf.save(output_pdf, optimize_version=True)
#     return output_pdf.getvalue()
