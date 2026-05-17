import razorpay
import uuid
import streamlit as st

def create_subscription_order(user, plan_id, price):
    client = razorpay.Client(
        auth=(
            st.secrets["razorpay_key_id"],
            st.secrets["razorpay_key_secret"]
        )
    )

    # Ensure price is valid
    if price is None:
        raise ValueError("Plan price is missing in database.")

    amount = int(price) * 100  # convert to paise

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_{uuid.uuid4()}",
        "payment_capture": 1
    })

    return order
