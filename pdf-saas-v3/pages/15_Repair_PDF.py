import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_repair import repair_pdf


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("🛠️ Repair PDF")

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

        if st.button("Repair"):
            with st.spinner("Repairing PDF..."):
                out_bytes = repair_pdf(pdf_bytes)
                log_usage(
                    user,
                    "repair_pdf",
                    {"input_mb": size_mb},
                )
            st.success("Repair attempt complete.")
            st.download_button(
                "Download repaired PDF",
                out_bytes,
                "repaired.pdf",
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()
