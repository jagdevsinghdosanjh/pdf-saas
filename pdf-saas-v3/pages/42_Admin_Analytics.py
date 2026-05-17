import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.auth import require_auth
from core.admin import require_admin
from core.supabase_client import get_supabase


def main():
    user = require_auth()
    try:
        require_admin(user)
    except PermissionError:
        st.error("Admin access only.")
        return

    st.title("📈 Admin Analytics Dashboard")

    sb = get_supabase()

    # ---------------------------------------------------------
    # Load Data
    # ---------------------------------------------------------
    users = sb.table("profiles").select("*").execute().data or []
    subs = sb.table("subscriptions").select("*, plans(*)").execute().data or []
    logs = sb.table("usage_logs").select("*").order("created_at", desc=True).limit(5000).execute().data or []

    df_users = pd.DataFrame(users)
    df_subs = pd.DataFrame(subs)
    df_logs = pd.DataFrame(logs)

    # ---------------------------------------------------------
    # Revenue Calculations
    # ---------------------------------------------------------
    st.subheader("💰 Revenue Metrics")

    # Active paid subscriptions
    active_paid = df_subs[df_subs["status"].isin(["active", "trialing"])]

    # MRR
    active_paid["price"] = active_paid["plans"].apply(lambda p: p["price_monthly"])
    mrr = active_paid["price"].sum()

    # ARR
    arr = mrr * 12

    # ARPU
    total_users = len(df_users)
    arpu = mrr / total_users if total_users > 0 else 0

    # LTV (simple SaaS formula)
    churn_rate = 0.02  # default if no data
    if len(df_subs) > 10:
        cancelled = df_subs[df_subs["status"] == "canceled"]
        churn_rate = len(cancelled) / len(df_subs)

    ltv = (arpu / churn_rate) if churn_rate > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("MRR (₹)", f"{mrr:,.0f}")
    col2.metric("ARR (₹)", f"{arr:,.0f}")
    col3.metric("ARPU (₹)", f"{arpu:,.2f}")
    col4.metric("LTV (₹)", f"{ltv:,.0f}")

    st.metric("Churn Rate", f"{churn_rate*100:.2f}%")

    st.markdown("---")

    # ---------------------------------------------------------
    # Revenue by Plan
    # ---------------------------------------------------------
    st.subheader("📦 Revenue by Plan")

    if not active_paid.empty:
        plan_revenue = active_paid.groupby(active_paid["plans"].apply(lambda p: p["name"]))["price"].sum()
        st.bar_chart(plan_revenue)
    else:
        st.info("No active paid subscriptions.")

    st.markdown("---")

    # ---------------------------------------------------------
    # Revenue Timeline (Last 12 Months)
    # ---------------------------------------------------------
    st.subheader("📅 Revenue Timeline (Last 12 Months)")

    if not active_paid.empty:
        df_subs["start_date"] = pd.to_datetime(df_subs["current_period_start"]).dt.to_period("M")
        monthly_revenue = df_subs[df_subs["status"] == "active"].groupby("start_date")["plans"].apply(
            lambda x: sum(p["price_monthly"] for p in x)
        )

        st.line_chart(monthly_revenue)
    else:
        st.info("No revenue data available.")

    st.markdown("---")

    # ---------------------------------------------------------
    # Usage Metrics (DAU, MAU, etc.)
    # ---------------------------------------------------------
    st.subheader("📊 Usage Metrics")

    today = datetime.utcnow().date()
    dau = len({log["user_id"] for log in logs if log["created_at"][:10] == str(today)})

    this_month = datetime.utcnow().month
    this_year = datetime.utcnow().year
    mau = len({
        log["user_id"]
        for log in logs
        if datetime.fromisoformat(log["created_at"]).month == this_month
        and datetime.fromisoformat(log["created_at"]).year == this_year
    })

    new_users_30 = len([
        u for u in users
        if (datetime.utcnow() - datetime.fromisoformat(u["created_at"])).days <= 30
    ])

    col1, col2, col3 = st.columns(3)
    col1.metric("DAU", dau)
    col2.metric("MAU", mau)
    col3.metric("New Users (30 days)", new_users_30)

    st.markdown("---")

    # ---------------------------------------------------------
    # Feature Usage Breakdown
    # ---------------------------------------------------------
    st.subheader("🧩 Feature Usage Breakdown")

    if not df_logs.empty:
        feature_counts = df_logs["action"].value_counts()
        st.bar_chart(feature_counts)
    else:
        st.info("No feature usage data.")

    st.markdown("---")

    # ---------------------------------------------------------
    # Peak Hours Heatmap
    # ---------------------------------------------------------
    st.subheader("⏰ Peak Usage Hours")

    if not df_logs.empty:
        df_logs["hour"] = pd.to_datetime(df_logs["created_at"]).dt.hour
        heatmap = df_logs.groupby("hour").size()
        st.bar_chart(heatmap)
    else:
        st.info("No hourly usage data.")

    st.markdown("---")

    # ---------------------------------------------------------
    # Raw Data (Optional)
    # ---------------------------------------------------------
    with st.expander("Raw Subscriptions"):
        st.dataframe(df_subs)

    with st.expander("Raw Users"):
        st.dataframe(df_users)

    with st.expander("Raw Usage Logs"):
        st.dataframe(df_logs)


if __name__ == "__main__":
    main()

# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta
# from core.auth import require_auth
# from core.admin import require_admin
# from core.supabase_client import get_supabase


# def main():
#     user = require_auth()
#     try:
#         require_admin(user)
#     except PermissionError:
#         st.error("Admin access only.")
#         return

#     st.title("📈 Admin Analytics Dashboard")

#     sb = get_supabase()

#     # ---------------------------------------------------------
#     # Load Data
#     # ---------------------------------------------------------
#     users = sb.table("profiles").select("*").execute().data or []
#     subs = sb.table("subscriptions").select("*").execute().data or []
#     logs = sb.table("usage_logs").select("*").order("created_at", desc=True).limit(5000).execute().data or []

#     df_logs = pd.DataFrame(logs)
#     df_users = pd.DataFrame(users)

#     # ---------------------------------------------------------
#     # Metrics
#     # ---------------------------------------------------------
#     st.subheader("📊 Key Metrics")

#     total_users = len(users)
#     active_subs = len([s for s in subs if s["status"] in ["active", "trialing"]])

#     # DAU
#     today = datetime.utcnow().date()
#     dau = len({log["user_id"] for log in logs if log["created_at"][:10] == str(today)})

#     # MAU
#     this_month = datetime.utcnow().month
#     this_year = datetime.utcnow().year
#     mau = len({
#         log["user_id"]
#         for log in logs
#         if datetime.fromisoformat(log["created_at"]).month == this_month
#         and datetime.fromisoformat(log["created_at"]).year == this_year
#     })

#     # New users last 30 days
#     new_users_30 = len([
#         u for u in users
#         if (datetime.utcnow() - datetime.fromisoformat(u["created_at"])).days <= 30
#     ])

#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Total Users", total_users)
#     col2.metric("Active Subscriptions", active_subs)
#     col3.metric("DAU", dau)
#     col4.metric("MAU", mau)

#     st.metric("New Users (30 days)", new_users_30)

#     st.markdown("---")

#     # ---------------------------------------------------------
#     # Usage Timeline
#     # ---------------------------------------------------------
#     st.subheader("📅 Usage Timeline (Last 30 Days)")

#     if not df_logs.empty:
#         df_logs["date"] = pd.to_datetime(df_logs["created_at"]).dt.date
#         timeline = df_logs.groupby("date").size()

#         st.line_chart(timeline)
#     else:
#         st.info("No usage logs available.")

#     st.markdown("---")

#     # ---------------------------------------------------------
#     # Feature Usage Breakdown
#     # ---------------------------------------------------------
#     st.subheader("🧩 Feature Usage Breakdown")

#     if not df_logs.empty:
#         feature_counts = df_logs["action"].value_counts()
#         st.bar_chart(feature_counts)
#     else:
#         st.info("No feature usage data.")

#     st.markdown("---")

#     # ---------------------------------------------------------
#     # Peak Hours Heatmap
#     # ---------------------------------------------------------
#     st.subheader("⏰ Peak Usage Hours")

#     if not df_logs.empty:
#         df_logs["hour"] = pd.to_datetime(df_logs["created_at"]).dt.hour
#         heatmap = df_logs.groupby("hour").size()

#         st.bar_chart(heatmap)
#     else:
#         st.info("No hourly usage data.")

#     st.markdown("---")

#     # ---------------------------------------------------------
#     # Raw Data (Optional)
#     # ---------------------------------------------------------
#     with st.expander("Raw Usage Logs"):
#         st.dataframe(df_logs)

#     with st.expander("Raw Users"):
#         st.dataframe(df_users)


# if __name__ == "__main__":
#     main()
