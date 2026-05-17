import streamlit as st
from core.auth import require_auth
from core.admin import require_admin, get_all_subscriptions, get_usage_stats


def main():
    user = require_auth()
    try:
        require_admin(user)
    except PermissionError:
        st.error("Admin access only.")
        return

    st.title("🛡️ Admin Dashboard")

    subs = get_all_subscriptions()
    logs = get_usage_stats(50)

    st.subheader("Subscriptions")
    st.write(f"Total: {len(subs)}")
    st.dataframe(subs)

    st.subheader("Recent Usage Logs")
    st.write(f"Last {len(logs)} entries")
    st.dataframe(logs)


if __name__ == "__main__":
    main()
