import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan
from core.usage import log_usage


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.title("📄 Word → PDF (Coming Soon)")
    st.info("This feature is planned for a future engine (docx → PDF).")

    log_usage(user, "view_word_to_pdf_stub", {"plan": plan.slug})


if __name__ == "__main__":
    main()
