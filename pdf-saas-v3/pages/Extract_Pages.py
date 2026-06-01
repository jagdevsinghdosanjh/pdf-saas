import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_extract_pages import extract_pages


def parse_page_list(s: str):
    pages = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            pages.extend(range(int(a), int(b) + 1))
        else:
            pages.append(int(part))
    return sorted(set(pages))


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("📑 Extract Pages")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    page_spec = st.text_input("Pages (e.g. 1,3-5,10)")

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

        if st.button("Extract"):
            with st.spinner("Extracting pages..."):
                out_bytes = extract_pages(pdf_bytes, pages)
                log_usage(
                    user,
                    "extract_pages",
                    {"pages": pages, "input_mb": size_mb},
                )
            st.success("Extraction complete.")
            st.download_button(
                "Download extracted PDF",
                out_bytes,
                "extracted.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()
