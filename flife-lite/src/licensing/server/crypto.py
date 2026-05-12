from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sign_payload(payload: dict[str, Any], secret: str | None = None) -> str:
    signing_secret = (secret or os.environ.get("FLIFE_LICENSE_SECRET") or "dev-only-change-me").encode("utf-8")
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(signing_secret, body, hashlib.sha256).digest()
    return f"{base64.urlsafe_b64encode(body).decode()}.{base64.urlsafe_b64encode(signature).decode()}"


def verify_token(token: str, secret: str | None = None) -> dict[str, Any]:
    body_b64, sig_b64 = token.split(".", 1)
    body = base64.urlsafe_b64decode(body_b64.encode("utf-8"))
    expected = sign_payload(json.loads(body), secret).split(".", 1)[1]
    if not hmac.compare_digest(sig_b64, expected):
        raise ValueError("Invalid license signature.")
    payload = json.loads(body)
    if datetime.fromisoformat(payload["expires_at"]) < utc_now():
        raise ValueError("License token has expired.")
    return payload


def offline_expiry(days: int = 14) -> str:
    return (utc_now() + timedelta(days=days)).isoformat()
