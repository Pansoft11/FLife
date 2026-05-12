from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum


class SubscriptionState(StrEnum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    OFFLINE_GRACE = "OFFLINE_GRACE"


def derive_subscription_state(*, active: bool, revoked: bool, expires_at: str, offline_until: str | None = None, trial: bool = False) -> SubscriptionState:
    now = datetime.now(timezone.utc)
    if revoked:
        return SubscriptionState.REVOKED
    if not active:
        return SubscriptionState.SUSPENDED
    if offline_until and datetime.fromisoformat(offline_until) > now:
        return SubscriptionState.OFFLINE_GRACE
    if datetime.fromisoformat(expires_at) < now:
        return SubscriptionState.EXPIRED
    if trial:
        return SubscriptionState.TRIAL
    return SubscriptionState.ACTIVE
