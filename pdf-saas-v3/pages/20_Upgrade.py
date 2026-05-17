import streamlit as st
from core.auth import require_auth
from core.supabase_client import get_supabase
from core.billing import create_subscription_order


def main():
    user = require_auth()
    sb = get_supabase()

    st.title("⬆️ Upgrade Your Plan")

    res = sb.table("plans").select("*").order("price_monthly").execute()
    plans = res.data or []

    if not plans:
        st.error("Could not load plans. Check Supabase.")
        return

    cols = st.columns(len(plans))

    for idx, plan in enumerate(plans):
        with cols[idx]:
            st.subheader(plan["name"])
            st.write(f"**₹{plan['price_monthly']} / month**")
            st.write(f"Max File Size: **{plan['max_file_size_mb']} MB**")
            st.write(f"Max Merge Files: **{plan['max_files_per_merge']}**")
            st.write(f"OCR Enabled: **{'Yes' if plan['ocr_enabled'] else 'No'}**")

            if st.button(f"Choose {plan['name']}", key=plan["id"]):
                order = create_subscription_order(
                    user, plan["id"], plan["price_monthly"]
                )
                st.session_state["selected_plan_id"] = plan["id"]
                st.session_state["order_id"] = order["id"]
                st.success("Order created. Proceed to payment.")
                st.write("Integrate Razorpay Checkout here (JS or redirect).")


if __name__ == "__main__":
    main()
