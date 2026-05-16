from .supabase_client import get_supabase

def get_user_plan(user_id):
    sb = get_supabase()
    subs = sb.table("subscriptions").select(
        "status, current_period_end, plans(*)"
    ).eq("user_id", user_id).eq("status", "active").execute()
    data = subs.data
    if not data:
        return None
    return data[0]["plans"]

def enforce_limits(user_id, action, file_count=1, file_size_mb=0):
    plan = get_user_plan(user_id)
    if plan is None:
        # treat as free
        plan = {
            "slug": "free",
            "max_file_size_mb": 5,
            "max_files_per_merge": 2,
            "ocr_enabled": False,
        }

    if file_size_mb > plan["max_file_size_mb"]:
        raise ValueError(f"File too large for your plan (max {plan['max_file_size_mb']} MB).")

    if action == "merge" and file_count > plan["max_files_per_merge"]:
        raise ValueError(f"Too many files for your plan (max {plan['max_files_per_merge']}).")

    if action == "ocr" and not plan["ocr_enabled"]:
        raise ValueError("OCR is only available on Pro and above.")

    return plan
