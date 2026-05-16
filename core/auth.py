import streamlit as st
from supabase import Client
from .supabase_client import get_supabase

def get_client() -> Client:
    return get_supabase()

def login_form():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        sb = get_client()
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res.user is None:
            st.error("Invalid credentials")
        else:
            st.session_state["sb_session"] = res.session
            st.rerun()

def signup_form():
    st.subheader("Sign up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Create account"):
        sb = get_client()
        res = sb.auth.sign_up({"email": email, "password": password})
        if res.user:
            sb.table("profiles").insert({
                "id": res.user.id,
                "email": email
            }).execute()
            st.success("Check your email to confirm, then log in.")

def get_current_user():
    session = st.session_state.get("sb_session")
    if not session:
        return None
    sb = get_client()
    return sb.auth.get_user(session.access_token).user

def require_auth():
    user = get_current_user()
    if user is None:
        st.info("Please log in to continue.")
        login_form()
        st.stop()
    return user
