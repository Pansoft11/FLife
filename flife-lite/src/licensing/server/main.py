from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException

from .crypto import offline_expiry, sign_payload, utc_now, verify_token
from .database import connect
from .models import ActivationRequest, DeactivationRequest, LicenseResponse, MachineTransferRequest, RevocationRequest, ValidationRequest

DEFAULT_DB_PATH = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "FLIFE" / "server" / "flife_licenses.sqlite3"
DB_PATH = os.environ.get("FLIFE_LICENSE_DB", str(DEFAULT_DB_PATH))

app = FastAPI(title="FLIFE Lite Licensing Server", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    with connect(DB_PATH) as db:
        expires = datetime(2027, 5, 12, tzinfo=timezone.utc).isoformat()
        db.execute(
            "INSERT OR IGNORE INTO licenses (license_key, email, license_type, expires_at, max_activations, active, revoked) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("FLIFE-TRIAL-DEV-2026", "trial@flife.local", "trial", expires, 3, 1, 0),
        )


@app.post("/activate", response_model=LicenseResponse)
def activate(request: ActivationRequest) -> LicenseResponse:
    with connect(DB_PATH) as db:
        license_row = db.execute("SELECT * FROM licenses WHERE license_key = ? AND active = 1 AND revoked = 0", (request.license_key,)).fetchone()
        if license_row is None:
            raise HTTPException(status_code=404, detail="License key not found or inactive.")

        active_count = db.execute(
            "SELECT COUNT(*) AS total FROM activations WHERE license_key = ? AND deactivated_at IS NULL",
            (request.license_key,),
        ).fetchone()["total"]
        existing = db.execute(
            "SELECT * FROM activations WHERE license_key = ? AND machine_hash = ? AND deactivated_at IS NULL",
            (request.license_key, request.machine_hash),
        ).fetchone()
        if existing is None and active_count >= license_row["max_activations"]:
            raise HTTPException(status_code=409, detail="Activation limit reached.")

        db.execute(
            "INSERT OR IGNORE INTO activations (license_key, machine_hash, activated_at, challenge_nonce) VALUES (?, ?, ?, ?)",
            (request.license_key, request.machine_hash, utc_now().isoformat(), os.urandom(16).hex()),
        )
        _audit(db, request.license_key, request.machine_hash, "activate", request.email)

    token = _token_for(license_row, request.machine_hash, request.email)
    return _response("active", license_row, request.email, token)


@app.post("/validate", response_model=LicenseResponse)
def validate(request: ValidationRequest) -> LicenseResponse:
    try:
        payload = verify_token(request.token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    if payload["machine_hash"] != request.machine_hash:
        raise HTTPException(status_code=401, detail="License is bound to another machine.")

    with connect(DB_PATH) as db:
        license_row = db.execute("SELECT * FROM licenses WHERE license_key = ? AND active = 1 AND revoked = 0", (payload["license_key"],)).fetchone()
        if license_row is None:
            raise HTTPException(status_code=404, detail="License no longer active.")
        _audit(db, payload["license_key"], request.machine_hash, "validate", "online validation")
    return _response("active", license_row, payload["email"], request.token)


@app.post("/deactivate", response_model=LicenseResponse)
def deactivate(request: DeactivationRequest) -> LicenseResponse:
    payload = verify_token(request.token)
    with connect(DB_PATH) as db:
        db.execute(
            "UPDATE activations SET deactivated_at = ? WHERE license_key = ? AND machine_hash = ?",
            (utc_now().isoformat(), payload["license_key"], request.machine_hash),
        )
        _audit(db, payload["license_key"], request.machine_hash, "deactivate", "user requested")
    return LicenseResponse(
        state="deactivated",
        type=payload["type"],
        email=payload["email"],
        days_remaining=0,
        offline_until=utc_now().isoformat(),
    )


@app.get("/license-status")
def license_status() -> dict[str, str]:
    return {"status": "online", "service": "FLIFE Lite Licensing Server"}


@app.post("/admin/revoke")
def revoke(request: RevocationRequest) -> dict[str, str]:
    with connect(DB_PATH) as db:
        db.execute("UPDATE licenses SET revoked = 1 WHERE license_key = ?", (request.license_key,))
        db.execute(
            "INSERT OR REPLACE INTO revocations (license_key, reason, revoked_at) VALUES (?, ?, ?)",
            (request.license_key, request.reason, utc_now().isoformat()),
        )
        _audit(db, request.license_key, "admin", "revoke", request.reason)
    return {"state": "revoked", "license_key": request.license_key}


@app.post("/admin/transfer-machine")
def transfer_machine(request: MachineTransferRequest) -> dict[str, str]:
    with connect(DB_PATH) as db:
        db.execute(
            "UPDATE activations SET deactivated_at = ? WHERE license_key = ? AND machine_hash = ?",
            (utc_now().isoformat(), request.license_key, request.from_machine_hash),
        )
        db.execute(
            "INSERT OR IGNORE INTO activations (license_key, machine_hash, activated_at, challenge_nonce) VALUES (?, ?, ?, ?)",
            (request.license_key, request.to_machine_hash, utc_now().isoformat(), os.urandom(16).hex()),
        )
        _audit(db, request.license_key, request.from_machine_hash, "transfer_from", request.to_machine_hash)
        _audit(db, request.license_key, request.to_machine_hash, "transfer_to", request.from_machine_hash)
    return {"state": "transferred", "license_key": request.license_key}


def _token_for(license_row, machine_hash: str, email: str) -> str:
    payload = {
        "license_key": license_row["license_key"],
        "email": email,
        "type": license_row["license_type"],
        "machine_hash": machine_hash,
        "expires_at": license_row["expires_at"],
        "offline_until": offline_expiry(14),
    }
    return sign_payload(payload)


def _response(state: str, license_row, email: str, token: str) -> LicenseResponse:
    expires_at = datetime.fromisoformat(license_row["expires_at"])
    days_remaining = max(0, (expires_at - utc_now()).days)
    return LicenseResponse(
        state=state,
        type=license_row["license_type"],
        email=email,
        token=token,
        days_remaining=days_remaining,
        offline_until=offline_expiry(14),
        max_activations=license_row["max_activations"],
    )


def _audit(db, license_key: str, machine_hash: str, event: str, detail: str) -> None:
    db.execute(
        "INSERT INTO activation_audit (license_key, machine_hash, event, event_at, detail) VALUES (?, ?, ?, ?, ?)",
        (license_key, machine_hash, event, utc_now().isoformat(), detail),
    )
