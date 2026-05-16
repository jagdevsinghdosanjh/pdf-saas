import streamlit as st
from core.supabase_client import get_supabase

st.title("Create an Account")

sb = get_supabase()

email = st.text_input("Email")
password = st.text_input("Password", type="password")
full_name = st.text_input("Full Name (optional)")

if st.button("Sign Up"):
    if not email or not password:
        st.error("Email and password are required.")
    else:
        try:
            # Create user in Supabase Auth
            res = sb.auth.sign_up({"email": email, "password": password})

            if res.user:
                # Create profile row
                sb.table("profiles").insert({
                    "id": res.user.id,
                    "email": email,
                    "full_name": full_name
                }).execute()

                st.success("Account created! Check your email to confirm, then log in.")
            else:
                st.error("Signup failed. Try again.")

        except Exception as e:
            st.error(str(e))
