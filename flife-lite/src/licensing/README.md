# FLIFE Lite Licensing

The licensing service is a small FastAPI application with SQLite storage and a PostgreSQL-ready repository boundary.

Endpoints:

- `POST /activate`
- `POST /validate`
- `POST /deactivate`
- `GET /license-status`

Set `FLIFE_LICENSE_SECRET` in production. The default development secret is intentionally unsafe and should never ship.
