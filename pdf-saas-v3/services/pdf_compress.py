import shutil
import subprocess
import tempfile
import os
from io import BytesIO
import pikepdf

# Import presets from core/
from core.compression_presets import COMPRESSION_PRESETS

def compress_with_pikepdf(pdf_bytes: bytes, level: str = "medium") -> bytes:
    """
    Pure Python PDF compression using PikePDF only.
    Works on Streamlit Cloud (no Ghostscript required).
    """
    settings = {
        "high": pikepdf.ObjectStreamMode.generate,
        "medium": pikepdf.ObjectStreamMode.preserve,
        "aggressive": pikepdf.ObjectStreamMode.disabled,
    }
    mode = settings.get(level, pikepdf.ObjectStreamMode.preserve)

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


def compress_with_ghostscript(pdf_bytes: bytes, level: str, gs_path: str) -> bytes:
    """
    Dense PDF compression using Ghostscript + PikePDF.
    """
    if level not in COMPRESSION_PRESETS:
        level = "medium"

    cfg = COMPRESSION_PRESETS[level]
    dpi = cfg["dpi"]
    jpeg_quality = cfg["jpeg_quality"]
    pdf_settings = cfg["pdf_settings"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
        tmp_in.write(pdf_bytes)
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path.replace(".pdf", "_compressed.pdf")

    gs_cmd = [
        gs_path,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={pdf_settings}",
        "-dDownsampleColorImages=true",
        f"-dColorImageResolution={dpi}",
        f"-dJPEGQ={jpeg_quality}",
        "-dDownsampleGrayImages=true",
        f"-dGrayImageResolution={dpi}",
        "-dDownsampleMonoImages=true",
        f"-dMonoImageResolution={dpi}",
        "-dCompressFonts=true",
        "-dEmbedAllFonts=true",
        "-dSubsetFonts=true",
        "-dAutoRotatePages=/None",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={tmp_out_path}",
        tmp_in_path,
    ]

    subprocess.run(gs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output_pdf = BytesIO()
    with pikepdf.open(tmp_out_path) as pdf:
        pdf.save(
            output_pdf,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            linearize=True,
        )

    for f in [tmp_in_path, tmp_out_path]:
        try:
            os.remove(f)
        except Exception:
            pass

    return output_pdf.getvalue()


def compress_pdf(pdf_bytes: bytes, level: str = "medium") -> bytes:
    """
    Try Ghostscript + PikePDF if available, otherwise fallback to PikePDF-only.
    """
    gs_path = shutil.which("gswin64c") or shutil.which("gs")

    if gs_path:
        try:
            return compress_with_ghostscript(pdf_bytes, level, gs_path)
        except Exception:
            return compress_with_pikepdf(pdf_bytes, level)
    else:
        return compress_with_pikepdf(pdf_bytes, level)


# import subprocess
# from io import BytesIO
# import pikepdf
# import tempfile
# import os

# # Import presets from core/
# from core.compression_presets import COMPRESSION_PRESETS

# def compress_pdf(pdf_bytes: bytes, level: str = "medium") -> bytes:
#     """
#     Dense PDF compression using Ghostscript + PikePDF.
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
#         "gswin64c",  # Windows Ghostscript binary
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

#     # Step 3: Final optimization with PikePDF
#     output_pdf = BytesIO()
#     with pikepdf.open(tmp_out_path) as pdf:
#         pdf.save(
#             output_pdf,
#             compress_streams=True,
#             object_stream_mode=pikepdf.ObjectStreamMode.generate,  # always safe
#             linearize=True,
#         )

#     # Cleanup temp files safely
#     for f in [tmp_in_path, tmp_out_path]:
#         try:
#             os.remove(f)
#         except Exception:
#             pass

#     return output_pdf.getvalue()


# # try:
# #     import pikepdf  # type: ignore[import]
# # except ImportError as exc:
# #     raise ImportError(
# #         "Missing dependency 'pikepdf'. Install it with 'pip install pikepdf'."
# #     ) from exc

# # from io import BytesIO

# # def compress_pdf(pdf_bytes: bytes, level: str = "medium") -> bytes:
# #     """
# #     Pure Python PDF compression using pikepdf only.
# #     Works on Streamlit Cloud (no Ghostscript required).
# #     """

# #     # Valid compression levels mapped to ObjectStreamMode
# #     settings = {
# #         "high": pikepdf.ObjectStreamMode.generate,   # create new object streams
# #         "medium": pikepdf.ObjectStreamMode.preserve, # keep existing streams
# #         "aggressive": pikepdf.ObjectStreamMode.disabled, # disable object streams
# #     }

# #     # Default to 'preserve' if level not found
# #     mode = settings.get(level, pikepdf.ObjectStreamMode.preserve)

# #     input_pdf = BytesIO(pdf_bytes)
# #     output_pdf = BytesIO()

# #     with pikepdf.open(input_pdf) as pdf:
# #         pdf.save(
# #             output_pdf,
# #             compress_streams=True,   # actually compresses streams
# #             object_stream_mode=mode, # controls object stream handling
# #             linearize=True,          # web-optimized PDF
# #         )

# #     return output_pdf.getvalue()

# # # import pikepdf
# # # from io import BytesIO

# # # def compress_pdf(pdf_bytes: bytes, level: str = "medium") -> bytes:
# # #     """
# # #     Pure Python PDF compression using pikepdf only.
# # #     Works on Streamlit Cloud (no Ghostscript required).
# # #     """

# # #     # Compression levels
# # #     settings = {
# # #         "high": pikepdf.ObjectStreamMode.generate,
# # #         "medium": pikepdf.ObjectStreamMode.compress,
# # #         "aggressive": pikepdf.ObjectStreamMode.disable,
# # #     }

# # #     mode = settings.get(level, pikepdf.ObjectStreamMode.compress)

# # #     input_pdf = BytesIO(pdf_bytes)
# # #     output_pdf = BytesIO()

# # #     with pikepdf.open(input_pdf) as pdf:
# # #         pdf.save(
# # #             output_pdf,
# # #             compress_streams=True,
# # #             object_stream_mode=mode,
# # #             linearize=True,
# # #         )

# # #     return output_pdf.getvalue()

# # # # import subprocess
# # # # from io import BytesIO
# # # # import pikepdf
# # # # import tempfile
# # # # import os

# # # # # Import presets from core/
# # # # from core.compression_presets import COMPRESSION_PRESETS


# # # # def compress_pdf(pdf_bytes: bytes, level: str = "medium") -> bytes:
# # # #     """
# # # #     Dense PDF compression using Ghostscript + pikepdf.
# # # #     Supports presets: high, medium, aggressive, extreme.
# # # #     """

# # # #     # Validate preset
# # # #     if level not in COMPRESSION_PRESETS:
# # # #         level = "medium"

# # # #     cfg = COMPRESSION_PRESETS[level]
# # # #     dpi = cfg["dpi"]
# # # #     jpeg_quality = cfg["jpeg_quality"]
# # # #     pdf_settings = cfg["pdf_settings"]

# # # #     # Step 1: Write input PDF to temp file
# # # #     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
# # # #         tmp_in.write(pdf_bytes)
# # # #         tmp_in_path = tmp_in.name

# # # #     tmp_out_path = tmp_in_path.replace(".pdf", "_compressed.pdf")

# # # #     # Step 2: Ghostscript compression
# # # #     gs_cmd = [
# # # #         "gswin64c",
# # # #         "-sDEVICE=pdfwrite",
# # # #         "-dCompatibilityLevel=1.4",
# # # #         f"-dPDFSETTINGS={pdf_settings}",
# # # #         "-dDownsampleColorImages=true",
# # # #         f"-dColorImageResolution={dpi}",
# # # #         f"-dJPEGQ={jpeg_quality}",
# # # #         "-dDownsampleGrayImages=true",
# # # #         f"-dGrayImageResolution={dpi}",
# # # #         "-dDownsampleMonoImages=true",
# # # #         f"-dMonoImageResolution={dpi}",
# # # #         "-dCompressFonts=true",
# # # #         "-dEmbedAllFonts=true",
# # # #         "-dSubsetFonts=true",
# # # #         "-dAutoRotatePages=/None",
# # # #         "-dNOPAUSE",
# # # #         "-dQUIET",
# # # #         "-dBATCH",
# # # #         f"-sOutputFile={tmp_out_path}",
# # # #         tmp_in_path,
# # # #     ]

# # # #     subprocess.run(gs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# # # #     # Step 3: Final optimization with pikepdf
# # # #     output_pdf = BytesIO()
# # # #     with pikepdf.open(tmp_out_path) as pdf:
# # # #         pdf.save(
# # # #             output_pdf,
# # # #             compress_streams=True,
# # # #             object_stream_mode=pikepdf.ObjectStreamMode.generate,
# # # #             linearize=True,
# # # #         )

# # # #     # Cleanup temp files safely
# # # #     for f in [tmp_in_path, tmp_out_path]:
# # # #         try:
# # # #             os.remove(f)
# # # #         except Exception:
# # # #             pass

# # # #     return output_pdf.getvalue()
