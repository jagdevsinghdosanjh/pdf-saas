from io import BytesIO
import fitz  # PyMuPDF


def add_text_watermark(pdf_bytes: bytes, text: str, opacity: float = 0.2) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page in doc:
        rect = page.rect
        fontsize = rect.width / 10
        page.insert_text(
            rect.center,
            text,
            fontsize=fontsize,
            rotate=45,
            color=(0.6, 0.6, 0.6),
            fill_opacity=opacity,
            render_mode=2,
        )

    out_buf = BytesIO()
    doc.save(out_buf)
    doc.close()
    return out_buf.getvalue()
