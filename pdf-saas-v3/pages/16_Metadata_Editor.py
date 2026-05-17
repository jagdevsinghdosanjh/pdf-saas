import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_metadata import get_metadata, set_metadata


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("ℹ️ PDF Metadata Editor")

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
            st.warning("Upgrade your plan to process larger files.")
            st.page_link("pages/20_Upgrade.py", label="Go to Upgrade Page")
            return

        meta = get_metadata(pdf_bytes)
        st.subheader("Current Metadata")
        st.json(meta)

        st.subheader("Edit Metadata")
        title = st.text_input("Title", value=meta.get("title", ""))
        author = st.text_input("Author", value=meta.get("author", ""))
        subject = st.text_input("Subject", value=meta.get("subject", ""))
        keywords = st.text_input("Keywords", value=meta.get("keywords", ""))

        if st.button("Save Metadata"):
            new_meta = meta.copy()
            new_meta["title"] = title
            new_meta["author"] = author
            new_meta["subject"] = subject
            new_meta["keywords"] = keywords

            with st.spinner("Updating metadata..."):
                out_bytes = set_metadata(pdf_bytes, new_meta)
                log_usage(
                    user,
                    "edit_metadata",
                    {"input_mb": size_mb},
                )
            st.success("Metadata updated.")
            st.download_button(
                "Download updated PDF",
                out_bytes,
                "metadata_updated.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()
