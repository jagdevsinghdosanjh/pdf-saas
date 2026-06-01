import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_rotate import rotate_pages
from pages.5_Extract_Pages import parse_page_list


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("🔄 Rotate PDF")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    page_spec = st.text_input("Pages to rotate (e.g. 1,3-5)")
    angle = st.selectbox("Rotation angle", [90, 180, 270], index=0)

    if uploaded and page_spec:
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

        pages = parse_page_list(page_spec)

        if st.button("Rotate"):
            with st.spinner("Rotating pages..."):
                out_bytes = rotate_pages(pdf_bytes, pages, angle)
                log_usage(
                    user,
                    "rotate_pages",
                    {"pages": pages, "angle": angle, "input_mb": size_mb},
                )
            st.success("Rotation complete.")
            st.download_button(
                "Download rotated PDF",
                out_bytes,
                "rotated.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()
