import streamlit as st
from version_1.core.auth import require_auth
from version_1.core.plans import get_active_subscription_plan

st.set_page_config(page_title="PDF SaaS", page_icon="📄", layout="wide")

user = require_auth()
plan = get_active_subscription_plan(user.id)

st.sidebar.title("PDF SaaS")
st.sidebar.write(f"Logged in as: {user.email}")
st.sidebar.write(f"Plan: {plan.name}")

st.title("Welcome to PDF SaaS")
st.write("Choose a tool from the sidebar:")
st.write("• Compress PDF")
st.write("• Merge PDFs")
st.write("• OCR Reader")
st.write("• Scanner")
