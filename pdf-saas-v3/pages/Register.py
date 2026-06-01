import streamlit as st
from core.supabase_client import get_supabase

def register_form():
    sb = get_supabase()
    st.title("Register for PDF SaaS v3")

    with st.form("register_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        full_name = st.text_input("Full Name")
        submitted = st.form_submit_button("Register")

        if not submitted:
            return

        if not email or not password:
            st.error("Please enter both email and password.")
            return

        try:
            res = sb.auth.sign_up({"email": email, "password": password})
            if res.user:
                # Insert into profiles
                sb.table("profiles").insert({
                    "id": res.user.id,
                    "email": email,
                    "full_name": full_name,
                    "role": "user"
                }).execute()

                # Assign free plan subscription
                free_plan = sb.table("plans").select("id").eq("slug", "free").maybe_single().execute().data
                if free_plan:
                    sb.table("subscriptions").insert({
                        "user_id": res.user.id,
                        "plan_id": free_plan["id"],
                        "status": "active"
                    }).execute()

                st.success("Registration successful. Please log in.")
                st.page_link("pages/1_Login.py", label="Go to Login Page")
            else:
                st.error("Registration failed.")
        except Exception as e:
            st.error("Error during registration.")
            st.caption(str(e))

if __name__ == "__main__":
    register_form()
