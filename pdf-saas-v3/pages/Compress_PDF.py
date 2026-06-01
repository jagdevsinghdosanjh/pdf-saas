import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_compress import compress_pdf


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("🗜️ Compress PDF")

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
            st.page_link("pages/Upgrade.py", label="Go to Upgrade Page")
            return

        if st.button("Compress"):
            with st.spinner("Compressing ..."):
                out_bytes, method, in_mb, out_mb = compress_pdf(pdf_bytes, level="medium")

                log_usage(
                    user,
                    "compress_pdf",
                    {"method": method, "input_mb": in_mb, "output_mb": out_mb},
                )

                st.success(f"Compression complete using {method}.")
                st.caption(f"Size reduced from {in_mb:.2f} MB → {out_mb:.2f} MB")

                st.download_button(
                    "Download compressed PDF",
                    out_bytes,
                    "compressed.pdf",
                    mime="application/pdf",
                )


if __name__ == "__main__":
    main()
