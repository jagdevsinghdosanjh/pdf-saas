import secrets
from .supabase_client import get_supabase
from .models import User


def generate_api_key() -> str:
    return secrets.token_hex(32)


def list_api_keys(user: User):
    sb = get_supabase()
    res = (
        sb.table("api_keys")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def create_api_key(user: User, label: str):
    sb = get_supabase()
    key = generate_api_key()
    sb.table("api_keys").insert(
        {
            "user_id": user.id,
            "label": label,
            "key": key,
        }
    ).execute()
    return key
