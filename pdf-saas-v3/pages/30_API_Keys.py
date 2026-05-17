import streamlit as st
from core.auth import require_auth
from core.api_keys import list_api_keys, create_api_key


def main():
    user = require_auth()
    st.title("🔑 API Keys")

    st.markdown("Use API keys to access PDF SaaS via REST API (future).")

    keys = list_api_keys(user)
    if keys:
        st.subheader("Existing Keys")
        for k in keys:
            st.code(f"{k['label']}: {k['key']}")
    else:
        st.info("No API keys yet.")

    st.subheader("Create New Key")
    label = st.text_input("Label")
    if st.button("Create API Key") and label:
        key = create_api_key(user, label)
        st.success("API key created:")
        st.code(key)


if __name__ == "__main__":
    main()
