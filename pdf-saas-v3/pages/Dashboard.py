import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan
from core.usage import log_usage
from core.supabase_client import get_supabase


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)
    sb = get_supabase()

    st.title("📊 Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Plan", plan.name)
    with col2:
        st.metric("Max File Size (MB)", plan.max_file_size_mb)
    with col3:
        st.metric("Max Merge Files", plan.max_files_per_merge)

    st.markdown("### Recent Activity")
    res = (
        sb.table("usage_logs")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    logs = res.data or []
    for log in logs:
        st.write(f"- **{log['action']}** — {log['created_at']} — `{log.get('meta')}`")

    log_usage(user, "view_dashboard_page", {})


if __name__ == "__main__":
    main()
