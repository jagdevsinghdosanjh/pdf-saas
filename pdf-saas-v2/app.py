import streamlit as st
from core.auth import require_auth, logout
from core.plans import get_active_subscription_plan

user = require_auth()
plan = get_active_subscription_plan(user)

st.sidebar.title("PDF SaaS")
st.sidebar.write(user.email)
st.sidebar.write(f"Plan: {plan.name}")
if st.sidebar.button("Logout"):
    logout()

st.title("Welcome to PDF SaaS")
st.write("Choose a tool from the sidebar pages:")
st.write("- Compress PDF")
st.write("- Merge PDFs")
st.write("- OCR Reader")
