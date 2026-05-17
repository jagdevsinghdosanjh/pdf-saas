import razorpay
import streamlit as st
from .supabase_client import get_supabase
from .models import User


def get_razorpay_client() -> razorpay.Client:
    key_id = st.secrets["razorpay"]["key_id"]
    key_secret = st.secrets["razorpay"]["key_secret"]
    return razorpay.Client(auth=(key_id, key_secret))


def create_subscription_order(user: User, plan_id: str, amount_inr: int) -> dict:
    client = get_razorpay_client()
    order = client.order.create(
        {
            "amount": amount_inr * 100,
            "currency": "INR",
            "payment_capture": 1,
            "notes": {"user_id": user.id, "plan_id": plan_id},
        }
    )
    return order


def activate_subscription_after_payment(user: User, plan_id: str):
    sb = get_supabase()
    sub = (
        sb.table("subscriptions")
        .select("*")
        .eq("user_id", user.id)
        .maybe_single()
        .execute()
        .data
    )

    if sub:
        sb.table("subscriptions").update(
            {
                "plan_id": plan_id,
                "status": "active",
            }
        ).eq("id", sub["id"]).execute()
    else:
        sb.table("subscriptions").insert(
            {
                "user_id": user.id,
                "plan_id": plan_id,
                "status": "active",
            }
        ).execute()
