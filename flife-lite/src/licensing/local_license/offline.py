from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .machine import machine_hash


def create_offline_request(path: str | Path, email: str, license_key: str) -> Path:
    target = Path(path).with_suffix(".flreq")
    payload = {
        "format": "FLIFE_OFFLINE_ACTIVATION_REQUEST",
        "version": "1.0",
        "email": email,
        "license_key": license_key,
        "machine_hash": machine_hash(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def read_offline_response(path: str | Path) -> dict:
    target = Path(path)
    if target.suffix != ".flres":
        raise ValueError("Offline activation response must use .flres extension.")
    payload = json.loads(target.read_text(encoding="utf-8"))
    if payload.get("format") != "FLIFE_OFFLINE_ACTIVATION_RESPONSE":
        raise ValueError("Invalid FLIFE offline response file.")
    return payload
