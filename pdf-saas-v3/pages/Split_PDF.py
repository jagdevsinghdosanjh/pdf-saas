import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_split import split_pdf


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("✂️ Split PDF")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    pages_per_chunk = st.number_input("Pages per split file", min_value=1, max_value=100, value=10)

    if uploaded:
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

        if st.button("Split PDF"):
            with st.spinner("Splitting..."):
                parts = split_pdf(pdf_bytes, pages_per_chunk=pages_per_chunk)
                log_usage(
                    user,
                    "split_pdf",
                    {"parts": len(parts), "input_mb": size_mb, "pages_per_chunk": pages_per_chunk},
                )
            st.success(f"Split into {len(parts)} files.")
            for i, part in enumerate(parts, start=1):
                st.download_button(
                    f"Download Part {i}",
                    part,
                    file_name=f"split_part_{i}.pdf",
                    mime="application/pdf",
                    key=f"split_{i}",
                )


if __name__ == "__main__":
    main()
