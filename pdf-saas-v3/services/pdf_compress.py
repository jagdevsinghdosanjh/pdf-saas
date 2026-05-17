import pikepdf
from io import BytesIO

def compress_pdf(pdf_bytes: bytes, level: str = "medium") -> bytes:
    """
    Pure Python PDF compression using pikepdf only.
    Works on Streamlit Cloud (no Ghostscript required).
    """

    # Compression levels
    settings = {
        "high": pikepdf.ObjectStreamMode.generate,
        "medium": pikepdf.ObjectStreamMode.compress,
        "aggressive": pikepdf.ObjectStreamMode.disable,
    }

    mode = settings.get(level, pikepdf.ObjectStreamMode.compress)

    input_pdf = BytesIO(pdf_bytes)
    output_pdf = BytesIO()

    with pikepdf.open(input_pdf) as pdf:
        pdf.save(
            output_pdf,
            compress_streams=True,
            object_stream_mode=mode,
            linearize=True,
        )

    return output_pdf.getvalue()

# import subprocess
# from io import BytesIO
# import pikepdf
# import tempfile
# import os

# # Import presets from core/
# from core.compression_presets import COMPRESSION_PRESETS


# def compress_pdf(pdf_bytes: bytes, level: str = "medium") -> bytes:
#     """
#     Dense PDF compression using Ghostscript + pikepdf.
#     Supports presets: high, medium, aggressive, extreme.
#     """

#     # Validate preset
#     if level not in COMPRESSION_PRESETS:
#         level = "medium"

#     cfg = COMPRESSION_PRESETS[level]
#     dpi = cfg["dpi"]
#     jpeg_quality = cfg["jpeg_quality"]
#     pdf_settings = cfg["pdf_settings"]

#     # Step 1: Write input PDF to temp file
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
#         tmp_in.write(pdf_bytes)
#         tmp_in_path = tmp_in.name

#     tmp_out_path = tmp_in_path.replace(".pdf", "_compressed.pdf")

#     # Step 2: Ghostscript compression
#     gs_cmd = [
#         "gswin64c",
#         "-sDEVICE=pdfwrite",
#         "-dCompatibilityLevel=1.4",
#         f"-dPDFSETTINGS={pdf_settings}",
#         "-dDownsampleColorImages=true",
#         f"-dColorImageResolution={dpi}",
#         f"-dJPEGQ={jpeg_quality}",
#         "-dDownsampleGrayImages=true",
#         f"-dGrayImageResolution={dpi}",
#         "-dDownsampleMonoImages=true",
#         f"-dMonoImageResolution={dpi}",
#         "-dCompressFonts=true",
#         "-dEmbedAllFonts=true",
#         "-dSubsetFonts=true",
#         "-dAutoRotatePages=/None",
#         "-dNOPAUSE",
#         "-dQUIET",
#         "-dBATCH",
#         f"-sOutputFile={tmp_out_path}",
#         tmp_in_path,
#     ]

#     subprocess.run(gs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     # Step 3: Final optimization with pikepdf
#     output_pdf = BytesIO()
#     with pikepdf.open(tmp_out_path) as pdf:
#         pdf.save(
#             output_pdf,
#             compress_streams=True,
#             object_stream_mode=pikepdf.ObjectStreamMode.generate,
#             linearize=True,
#         )

#     # Cleanup temp files safely
#     for f in [tmp_in_path, tmp_out_path]:
#         try:
#             os.remove(f)
#         except Exception:
#             pass

#     return output_pdf.getvalue()
