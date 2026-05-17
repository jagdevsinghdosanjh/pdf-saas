from typing import Optional, Dict, Any
from .supabase_client import get_supabase
from .models import User


def log_usage(user: User, action: str, meta: Optional[Dict[str, Any]] = None):
    sb = get_supabase()
    try:
        sb.table("usage_logs").insert(
            {
                "user_id": user.id,
                "action": action,
                "meta": meta or {},
            }
        ).execute()
    except Exception:
        pass
