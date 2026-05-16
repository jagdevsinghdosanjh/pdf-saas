import streamlit as st
from core.auth import require_auth
from core.plans import enforce_limits
from services.pdf_compress import compress_pdf

user = require_auth()
st.title("Compress PDF")

uploaded = st.file_uploader("Upload PDF", type=["pdf"])
if uploaded:
    size_mb = uploaded.size / (1024 * 1024)
    try:
        enforce_limits(user["id"], "compress", file_size_mb=size_mb)
        if st.button("Compress"):
            out_bytes = compress_pdf(uploaded.read())
            st.download_button("Download compressed PDF", out_bytes, file_name="compressed.pdf")
    except ValueError as e:
        st.error(str(e))
