"""Versioned SQLite source records. All amounts are EUR cents."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
INSERT OR IGNORE INTO schema_version VALUES (1);
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
