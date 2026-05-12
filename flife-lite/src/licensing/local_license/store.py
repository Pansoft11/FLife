from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet

from .machine import machine_hash

APP_DIR = Path(os.environ.get("FLIFE_PORTABLE_HOME") or os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "FLIFE"
LICENSE_FILE = APP_DIR / "license.bin"
KEY_FILE = APP_DIR / "license.key"
SERVER_URL = os.environ.get("FLIFE_LICENSE_SERVER", "http://127.0.0.1:8088")


def status() -> dict:
    payload = _read_license()
    if payload is None:
        return _status_payload("unactivated", "trial", 0, "", None)

    offline_until = payload.get("offline_until") or payload.get("offlineUntil") or ""
    try:
        state = "offline" if datetime.fromisoformat(offline_until) > datetime.now(timezone.utc) else "expired"
    except ValueError:
        state = "expired"
    return _status_payload(state, payload.get("type", "trial"), _days_until(offline_until), offline_until, payload.get("email"))


def activate(email: str, license_key: str) -> dict:
    response = _post(
        "/activate",
        {
            "email": email,
            "license_key": license_key,
            "machine_hash": machine_hash(),
        },
    )
    token_payload = _decode_unsigned_token(response["token"])
    token_payload["token"] = response["token"]
    _write_license(token_payload)
    return _status_payload("active", response["type"], response["days_remaining"], response["offline_until"], email)


def _post(path: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{SERVER_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"License server is unavailable: {exc}") from exc


def _status_payload(state: str, license_type: str, days_remaining: int, offline_until: str, email: str | None) -> dict:
    return {
        "state": state,
        "type": license_type,
        "daysRemaining": days_remaining,
        "offlineUntil": offline_until,
        "email": email,
    }


def _days_until(value: str) -> int:
    if not value:
        return 0
    try:
        return max(0, (datetime.fromisoformat(value) - datetime.now(timezone.utc)).days)
    except ValueError:
        return 0


def _cipher() -> Fernet:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not KEY_FILE.exists():
        KEY_FILE.write_bytes(Fernet.generate_key())
    return Fernet(KEY_FILE.read_bytes())


def _read_license() -> dict | None:
    if not LICENSE_FILE.exists():
        return None
    try:
        return json.loads(_cipher().decrypt(LICENSE_FILE.read_bytes()).decode("utf-8"))
    except Exception:
        return None


def _write_license(payload: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    LICENSE_FILE.write_bytes(_cipher().encrypt(json.dumps(payload).encode("utf-8")))


def _decode_unsigned_token(token: str) -> dict:
    import base64

    body, _signature = token.split(".", 1)
    return json.loads(base64.urlsafe_b64decode(body.encode("utf-8")).decode("utf-8"))
