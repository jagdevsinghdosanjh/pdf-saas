from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime

SubscriptionStatus = Literal["trialing", "active", "past_due", "canceled"]


@dataclass
class User:
    id: str
    email: str
    full_name: Optional[str] = None
    is_admin: bool = False


@dataclass
class Plan:
    id: str
    slug: str
    name: str
    price_monthly: int
    max_file_size_mb: int
    max_files_per_merge: int
    ocr_enabled: bool


@dataclass
class Subscription:
    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
