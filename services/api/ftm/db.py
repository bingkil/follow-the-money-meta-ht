"""Versioned SQLite source records. All amounts are EUR cents."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
INSERT OR IGNORE INTO schema_version VALUES (1);
INSERT OR IGNORE INTO schema_version VALUES (2);
CREATE TABLE IF NOT EXISTS customers(
 id TEXT PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL, occupation TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS accounts(
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES customers(id),
 opening_balance_cents INTEGER NOT NULL, branch_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS relationships(
 id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES customers(id),
 target_id TEXT NOT NULL REFERENCES customers(id), kind TEXT NOT NULL, source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions(
 id TEXT PRIMARY KEY, source_account TEXT NOT NULL REFERENCES accounts(id),
 target_account TEXT NOT NULL REFERENCES accounts(id), amount_cents INTEGER NOT NULL
 CHECK(amount_cents > 0), timestamp TEXT NOT NULL, purpose TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS locations(
 id TEXT PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL,
 latitude REAL NOT NULL, longitude REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS location_events(
 id TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id),
 location_id TEXT NOT NULL REFERENCES locations(id), timestamp TEXT NOT NULL,
 event_type TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS documents(
 id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES customers(id),
 title TEXT NOT NULL, content TEXT NOT NULL, effective_from TEXT NOT NULL, source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS detection_runs(
 id TEXT PRIMARY KEY, rule_version TEXT NOT NULL, parameters TEXT NOT NULL,
 window_start TEXT NOT NULL, cutoff TEXT NOT NULL, started_at TEXT NOT NULL,
 completed_at TEXT NOT NULL, matched INTEGER NOT NULL, created INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS alerts(
 id TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id),
 run_id TEXT NOT NULL REFERENCES detection_runs(id), rule_version TEXT NOT NULL,
 window_start TEXT NOT NULL, cutoff TEXT NOT NULL, score INTEGER NOT NULL,
 evidence TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'New', owner TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS cases(
 id TEXT PRIMARY KEY, alert_id TEXT NOT NULL UNIQUE REFERENCES alerts(id),
 status TEXT NOT NULL DEFAULT 'Open', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS case_notes(
 id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id),
 content TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS tx_time ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS tx_target ON transactions(target_account, timestamp);
CREATE INDEX IF NOT EXISTS tx_source ON transactions(source_account, timestamp);
CREATE TABLE IF NOT EXISTS fixture_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


@contextmanager
def connect(path: str | None = None):
    target = Path(path or os.getenv("FTM_DB_PATH", "var/ftm.sqlite3"))
    target.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(target)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        db.executescript(SCHEMA)
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
