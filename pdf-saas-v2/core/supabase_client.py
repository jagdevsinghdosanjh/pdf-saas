import streamlit as st
from supabase import create_client

_supabase = None

def get_supabase():
    global _supabase
    if _supabase is None:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        _supabase = create_client(url, key)
    return _supabase
