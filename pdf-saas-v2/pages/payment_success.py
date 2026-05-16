import streamlit as st
from core.auth import require_auth
from core.supabase_client import get_supabase

st.title("Payment Successful")

user = require_auth()
sb = get_supabase()

order_id = st.session_state.get("order_id")
plan_id = st.session_state.get("selected_plan_id")

if not order_id or not plan_id:
    st.error("Invalid payment session.")
    st.stop()

# Fetch existing subscription
sub = (
    sb.table("subscriptions")
    .select("*")
    .eq("user_id", user.id)
    .maybe_single()
    .execute()
    .data
)

# Update or create subscription
if sub:
    sb.table("subscriptions").update({
        "plan_id": plan_id,
        "status": "active"
    }).eq("id", sub["id"]).execute()
else:
    sb.table("subscriptions").insert({
        "user_id": user.id,
        "plan_id": plan_id,
        "status": "active"
    }).execute()

st.success("Your plan has been upgraded successfully!")
st.balloons()

st.page_link("app.py", label="Go to Dashboard")
