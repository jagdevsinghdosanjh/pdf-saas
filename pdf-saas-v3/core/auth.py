import streamlit as st
from typing import Optional
from .supabase_client import get_supabase
from .models import User

SESSION_USER_KEY = "user"
PAGE_CONFIG_FLAG = "page_config_set"


def set_page_config():
    if PAGE_CONFIG_FLAG not in st.session_state:
        st.set_page_config(
            page_title="PDF SaaS v3",
            page_icon="📄",
            layout="wide",
        )
        st.session_state[PAGE_CONFIG_FLAG] = True


def _init_session():
    if SESSION_USER_KEY not in st.session_state:
        st.session_state[SESSION_USER_KEY] = None


def get_current_user() -> Optional[User]:
    return st.session_state.get(SESSION_USER_KEY)


def _store_user(res_user, profile_row=None):
    st.session_state[SESSION_USER_KEY] = User(
        id=res_user.id,
        email=res_user.email,
        full_name=(profile_row or {}).get("full_name"),
        is_admin=(profile_row or {}).get("is_admin", False),
    )


def login_form():
    sb = get_supabase()
    st.title("Login to PDF SaaS v3")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if not submitted:
        return

    if not email or not password:
        st.error("Please enter both email and password.")
        return

    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            profile = (
                sb.table("profiles")
                .select("*")
                .eq("id", res.user.id)
                .maybe_single()
                .execute()
                .data
            )
            _store_user(res.user, profile)
            st.success("Logged in successfully.")
            st.rerun()
        else:
            st.error("Login failed. Check credentials.")
    except Exception as e:
        st.error("Login error.")
        st.caption(str(e))


def logout():
    sb = get_supabase()
    try:
        sb.auth.sign_out()
    except Exception:
        pass
    st.session_state[SESSION_USER_KEY] = None
    st.success("Logged out.")
    st.rerun()


def require_auth() -> User:
    set_page_config()
    _init_session()
    user = get_current_user()
    if user is None:
        login_form()
        st.stop()
    return user
