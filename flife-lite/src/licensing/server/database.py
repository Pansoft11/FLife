from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS licenses (
    license_key TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    license_type TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    max_activations INTEGER NOT NULL DEFAULT 1,
    active INTEGER NOT NULL DEFAULT 1,
    revoked INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_key TEXT NOT NULL,
    machine_hash TEXT NOT NULL,
    activated_at TEXT NOT NULL,
    deactivated_at TEXT,
    challenge_nonce TEXT,
    UNIQUE(license_key, machine_hash)
);

CREATE TABLE IF NOT EXISTS activation_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_key TEXT NOT NULL,
    machine_hash TEXT NOT NULL,
    event TEXT NOT NULL,
    event_at TEXT NOT NULL,
    detail TEXT
);

CREATE TABLE IF NOT EXISTS revocations (
    license_key TEXT PRIMARY KEY,
    reason TEXT,
    revoked_at TEXT NOT NULL
);
"""


def connect(db_path: str = "flife_licenses.sqlite3") -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    _ensure_column(connection, "licenses", "revoked", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(connection, "activations", "challenge_nonce", "TEXT")
    return connection


def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
