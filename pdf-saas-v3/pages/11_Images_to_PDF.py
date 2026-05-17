import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.images_to_pdf import images_to_pdf


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("🖼️ Images → PDF")

    uploaded_files = st.file_uploader(
        "Upload images (PNG/JPEG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True
    )

    if uploaded_files:
        img_bytes_list = [f.read() for f in uploaded_files]
        total_mb = sum(len(b) for b in img_bytes_list) / (1024 * 1024)
        st.info(f"Total images: {len(img_bytes_list)}, size: {total_mb:.2f} MB")
        st.caption(f"Plan: {plan.name} (max {plan.max_file_size_mb} MB per file)")

        try:
            enforce_limits(plan, action="compress", file_size_mb=total_mb)
        except ValueError as e:
            st.error(str(e))
            st.warning("Upgrade your plan to process larger files.")
            st.page_link("pages/20_Upgrade.py", label="Go to Upgrade Page")
            return

        if st.button("Convert to PDF"):
            with st.spinner("Converting images to PDF..."):
                out_bytes = images_to_pdf(img_bytes_list)
                log_usage(
                    user,
                    "images_to_pdf",
                    {"image_count": len(img_bytes_list), "total_mb": total_mb},
                )
            st.success("Conversion complete.")
            st.download_button(
                "Download PDF",
                out_bytes,
                "images.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()
