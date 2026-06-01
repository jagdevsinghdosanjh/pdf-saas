import streamlit as st
from core.auth import require_auth
from core.billing import activate_subscription_after_payment


def main():
    user = require_auth()

    st.title("✅ Payment Successful")

    order_id = st.session_state.get("order_id")
    plan_id = st.session_state.get("selected_plan_id")

    if not order_id or not plan_id:
        st.error("Invalid payment session.")
        return

    activate_subscription_after_payment(user, plan_id)

    st.success("Your plan has been upgraded successfully!")
    st.balloons()
    st.page_link("app.py", label="Go to Dashboard")


if __name__ == "__main__":
    main()
