import streamlit as st
from core.auth import require_auth
from core.plans import get_active_subscription_plan
from services.pdf_compress import compress_pdf

st.title("Compress PDF")

user = require_auth()
plan = get_active_subscription_plan(user["id"])

uploaded = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded:
    pdf_bytes = uploaded.read()
    size_mb = len(pdf_bytes) / (1024 * 1024)

    st.info(f"Uploaded file size: {size_mb:.2f} MB")
    st.caption(f"Your Plan: {plan['name']} (max {plan['max_file_size_mb']} MB)")

    # -----------------------------
    # FREE PLAN LIMIT CHECK
    # -----------------------------
    if size_mb > plan["max_file_size_mb"]:
        st.error(f"❌ Your plan allows only {plan['max_file_size_mb']} MB.")

        st.warning("Upgrade to compress larger files:")

        st.markdown("""
        ### 🚀 Upgrade Plans

        **Basic – ₹99/month**  
        - Max file size: 50 MB  
        - Faster compression  

        **Pro – ₹199/month**  
        - Max file size: 200 MB  
        - Bulk compression  
        - OCR enabled  

        **Lifetime – ₹999 one-time**  
        - Unlimited file size  
        - Offline EXE  
        - Lifetime updates  
        """)

        st.page_link("pages/4_Upgrade.py", label="Upgrade Now")
        st.stop()

    # -----------------------------
    # COMPRESSION ALLOWED
    # -----------------------------
    if st.button("Compress"):
        with st.spinner("Compressing..."):
            compressed = compress_pdf(pdf_bytes)

        if compressed:
            st.success("Compression complete!")
            st.download_button(
                "Download Compressed PDF",
                compressed,
                "compressed.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Compression failed.")

# import streamlit as st
# from core.auth import require_auth
# from core.plans import enforce_limits
# from services.pdf_compress import compress_pdf

# st.title("Compress PDF")

# user = require_auth()
# uploaded = st.file_uploader("Upload PDF", type=["pdf"])

# if uploaded:
#     size_mb = uploaded.size / (1024 * 1024)
#     try:
#         plan = enforce_limits(user.id, "compress", file_size_mb=size_mb)
#         st.caption(f"Plan: {plan.name} (max {plan.max_file_size_mb} MB)")
#         if st.button("Compress"):
#             out_bytes = compress_pdf(uploaded.read())
#             st.download_button("Download compressed PDF", out_bytes, "compressed.pdf")
#     except ValueError as e:
#         st.error(str(e))
