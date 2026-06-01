import streamlit as st
from typing import List
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_merge import merge_pdfs


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("➕ Merge PDFs")

    uploaded_files = st.file_uploader(
        "Upload PDFs to merge (in order)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        file_count = len(uploaded_files)
        st.info(f"Files selected: {file_count}")
        st.caption(f"Plan: {plan.name} (max {plan.max_files_per_merge} files)")

        try:
            enforce_limits(plan, action="merge", file_count=file_count)
        except ValueError as e:
            st.error(str(e))
            st.warning("Upgrade your plan to merge more files.")
            st.page_link("pages/20_Upgrade.py", label="Go to Upgrade Page")
            return

        if st.button("Merge"):
            pdf_bytes_list: List[bytes] = [f.read() for f in uploaded_files]
            total_mb = sum(len(b) for b in pdf_bytes_list) / (1024 * 1024)
            with st.spinner("Merging PDFs..."):
                out_bytes = merge_pdfs(pdf_bytes_list)
                log_usage(
                    user,
                    "merge_pdfs",
                    {"file_count": file_count, "total_mb": total_mb},
                )
            st.success("Merge complete.")
            st.download_button(
                "Download merged PDF",
                out_bytes,
                "merged.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()
