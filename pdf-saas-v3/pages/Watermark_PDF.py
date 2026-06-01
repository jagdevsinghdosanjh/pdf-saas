import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_watermark import add_text_watermark


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("💧 Watermark PDF")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    text = st.text_input("Watermark text", value="CONFIDENTIAL")
    opacity = st.slider("Opacity", min_value=0.1, max_value=0.9, value=0.2, step=0.05)

    if uploaded and text:
        pdf_bytes = uploaded.read()
        size_mb = len(pdf_bytes) / (1024 * 1024)
        st.info(f"Uploaded file size: {size_mb:.2f} MB")
        st.caption(f"Plan: {plan.name} (max {plan.max_file_size_mb} MB)")

        try:
            enforce_limits(plan, action="compress", file_size_mb=size_mb)
        except ValueError as e:
            st.error(str(e))
            st.warning("Upgrade your plan to process larger files.")
            st.page_link("pages/20_Upgrade.py", label="Go to Upgrade Page")
            return

        if st.button("Apply Watermark"):
            with st.spinner("Applying watermark..."):
                out_bytes = add_text_watermark(pdf_bytes, text=text, opacity=opacity)
                log_usage(
                    user,
                    "watermark_pdf",
                    {"input_mb": size_mb, "text": text},
                )
            st.success("Watermark applied.")
            st.download_button(
                "Download watermarked PDF",
                out_bytes,
                "watermarked.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()
