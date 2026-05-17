from .supabase_client import get_supabase
from .models import User

def require_admin(user):
    if user.role not in ["admin", "superadmin"]:
        raise PermissionError("Admin access required.")

# def require_admin(user: User):
#     if not user.is_admin:
#         raise PermissionError("Admin access required.")


def get_all_users():
    sb = get_supabase()
    res = sb.table("profiles").select("*").order("created_at", desc=True).execute()
    return res.data or []


def get_all_subscriptions():
    sb = get_supabase()
    res = (
        sb.table("subscriptions")
        .select("*, plans(*), profiles(email, full_name)")
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def get_usage_stats(limit: int = 100):
    sb = get_supabase()
    res = (
        sb.table("usage_logs")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []
