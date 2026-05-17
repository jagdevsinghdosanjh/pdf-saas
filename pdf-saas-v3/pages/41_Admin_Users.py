import streamlit as st
from core.auth import require_auth
from core.admin import require_admin, get_all_users


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


if __name__ == "__main__":
    main()
