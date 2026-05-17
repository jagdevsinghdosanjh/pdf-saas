from io import BytesIO
import fitz  # PyMuPDF
from typing import Dict


def get_metadata(pdf_bytes: bytes) -> Dict[str, str]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    meta = dict(doc.metadata or {})
    doc.close()
    return meta


def set_metadata(pdf_bytes: bytes, new_meta: Dict[str, str]) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    doc.set_metadata(new_meta)
    out_buf = BytesIO()
    doc.save(out_buf)
    doc.close()
    return out_buf.getvalue()
