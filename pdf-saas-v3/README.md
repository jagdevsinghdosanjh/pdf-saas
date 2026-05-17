# PDF SaaS v3

Streamlit + Supabase + Razorpay + PyMuPDF + pikepdf.

- Auth via Supabase
- Plans, subscriptions, usage logs
- 15 PDF tools (most fully implemented)
- Admin dashboard
- API keys (requires `api_keys` table)

Run:

```bash
pip install -r requirements.txt
streamlit run app.py

---

If you want, next step we can generate:

- Supabase `api_keys` table SQL  
- RLS policies for all tables  
- A small checklist for deploying this on Streamlit Cloud without surprises.