from datetime import timedelta

from licensing.server.crypto import offline_expiry, sign_payload, utc_now, verify_token


def test_license_token_signature_roundtrip():
    payload = {
        "license_key": "FLIFE-TEST",
        "email": "test@example.com",
        "type": "trial",
        "machine_hash": "a" * 64,
        "expires_at": (utc_now() + timedelta(days=1)).isoformat(),
        "offline_until": offline_expiry(7),
    }

    token = sign_payload(payload, secret="test-secret")
    decoded = verify_token(token, secret="test-secret")

    assert decoded["license_key"] == "FLIFE-TEST"
    assert decoded["machine_hash"] == "a" * 64
