import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone #noqa
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
    logs = (
        sb.table("usage_logs")
        .select("*")
        .order("created_at", desc=True)
        .limit(5000)
        .execute()
        .data
        or []
    )

    df_users = pd.DataFrame(users)
    df_subs = pd.DataFrame(subs)
    df_logs = pd.DataFrame(logs)

    # ---------------------------------------------------------
    # Revenue Calculations
    # ---------------------------------------------------------
    st.subheader("💰 Revenue Metrics")

    if not df_subs.empty:
        active_paid = df_subs[df_subs["status"].isin(["active", "trialing"])].copy()

        # MRR
        active_paid["price"] = active_paid["plans"].apply(
            lambda p: p.get("price_monthly", 0) if isinstance(p, dict) else 0
        )
        mrr = float(active_paid["price"].sum())

        # ARR
        arr = mrr * 12

        # ARPU
        total_users = len(df_users)
        arpu = mrr / total_users if total_users > 0 else 0

        # Churn rate (simple)
        churn_rate = 0.02
        if len(df_subs) > 10:
            cancelled = df_subs[df_subs["status"] == "canceled"]
            churn_rate = len(cancelled) / len(df_subs) if len(df_subs) > 0 else 0

        # LTV
        ltv = (arpu / churn_rate) if churn_rate > 0 else 0
    else:
        mrr = arr = arpu = ltv = 0.0
        churn_rate = 0.0
        active_paid = pd.DataFrame()

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
        def plan_name(p):
            if isinstance(p, dict):
                return p.get("name", "Unknown")
            return "Unknown"

        active_paid["plan_name"] = active_paid["plans"].apply(plan_name)
        plan_revenue = active_paid.groupby("plan_name")["price"].sum()
        st.bar_chart(plan_revenue)
    else:
        st.info("No active paid subscriptions.")

    st.markdown("---")

    # ---------------------------------------------------------
    # Revenue Timeline (Last 12 Months)
    # ---------------------------------------------------------
    st.subheader("📅 Revenue Timeline (Last 12 Months)")

    if not df_subs.empty:
        df_subs["start_date"] = pd.to_datetime(
            df_subs["current_period_start"], errors="coerce"
        ).dt.to_period("M")

        def plan_price_monthly(p):
            if isinstance(p, dict):
                return p.get("price_monthly", 0)
            return 0

        active_only = df_subs[df_subs["status"] == "active"].copy()
        if not active_only.empty:
            active_only["price"] = active_only["plans"].apply(plan_price_monthly)
            monthly_revenue = active_only.groupby("start_date")["price"].sum()
            st.line_chart(monthly_revenue)
        else:
            st.info("No active revenue data available.")
    else:
        st.info("No revenue data available.")

    st.markdown("---")

    # ---------------------------------------------------------
    # Usage Metrics (DAU, MAU, New Users)
    # ---------------------------------------------------------
    st.subheader("📊 Usage Metrics")

    now = datetime.now(timezone.utc)

    # DAU
    dau_users = set()
    for log in logs:
        try:
            ts = datetime.fromisoformat(log["created_at"]).astimezone(timezone.utc)
            if ts.date() == now.date():
                dau_users.add(log["user_id"])
        except Exception:
            continue
    dau = len(dau_users)

    # MAU
    mau_users = set()
    for log in logs:
        try:
            ts = datetime.fromisoformat(log["created_at"]).astimezone(timezone.utc)
            if ts.year == now.year and ts.month == now.month:
                mau_users.add(log["user_id"])
        except Exception:
            continue
    mau = len(mau_users)

    # New users in last 30 days
    new_users_30 = 0
    for u in users:
        try:
            created_at = datetime.fromisoformat(u["created_at"]).astimezone(timezone.utc)
            if (now - created_at).days <= 30:
                new_users_30 += 1
        except Exception:
            continue

    col1, col2, col3 = st.columns(3)
    col1.metric("DAU", dau)
    col2.metric("MAU", mau)
    col3.metric("New Users (30 days)", new_users_30)

    st.markdown("---")

    # ---------------------------------------------------------
    # Feature Usage Breakdown
    # ---------------------------------------------------------
    st.subheader("🧩 Feature Usage Breakdown")

    if not df_logs.empty and "action" in df_logs.columns:
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
        df_logs["created_at_dt"] = pd.to_datetime(
            df_logs["created_at"], errors="coerce"
        )
        df_logs["hour"] = df_logs["created_at_dt"].dt.hour
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
