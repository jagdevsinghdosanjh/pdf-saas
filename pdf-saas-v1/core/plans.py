from dataclasses import dataclass
from typing import Dict, Any
from .supabase_client import get_supabase

@dataclass
class Plan:
    id: str
    slug: str
    name: str
    price_monthly: int
    max_file_size_mb: int
    max_files_per_merge: int
    ocr_enabled: bool

FREE_PLAN = Plan(
    id="free-local",
    slug="free",
    name="Free",
    price_monthly=0,
    max_file_size_mb=5,
    max_files_per_merge=2,
    ocr_enabled=False,
)

def _plan_from_row(row: Dict[str, Any]) -> Plan:
    return Plan(
        id=row["id"],
        slug=row["slug"],
        name=row["name"],
        price_monthly=row["price_monthly"],
        max_file_size_mb=row["max_file_size_mb"],
        max_files_per_merge=row["max_files_per_merge"],
        ocr_enabled=row["ocr_enabled"],
    )

def get_active_subscription_plan(user_id: str) -> Plan:
    sb = get_supabase()
    res = (
        sb.table("subscriptions")
        .select("status, current_period_end, plans(*)")
        .eq("user_id", user_id)
        .in_("status", ["trialing", "active"])
        .order("current_period_end", desc=True)
        .limit(1)
        .execute()
    )

    data = res.data or []
    if not data or not data[0].get("plans"):
        return FREE_PLAN

    return _plan_from_row(data[0]["plans"])

def enforce_limits(user_id: str, action: str, file_count=1, file_size_mb=0.0) -> Plan:
    plan = get_active_subscription_plan(user_id)

    if file_size_mb > plan.max_file_size_mb:
        raise ValueError(f"File too large for your plan (max {plan.max_file_size_mb} MB).")

    if action == "merge" and file_count > plan.max_files_per_merge:
        raise ValueError(f"Too many files for your plan (max {plan.max_files_per_merge}).")

    if action == "ocr" and not plan.ocr_enabled:
        raise ValueError("OCR is only available on Pro and Business plans.")

    return plan
