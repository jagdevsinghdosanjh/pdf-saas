from core.supabase_client import get_supabase

def log_admin_action(admin_id, action, target_user=None, meta=None):
    sb = get_supabase()
    sb.table("admin_logs").insert({
        "admin_id": admin_id,
        "action": action,
        "target_user": target_user,
        "meta": meta or {}
    }).execute()
