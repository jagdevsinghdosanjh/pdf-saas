import streamlit as st
from core.auth import require_auth

st.set_page_config(page_title="PDF SaaS", page_icon="📄", layout="wide")

user = require_auth()
st.sidebar.success(f"Logged in as {user['email']}")
st.title("PDF Toolkit SaaS")
st.write("Use the pages on the left to compress, merge, or OCR your PDFs.")
