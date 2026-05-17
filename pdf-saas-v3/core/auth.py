import streamlit as st
from typing import Optional
from .supabase_client import get_supabase
from .models import User

SESSION_USER_KEY = "user"
PAGE_CONFIG_FLAG = "page_config_set"


# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
def set_page_config():
    if PAGE_CONFIG_FLAG not in st.session_state:
        st.set_page_config(
            page_title="PDF SaaS v3",
            page_icon="📄",
            layout="wide",
        )
        st.session_state[PAGE_CONFIG_FLAG] = True


# ---------------------------------------------------------
# Session Init
# ---------------------------------------------------------
def _init_session():
    if SESSION_USER_KEY not in st.session_state:
        st.session_state[SESSION_USER_KEY] = None


def get_current_user() -> Optional[User]:
    return st.session_state.get(SESSION_USER_KEY)


# ---------------------------------------------------------
# Store User in Session
# ---------------------------------------------------------
def _store_user(res_user, profile_row=None):
    role = (profile_row or {}).get("role", "user")
    disabled = (profile_row or {}).get("disabled", False)

    st.session_state[SESSION_USER_KEY] = User(
        id=res_user.id,
        email=res_user.email,
        full_name=(profile_row or {}).get("full_name"),
        is_admin=(role in ["admin", "superadmin"]),
        role=role,
        disabled=disabled,
    )


# ---------------------------------------------------------
# Login Form
# ---------------------------------------------------------
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

            # Disabled user check
            if profile and profile.get("disabled"):
                st.error("Your account has been disabled by an administrator.")
                return

            _store_user(res.user, profile)
            st.success("Logged in successfully.")
            st.rerun()

        else:
            st.error("Login failed. Check credentials.")

    except Exception as e:
        st.error("Login error.")
        st.caption(str(e))


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------
def logout():
    sb = get_supabase()
    try:
        sb.auth.sign_out()
    except Exception:
        pass

    st.session_state[SESSION_USER_KEY] = None
    st.success("Logged out.")
    st.rerun()


# ---------------------------------------------------------
# Maintenance Mode (SAFE VERSION)
# ---------------------------------------------------------
def check_maintenance_mode():
    sb = get_supabase()

    try:
        # Try to read the maintenance_mode row
        res = (
            sb.table("settings")
            .select("value")
            .eq("key", "maintenance_mode")
            .maybe_single()
            .execute()
        )
    except Exception:
        # Table does not exist → allow login
        return

    # If execute() returned None → allow login
    if res is None:
        return

    row = res.data

    # If row missing → allow login
    if not row:
        return

    # If value missing → allow login
    value = row.get("value", {})
    if not isinstance(value, dict):
        return

    # If enabled → block login
    if value.get("enabled", False):
        st.error("The system is under maintenance. Please try again later.")
        st.stop()

# def check_maintenance_mode():
#     sb = get_supabase()

#     try:
#         res = (
#             sb.table("settings")
#             .select("*")
#             .eq("key", "maintenance_mode")
#             .maybe_single()
#             .execute()
#         )
#     except Exception:
#         # Table does not exist yet → allow login
#         return

#     row = res.data

#     if not row:
#         # No maintenance row → system is active
#         return

#     if row.get("value", {}).get("enabled", False):
#         st.error("The system is under maintenance. Please try again later.")
#         st.stop()


# ---------------------------------------------------------
# Impersonation (Admin Only)
# ---------------------------------------------------------
def impersonate_user(user_id: str):
    sb = get_supabase()
    profile = (
        sb.table("profiles")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
        .data
    )

    st.session_state[SESSION_USER_KEY] = User(
        id=profile["id"],
        email=profile["email"],
        full_name=profile.get("full_name"),
        is_admin=False,
        role="user",
        disabled=profile.get("disabled", False),
    )


# ---------------------------------------------------------
# Require Auth
# ---------------------------------------------------------
def require_auth() -> User:
    set_page_config()
    _init_session()

    # Check maintenance mode BEFORE login
    check_maintenance_mode()

    user = get_current_user()

    if user is None:
        login_form()
        st.stop()

    # Disabled user check
    if getattr(user, "disabled", False):
        st.error("Your account has been disabled by an administrator.")
        st.stop()

    return user


# import streamlit as st
# from typing import Optional
# from .supabase_client import get_supabase
# from .models import User

# SESSION_USER_KEY = "user"
# PAGE_CONFIG_FLAG = "page_config_set"


# # ---------------------------------------------------------
# # Page Config
# # ---------------------------------------------------------
# def set_page_config():
#     if PAGE_CONFIG_FLAG not in st.session_state:
#         st.set_page_config(
#             page_title="PDF SaaS v3",
#             page_icon="📄",
#             layout="wide",
#         )
#         st.session_state[PAGE_CONFIG_FLAG] = True


# # ---------------------------------------------------------
# # Session Init
# # ---------------------------------------------------------
# def _init_session():
#     if SESSION_USER_KEY not in st.session_state:
#         st.session_state[SESSION_USER_KEY] = None


# def get_current_user() -> Optional[User]:
#     return st.session_state.get(SESSION_USER_KEY)


# # ---------------------------------------------------------
# # Store User in Session
# # ---------------------------------------------------------
# def _store_user(res_user, profile_row=None):
#     role = (profile_row or {}).get("role", "user")
#     disabled = (profile_row or {}).get("disabled", False)

#     st.session_state[SESSION_USER_KEY] = User(
#         id=res_user.id,
#         email=res_user.email,
#         full_name=(profile_row or {}).get("full_name"),
#         is_admin=(role in ["admin", "superadmin"]),
#         role=role,
#         disabled=disabled,
#     )


# # ---------------------------------------------------------
# # Login Form
# # ---------------------------------------------------------
# def login_form():
#     sb = get_supabase()
#     st.title("Login to PDF SaaS v3")

#     with st.form("login_form"):
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("Login")

#     if not submitted:
#         return

#     if not email or not password:
#         st.error("Please enter both email and password.")
#         return

#     try:
#         res = sb.auth.sign_in_with_password({"email": email, "password": password})

#         if res.user:
#             profile = (
#                 sb.table("profiles")
#                 .select("*")
#                 .eq("id", res.user.id)
#                 .maybe_single()
#                 .execute()
#                 .data
#             )

#             # Check disabled user
#             if profile and profile.get("disabled"):
#                 st.error("Your account has been disabled by an administrator.")
#                 return

#             _store_user(res.user, profile)
#             st.success("Logged in successfully.")
#             st.rerun()

#         else:
#             st.error("Login failed. Check credentials.")

#     except Exception as e:
#         st.error("Login error.")
#         st.caption(str(e))


# # ---------------------------------------------------------
# # Logout
# # ---------------------------------------------------------
# def logout():
#     sb = get_supabase()
#     try:
#         sb.auth.sign_out()
#     except Exception:
#         pass

#     st.session_state[SESSION_USER_KEY] = None
#     st.success("Logged out.")
#     st.rerun()


# # ---------------------------------------------------------
# # Maintenance Mode
# # ---------------------------------------------------------
# def check_maintenance_mode():
#     sb = get_supabase()
#     row = (
#         sb.table("settings")
#         .select("*")
#         .eq("key", "maintenance_mode")
#         .maybe_single()
#         .execute()
#         .data
#     )

#     if row and row["value"].get("enabled"):
#         st.error("The system is under maintenance. Please try again later.")
#         st.stop()


# # ---------------------------------------------------------
# # Impersonation (Admin Only)
# # ---------------------------------------------------------
# def impersonate_user(user_id: str):
#     sb = get_supabase()
#     profile = (
#         sb.table("profiles")
#         .select("*")
#         .eq("id", user_id)
#         .single()
#         .execute()
#         .data
#     )

#     # Impersonated user always becomes a normal user
#     st.session_state[SESSION_USER_KEY] = User(
#         id=profile["id"],
#         email=profile["email"],
#         full_name=profile.get("full_name"),
#         is_admin=False,
#         role="user",
#         disabled=profile.get("disabled", False),
#     )


# # ---------------------------------------------------------
# # Require Auth
# # ---------------------------------------------------------
# def require_auth() -> User:
#     set_page_config()
#     _init_session()

#     # Check maintenance mode BEFORE login
#     check_maintenance_mode()

#     user = get_current_user()

#     if user is None:
#         login_form()
#         st.stop()

#     # Check disabled user
#     if getattr(user, "disabled", False):
#         st.error("Your account has been disabled by an administrator.")
#         st.stop()

#     return user


# # import streamlit as st
# # from typing import Optional
# # from .supabase_client import get_supabase
# # from .models import User

# # SESSION_USER_KEY = "user"
# # PAGE_CONFIG_FLAG = "page_config_set"


# # def set_page_config():
# #     if PAGE_CONFIG_FLAG not in st.session_state:
# #         st.set_page_config(
# #             page_title="PDF SaaS v3",
# #             page_icon="📄",
# #             layout="wide",
# #         )
# #         st.session_state[PAGE_CONFIG_FLAG] = True


# # def _init_session():
# #     if SESSION_USER_KEY not in st.session_state:
# #         st.session_state[SESSION_USER_KEY] = None


# # def get_current_user() -> Optional[User]:
# #     return st.session_state.get(SESSION_USER_KEY)


# # def _store_user(res_user, profile_row=None):
# #     st.session_state[SESSION_USER_KEY] = User(
# #         id=res_user.id,
# #         email=res_user.email,
# #         full_name=(profile_row or {}).get("full_name"),
# #         is_admin=(profile_row or {}).get("is_admin", False),
# #     )


# # def login_form():
# #     sb = get_supabase()
# #     st.title("Login to PDF SaaS v3")

# #     with st.form("login_form"):
# #         email = st.text_input("Email")
# #         password = st.text_input("Password", type="password")
# #         submitted = st.form_submit_button("Login")

# #     if not submitted:
# #         return

# #     if not email or not password:
# #         st.error("Please enter both email and password.")
# #         return

# #     try:
# #         res = sb.auth.sign_in_with_password({"email": email, "password": password})
# #         if res.user:
# #             profile = (
# #                 sb.table("profiles")
# #                 .select("*")
# #                 .eq("id", res.user.id)
# #                 .maybe_single()
# #                 .execute()
# #                 .data
# #             )
# #             _store_user(res.user, profile)
# #             st.success("Logged in successfully.")
# #             st.rerun()
# #         else:
# #             st.error("Login failed. Check credentials.")
# #     except Exception as e:
# #         st.error("Login error.")
# #         st.caption(str(e))


# # def logout():
# #     sb = get_supabase()
# #     try:
# #         sb.auth.sign_out()
# #     except Exception:
# #         pass
# #     st.session_state[SESSION_USER_KEY] = None
# #     st.success("Logged out.")
# #     st.rerun()

# # def check_maintenance_mode():
# #     sb = get_supabase()
# #     row = sb.table("settings").select("*").eq("key", "maintenance_mode").single().execute().data
# #     if row["value"]["enabled"]:
# #         st.error("The system is under maintenance. Please try again later.")
# #         st.stop()

# # def require_auth() -> User:
# #     set_page_config()
# #     _init_session()
# #     user = get_current_user()
# #     if user is None:
# #         login_form()
# #         st.stop()
# #     return user
