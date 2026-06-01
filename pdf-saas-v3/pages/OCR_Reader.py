import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.ocr import extract_text_from_pdf


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("👁️ OCR / Text Reader")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded:
        pdf_bytes = uploaded.read()
        size_mb = len(pdf_bytes) / (1024 * 1024)
        st.info(f"Uploaded file size: {size_mb:.2f} MB")
        st.caption(f"Plan: {plan.name} (max {plan.max_file_size_mb} MB)")

        try:
            enforce_limits(plan, action="ocr", file_size_mb=size_mb)
        except ValueError as e:
            st.error(str(e))
            st.warning("Upgrade your plan to use OCR on larger files.")
            st.page_link("pages/20_Upgrade.py", label="Go to Upgrade Page")
            return

        if st.button("Extract Text"):
            with st.spinner("Extracting text..."):
                text = extract_text_from_pdf(pdf_bytes)
                log_usage(
                    user,
                    "ocr_extract_text",
                    {"input_mb": size_mb, "chars": len(text)},
                )
            st.success("Text extracted.")
            st.text_area("Extracted Text", value=text, height=400)


if __name__ == "__main__":
    main()
