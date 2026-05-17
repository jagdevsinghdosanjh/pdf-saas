from .supabase_client import get_supabase

def require_admin(user):
    """
    Ensures the logged-in user has admin privileges.
    Supports role-based access: admin, superadmin.
    """
    if not user:
        raise PermissionError("Not logged in")

    if getattr(user, "role", None) not in ["admin", "superadmin"]:
        raise PermissionError("Admin access required")

    return True


def get_all_users():
    """
    Returns all users from the profiles table.
    """
    sb = get_supabase()
    res = (
        sb.table("profiles")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def get_all_subscriptions():
    """
    Returns all subscriptions with plan and user info.
    """
    sb = get_supabase()
    res = (
        sb.table("subscriptions")
        .select("*, plans(*), profiles(email, full_name)")
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def get_usage_stats(limit: int = 100):
    """
    Returns recent usage logs.
    """
    sb = get_supabase()
    res = (
        sb.table("usage_logs")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


# from .supabase_client import get_supabase
# from .models import User

# def require_admin(user):
#     if user.role not in ["admin", "superadmin"]:
#         raise PermissionError("Admin access required.")

# # def require_admin(user: User):
# #     if not user.is_admin:
# #         raise PermissionError("Admin access required.")


# def get_all_users():
#     sb = get_supabase()
#     res = sb.table("profiles").select("*").order("created_at", desc=True).execute()
#     return res.data or []


# def get_all_subscriptions():
#     sb = get_supabase()
#     res = (
#         sb.table("subscriptions")
#         .select("*, plans(*), profiles(email, full_name)")
#         .order("created_at", desc=True)
#         .execute()
#     )
#     return res.data or []


# def get_usage_stats(limit: int = 100):
#     sb = get_supabase()
#     res = (
#         sb.table("usage_logs")
#         .select("*")
#         .order("created_at", desc=True)
#         .limit(limit)
#         .execute()
#     )
#     return res.data or []
