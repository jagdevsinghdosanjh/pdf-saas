import streamlit as st
from core.auth import require_auth
from core.admin import require_admin, get_all_subscriptions, get_usage_stats, get_all_users
from core.supabase_client import get_supabase


def main():
    user = require_auth()
    try:
        require_admin(user)
    except PermissionError:
        st.error("Admin access only.")
        return

    st.title("🛡️ Admin Dashboard")

    users = get_all_users()
    subs = get_all_subscriptions()
    logs = get_usage_stats(50)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", len(users))
    col2.metric("Active Subscriptions", len(subs))
    col3.metric("Recent Usage Logs", len(logs))

    st.markdown("---")
    st.subheader("Recent Usage Logs")
    st.dataframe(logs)

    st.markdown("---")
    st.subheader("Recent Admin Actions")

    sb = get_supabase()
    admin_logs = (
        sb.table("admin_logs")
        .select("*")
        .order("created_at", desc=True)
        .limit(20)
        .execute()
        .data
    )

    st.dataframe(admin_logs)

# import streamlit as st
# from core.auth import require_auth
# from core.admin import require_admin, get_all_subscriptions, get_usage_stats


# def main():
#     user = require_auth()
#     try:
#         require_admin(user)
#     except PermissionError:
#         st.error("Admin access only.")
#         return

#     st.title("🛡️ Admin Dashboard")

#     subs = get_all_subscriptions()
#     logs = get_usage_stats(50)

#     st.subheader("Subscriptions")
#     st.write(f"Total: {len(subs)}")
#     st.dataframe(subs)

#     st.subheader("Recent Usage Logs")
#     st.write(f"Last {len(logs)} entries")
#     st.dataframe(logs)


# if __name__ == "__main__":
#     main()
