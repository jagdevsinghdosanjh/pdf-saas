import streamlit as st
from core.auth import require_auth
from core.plans import enforce_limits
from services.pdf_compress import compress_pdf

st.title("Compress PDF")

user = require_auth()
uploaded = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded:
    size_mb = uploaded.size / (1024 * 1024)
    try:
        plan = enforce_limits(user.id, "compress", file_size_mb=size_mb)
        st.caption(f"Plan: {plan.name} (max {plan.max_file_size_mb} MB)")
        if st.button("Compress"):
            out_bytes = compress_pdf(uploaded.read())
            st.download_button("Download compressed PDF", out_bytes, "compressed.pdf")
    except ValueError as e:
        st.error(str(e))
