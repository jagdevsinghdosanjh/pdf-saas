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

    # Validate price
    if price is None:
        raise ValueError("Plan price is missing in database.")
    if not isinstance(price, (int, float)):
        raise ValueError(f"Plan price must be numeric, got {type(price)}")

    # Razorpay expects amount in paise (integer)
    amount = int(price * 100)

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_{uuid.uuid4()}",
        "payment_capture": 1,
        "notes": {
            "plan_id": plan_id,
            "user_id": user["id"],
        },
    })

    return order

# import razorpay
# import streamlit as st
# from .supabase_client import get_supabase
# from .models import User


# def get_razorpay_client() -> razorpay.Client:
#     key_id = st.secrets["razorpay"]["key_id"]
#     key_secret = st.secrets["razorpay"]["key_secret"]
#     return razorpay.Client(auth=(key_id, key_secret))


# def create_subscription_order(user: User, plan_id: str, amount_inr: int) -> dict:
#     client = get_razorpay_client()
#     order = client.order.create(
#         {
#             "amount": amount_inr * 100,
#             "currency": "INR",
#             "payment_capture": 1,
#             "notes": {"user_id": user.id, "plan_id": plan_id},
#         }
#     )
#     return order


# def activate_subscription_after_payment(user: User, plan_id: str):
#     sb = get_supabase()
#     sub = (
#         sb.table("subscriptions")
#         .select("*")
#         .eq("user_id", user.id)
#         .maybe_single()
#         .execute()
#         .data
#     )

#     if sub:
#         sb.table("subscriptions").update(
#             {
#                 "plan_id": plan_id,
#                 "status": "active",
#             }
#         ).eq("id", sub["id"]).execute()
#     else:
#         sb.table("subscriptions").insert(
#             {
#                 "user_id": user.id,
#                 "plan_id": plan_id,
#                 "status": "active",
#             }
#         ).execute()
