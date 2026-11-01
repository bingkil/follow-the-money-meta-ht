import os

from fastapi import FastAPI

from ftm.db import connect

app = FastAPI(title="Follow The Money", version="0.1.0")


@app.get("/api/health")
def health():
    with connect() as db:
        version = db.execute("SELECT max(version) FROM schema_version").fetchone()[0]
    return {
        "status": "ok",
        "database_version": version,
        "meta_configured": bool(os.getenv("META_API_KEY")),
        "meta_verified": False,
    }


@app.get("/api/overview")
def overview():
    with connect() as db:
        counts = {
            table: db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in ("customers", "accounts", "transactions")
        }
        accounts = [
            dict(row)
            for row in db.execute("""
            SELECT a.id, c.name owner, c.kind, a.branch_id,
            a.opening_balance_cents +
              coalesce((SELECT sum(amount_cents) FROM transactions WHERE target_account=a.id),0)-
              coalesce((SELECT sum(amount_cents) FROM transactions WHERE source_account=a.id),0)
              AS balance_cents
            FROM accounts a JOIN customers c ON c.id=a.owner_id ORDER BY c.name, a.id
        """)
        ]
    return {"counts": counts, "accounts": accounts, "synthetic": True}
