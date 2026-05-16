import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from services.pdf_compress import compress_pdf

st.title("Compress PDF")

user = require_auth()
plan = get_active_subscription_plan(user)

uploaded = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded:
    pdf_bytes = uploaded.read()
    size_mb = len(pdf_bytes) / (1024 * 1024)

    st.info(f"Uploaded file size: {size_mb:.2f} MB")
    st.caption(f"Plan: {plan.name} (max {plan.max_file_size_mb} MB)")

    try:
        enforce_limits(plan, action="compress", file_size_mb=size_mb)
    except ValueError as e:
        st.error(str(e))
        st.warning("Upgrade your plan to compress larger files.")
        st.page_link("pages/4_Upgrade.py", label="Go to Upgrade Page")
        st.stop()

    if st.button("Compress"):
        with st.spinner("Compressing..."):
            out_bytes = compress_pdf(pdf_bytes)

        st.success("Compression complete.")
        st.download_button(
            "Download compressed PDF",
            out_bytes,
            "compressed.pdf",
            mime="application/pdf",
        )
