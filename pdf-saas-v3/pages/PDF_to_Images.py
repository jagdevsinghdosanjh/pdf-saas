import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_to_images import pdf_to_images


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("🖼️ PDF → Images")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    dpi = st.slider("DPI", min_value=72, max_value=300, value=144, step=24)

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

        if st.button("Convert to Images"):
            with st.spinner("Rendering pages..."):
                images = pdf_to_images(pdf_bytes, dpi=dpi)
                log_usage(
                    user,
                    "pdf_to_images",
                    {"pages": len(images), "input_mb": size_mb, "dpi": dpi},
                )

            st.success(f"Generated {len(images)} images.")
            for i, img_bytes in enumerate(images, start=1):
                st.image(img_bytes, caption=f"Page {i}")
                st.download_button(
                    f"Download Page {i} PNG",
                    img_bytes,
                    file_name=f"page_{i}.png",
                    mime="image/png",
                    key=f"dl_{i}",
                )


if __name__ == "__main__":
    main()
