import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan, enforce_limits
from core.usage import log_usage
from services.pdf_protect import unlock_pdf


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("🔓 Unlock PDF (Remove Password)")

    uploaded = st.file_uploader("Upload protected PDF", type=["pdf"])
    password = st.text_input("Current password", type="password")

    if uploaded and password:
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

        if st.button("Unlock"):
            try:
                with st.spinner("Decrypting..."):
                    out_bytes = unlock_pdf(pdf_bytes, password)
                    log_usage(
                        user,
                        "unlock_pdf",
                        {"input_mb": size_mb},
                    )
                st.success("PDF unlocked.")
                st.download_button(
                    "Download unlocked PDF",
                    out_bytes,
                    "unlocked.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error("Failed to unlock PDF. Check password.")
                st.caption(str(e))


if __name__ == "__main__":
    main()
