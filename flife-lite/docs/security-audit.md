# FLIFE Lite Security Audit Notes

## Secrets

- No production signing keys or API keys are committed.
- `FLIFE_LICENSE_SECRET` must be supplied by environment variable.
- Tauri signing keys are read from environment variables during release.

## Licensing

- License tokens are HMAC signed.
- Machine fingerprints are SHA256 hashes.
- Activation audit, revocation, and machine transfer hooks are present.
- Offline activation files use explicit `.flreq` and `.flres` formats.

## Frontend

- Tauri CSP is configured to avoid unrestricted script execution.
- Static check blocks `eval`, `innerHTML`, and `dangerouslySetInnerHTML`.
- Imported engineering files remain local unless future opt-in telemetry/cloud features are enabled.
