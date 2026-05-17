import streamlit as st
from core.auth import require_auth, logout
from core.plans import get_active_subscription_plan
from core.usage import log_usage


def main():
    user = require_auth()
    plan = get_active_subscription_plan(user)

    st.sidebar.title("📄 PDF SaaS v3")
    st.sidebar.write(user.email)
    st.sidebar.write(f"Plan: {plan.name}")
    if st.sidebar.button("Logout"):
        logout()

    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/1_Dashboard.py", label="🏠 Dashboard")
    st.sidebar.page_link("pages/2_Compress_PDF.py", label="🗜️ Compress PDF")
    st.sidebar.page_link("pages/3_Merge_PDF.py", label="➕ Merge PDFs")
    st.sidebar.page_link("pages/4_Split_PDF.py", label="✂️ Split PDF")
    st.sidebar.page_link("pages/5_Extract_Pages.py", label="📑 Extract Pages")
    st.sidebar.page_link("pages/6_Rotate_PDF.py", label="🔄 Rotate PDF")
    st.sidebar.page_link("pages/7_Watermark_PDF.py", label="💧 Watermark PDF")
    st.sidebar.page_link("pages/8_Protect_PDF.py", label="🔐 Protect PDF")
    st.sidebar.page_link("pages/9_Unlock_PDF.py", label="🔓 Unlock PDF")
    st.sidebar.page_link("pages/10_PDF_to_Images.py", label="🖼️ PDF → Images")
    st.sidebar.page_link("pages/11_Images_to_PDF.py", label="🖼️ Images → PDF")
    st.sidebar.page_link("pages/12_PDF_to_Word.py", label="📄 PDF → Word")
    st.sidebar.page_link("pages/13_Word_to_PDF.py", label="📄 Word → PDF")
    st.sidebar.page_link("pages/14_OCR_Reader.py", label="👁️ OCR Reader")
    st.sidebar.page_link("pages/15_Repair_PDF.py", label="🛠️ Repair PDF")
    st.sidebar.page_link("pages/16_Metadata_Editor.py", label="ℹ️ Metadata Editor")
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/20_Upgrade.py", label="⬆️ Upgrade Plan")
    st.sidebar.page_link("pages/30_API_Keys.py", label="🔑 API Keys")
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/40_Admin_Dashboard.py", label="🛡️ Admin Dashboard")
    st.sidebar.page_link("pages/41_Admin_Users.py", label="👥 Admin Users")
    st.sidebar.page_link("pages/42_Admin_Analytics.py", label="📈 Admin Analytics")


    st.title("Welcome to PDF SaaS v3")
    st.write("Hybrid dashboard + tools. Use the sidebar to access all features.")

    log_usage(user, "view_dashboard", {"entry": "app.py"})


if __name__ == "__main__":
    main()
