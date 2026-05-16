# core/auth.py

import streamlit as st
from .supabase_client import get_supabase


SESSION_USER_KEY = "user"


def _set_page_config():
    # Call once at app entry (or guard with flag)
    if "page_config_set" not in st.session_state:
        st.set_page_config(page_title="PDF SaaS", page_icon="📄", layout="wide")
        st.session_state.page_config_set = True


def _init_session():
    if SESSION_USER_KEY not in st.session_state:
        st.session_state[SESSION_USER_KEY] = None


def get_current_user():
    return st.session_state.get(SESSION_USER_KEY, None)


def login_form():
    sb = get_supabase()
    st.title("Login to PDF SaaS")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        try:
            res = sb.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                st.session_state[SESSION_USER_KEY] = res.user
                st.success("Logged in successfully.")
                st.rerun()
            else:
                st.error("Login failed. Please check your credentials.")
        except Exception as e:
            # Supabase AuthApiError, etc.
            msg = getattr(e, "message", str(e))
            if "Invalid login credentials" in msg:
                st.error("Invalid email or password.")
            else:
                st.error("Login error. Please try again.")
                st.caption(msg)


def logout():
    sb = get_supabase()
    try:
        sb.auth.sign_out()
    except Exception:
        # Even if remote sign_out fails, clear local session
        pass

    st.session_state[SESSION_USER_KEY] = None
    st.success("Logged out.")
    st.rerun()


def require_auth():
    _set_page_config()
    _init_session()

    user = get_current_user()
    if user is None:
        # Not logged in → show login UI and stop
        login_form()
        st.stop()

    # Logged in → return user object to app.py
    return user
