import streamlit as st
from core.auth import require_auth
from core.supabase_client import get_supabase
from core.models import User

st.title("Upgrade Your Plan")

user: User = require_auth()
sb = get_supabase()

# -----------------------------
# SAFE Supabase query for plans
# -----------------------------
res = (
    sb.table("plans")
    .select("*")
    .order("price_monthly")
    .execute()
)

if not res or not hasattr(res, "data") or res.data is None:
    st.error("Could not load plans. Check Supabase or RLS policies.")
    st.stop()

plans = res.data

# -----------------------------
# Fetch current subscription
# -----------------------------
sub_res = (
    sb.table("subscriptions")
    .select("*")
    .eq("user_id", user.id)
    .eq("status", "active")
    .maybe_single()
    .execute()
)

sub = sub_res.data if sub_res and hasattr(sub_res, "data") else None
current_plan_id = sub["plan_id"] if sub else None

st.write("Choose a plan to unlock higher limits and premium features.")

cols = st.columns(len(plans))

for idx, plan in enumerate(plans):
    with cols[idx]:
        st.subheader(plan["name"])
        st.write(f"**₹{plan['price_monthly']} / month**")
        st.write(f"Max File Size: **{plan['max_file_size_mb']} MB**")
        st.write(f"Max Merge Files: **{plan['max_files_per_merge']}**")
        st.write(f"OCR Enabled: **{'Yes' if plan['ocr_enabled'] else 'No'}**")

        if plan["id"] == current_plan_id:
            st.success("Your Current Plan")
            continue

        if st.button(f"Upgrade to {plan['name']}", key=plan["id"]):

            # Update existing subscription
            if sub:
                sb.table("subscriptions").update({
                    "plan_id": plan["id"],
                    "status": "active"
                }).eq("id", sub["id"]).execute()

            # Create new subscription
            else:
                sb.table("subscriptions").insert({
                    "user_id": user.id,
                    "plan_id": plan["id"],
                    "status": "active"
                }).execute()

            st.success(f"Successfully upgraded to {plan['name']}!")
            st.rerun()


# import streamlit as st
# from core.auth import require_auth
# from core.supabase_client import get_supabase
# from core.models import User
# import razorpay

# st.title("Upgrade Your Plan")

# user: User = require_auth()
# sb = get_supabase()

# # Razorpay client
# client = razorpay.Client(
#     auth=(
#         st.secrets["razorpay"]["key_id"],
#         st.secrets["razorpay"]["key_secret"]
#     )
# )

# # Fetch all plans
# plans = (
#     sb.table("plans")
#     .select("*")
#     .order("price_monthly")
#     .execute()
#     .data
# )

# # Fetch current subscription
# sub = (
#     sb.table("subscriptions")
#     .select("*")
#     .eq("user_id", user.id)
#     .eq("status", "active")
#     .maybe_single()
#     .execute()
#     .data
# )

# current_plan_id = sub["plan_id"] if sub else None

# st.write("Choose a plan to unlock higher limits and premium features.")

# cols = st.columns(len(plans))

# for idx, plan in enumerate(plans):
#     with cols[idx]:
#         st.subheader(plan["name"])
#         st.write(f"**₹{plan['price_monthly']} / month**")
#         st.write(f"Max File Size: **{plan['max_file_size_mb']} MB**")
#         st.write(f"Max Merge Files: **{plan['max_files_per_merge']}**")
#         st.write("OCR Enabled: **{}**".format("Yes" if plan["ocr_enabled"] else "No"))

#         if plan["id"] == current_plan_id:
#             st.success("Your Current Plan")
#             continue

#         if st.button(f"Upgrade to {plan['name']}", key=plan["id"]):
#             amount = plan["price_monthly"] * 100  # Razorpay uses paise

#             # Create Razorpay order
#             order = client.order.create({
#                 "amount": amount,
#                 "currency": "INR",
#                 "payment_capture": 1
#             })

#             # Store session info
#             st.session_state["order_id"] = order["id"]
#             st.session_state["selected_plan_id"] = plan["id"]

#             # Razorpay Checkout Form
#             st.markdown(
#                 f"""
#                 <form action="/payment_success" method="POST">
#                   <script
#                     src="https://checkout.razorpay.com/v1/checkout.js"
#                     data-key="{st.secrets['razorpay']['key_id']}"
#                     data-amount="{amount}"
#                     data-currency="INR"
#                     data-order_id="{order['id']}"
#                     data-buttontext="Pay Now"
#                     data-name="PDF SaaS"
#                     data-description="Subscription Upgrade"
#                     data-prefill.name="{user.email}"
#                     data-theme.color="#0F9D58"
#                   ></script>
#                 </form>
#                 """,
#                 unsafe_allow_html=True
#             )
