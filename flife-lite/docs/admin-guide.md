# FLIFE Lite Admin Guide

## License Types

Supported license types are trial, monthly, yearly, perpetual, and enterprise. SQLite is used for the MVP server, with a schema that can be moved to PostgreSQL.

## Environment Variables

- `FLIFE_LICENSE_SECRET`: HMAC signing secret for license tokens.
- `FLIFE_LICENSE_DB`: SQLite database path. Defaults to `%LOCALAPPDATA%/FLIFE/server/flife_licenses.sqlite3` on Windows.
- `FLIFE_LICENSE_SERVER`: Desktop client activation server URL.

## Operational Controls

- Rotate secrets by issuing new activation tokens.
- Use `max_activations` to control machine count.
- Store only SHA256 machine fingerprints.
- Keep raw hardware identifiers on the client only long enough to hash them.

## Enterprise Roadmap

- PostgreSQL backend.
- Admin dashboard for key issuance and revocation.
- Floating license leases.
- SSO-bound license grants.
- Signed update channel.
