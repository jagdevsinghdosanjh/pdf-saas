import streamlit as st
from core.supabase_client import get_supabase

sb = get_supabase()

st.write("Testing Supabase connection...")

try:
    res = sb.table("plans").select("*").execute()
    st.write("Response:", res)
except Exception as e:
    st.error("Supabase error:")
    st.code(str(e))
