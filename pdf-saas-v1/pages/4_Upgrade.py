import streamlit as st
from version_1.core.auth import require_auth
from version_1.core.supabase_client import get_supabase

st.title("Upgrade Your Plan")

user = require_auth()
supabase = get_supabase()

# -----------------------------
# Fetch all plans
# -----------------------------
plans = supabase.table("plans").select("*").order("price_monthly").execute().data

# Fetch user's current subscription
sub = supabase.table("subscriptions") \
    .select("*") \
    .eq("user_id", user["id"]) \
    .eq("status", "active") \
    .maybe_single() \
    .execute().data

current_plan_id = sub["plan_id"] if sub else None

# -----------------------------
# UI Layout
# -----------------------------
st.write("Choose a plan to unlock higher file size limits and more features.")

cols = st.columns(len(plans))

for idx, plan in enumerate(plans):
    with cols[idx]:
        st.subheader(plan["name"])
        st.write(f"**₹{plan['price_monthly']} / month**")
        st.write(f"Max File Size: **{plan['max_file_size_mb']} MB**")
        st.write(f"Max Merge Files: **{plan['max_files_per_merge']}**")
        st.write("OCR Enabled: **{}**".format("Yes" if plan["ocr_enabled"] else "No"))

        if plan["id"] == current_plan_id:
            st.success("Your Current Plan")
        else:
            if st.button(f"Upgrade to {plan['name']}", key=plan["id"]):
                # -----------------------------
                # Create or update subscription
                # -----------------------------
                if sub:
                    # Update existing subscription
                    supabase.table("subscriptions").update({
                        "plan_id": plan["id"],
                        "status": "active"
                    }).eq("id", sub["id"]).execute()
                else:
                    # Create new subscription
                    supabase.table("subscriptions").insert({
                        "user_id": user["id"],
                        "plan_id": plan["id"],
                        "status": "active"
                    }).execute()

                st.success(f"Successfully upgraded to {plan['name']}!")
                st.switch_page("app.py")
