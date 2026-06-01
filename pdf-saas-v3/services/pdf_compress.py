import shutil
import subprocess
import tempfile
import os
from io import BytesIO
import pikepdf

from core.compression_presets import COMPRESSION_PRESETS


def compress_with_pikepdf(pdf_bytes: bytes, level: str = "medium") -> tuple[bytes, str]:
    """Pure Python PDF compression using PikePDF only."""
    settings = {
        "high": pikepdf.ObjectStreamMode.generate,
        "medium": pikepdf.ObjectStreamMode.preserve,
        "aggressive": pikepdf.ObjectStreamMode.disable,
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

    return output_pdf.getvalue(), "PikePDF-only"


def compress_with_ghostscript(pdf_bytes: bytes, level: str, gs_path: str) -> tuple[bytes, str]:
    """Dense PDF compression using Ghostscript + PikePDF."""
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

    # Clean up temp files safely
    for f in [tmp_in_path, tmp_out_path]:
        try:
            os.remove(f)
        except Exception:
            # Ignore errors if file already removed
            pass

    return output_pdf.getvalue(), "Ghostscript + PikePDF"


def compress_pdf(pdf_bytes: bytes, level: str = "medium") -> tuple[bytes, str, float, float]:
    """
    Try Ghostscript + PikePDF if available, otherwise fallback to PikePDF-only.
    Returns: (compressed_bytes, method_used, input_size_mb, output_size_mb)
    """
    input_size_mb = len(pdf_bytes) / (1024 * 1024)
    gs_path = shutil.which("gswin64c") or shutil.which("gs")

    if gs_path:
        try:
            out_bytes, method = compress_with_ghostscript(pdf_bytes, level, gs_path)
        except Exception:
            out_bytes, method = compress_with_pikepdf(pdf_bytes, level)
    else:
        out_bytes, method = compress_with_pikepdf(pdf_bytes, level)

    output_size_mb = len(out_bytes) / (1024 * 1024)
    return out_bytes, method, input_size_mb, output_size_mb
