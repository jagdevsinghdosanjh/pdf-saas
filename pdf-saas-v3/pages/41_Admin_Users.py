import streamlit as st
from core.auth import require_auth
from core.admin import require_admin, get_all_users
from core.admin_log import log_admin_action
from core.supabase_client import get_supabase


def main():
    user = require_auth()
    try:
        require_admin(user)
    except PermissionError:
        st.error("Admin access only.")
        return

    st.title("👥 Admin Users")

    users = get_all_users()
    st.write(f"Total users: {len(users)}")
    st.dataframe(users)

    st.markdown("---")
    st.subheader("Manage User")

    user_ids = [u["id"] for u in users]
    selected = st.selectbox("Select user", user_ids)

    if not selected:
        return

    sb = get_supabase()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Disable User"):
            sb.table("profiles").update({"disabled": True}).eq("id", selected).execute()
            log_admin_action(user.id, "disable_user", selected)
            st.success("User disabled.")
            st.rerun()

        if st.button("Enable User"):
            sb.table("profiles").update({"disabled": False}).eq("id", selected).execute()
            log_admin_action(user.id, "enable_user", selected)
            st.success("User enabled.")
            st.rerun()

    with col2:
        if st.button("Promote to Admin"):
            sb.table("profiles").update({"role": "admin"}).eq("id", selected).execute()
            log_admin_action(user.id, "promote_admin", selected)
            st.success("User promoted to admin.")
            st.rerun()

        if st.button("Demote to User"):
            sb.table("profiles").update({"role": "user"}).eq("id", selected).execute()
            log_admin_action(user.id, "demote_admin", selected)
            st.success("User demoted.")
            st.rerun()

    with col3:
        if st.button("Impersonate User"):
            from core.auth import impersonate_user
            impersonate_user(selected)
            log_admin_action(user.id, "impersonate_user", selected)
            st.success("You are now impersonating this user.")
            st.rerun()

# import streamlit as st
# from core.auth import require_auth
# from core.admin import require_admin, get_all_users


# def main():
#     user = require_auth()
#     try:
#         require_admin(user)
#     except PermissionError:
#         st.error("Admin access only.")
#         return

#     st.title("👥 Admin Users")

#     users = get_all_users()
#     st.write(f"Total users: {len(users)}")
#     st.dataframe(users)


# if __name__ == "__main__":
#     main()
