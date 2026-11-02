import json
import os
import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ftm.db import connect
from ftm.investigation import collect_evidence
from ftm.monitoring import DetectionRequest, run_detection

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


# Monitoring and case endpoints share the same deterministic services as the CLI.
@app.post("/api/detection-runs")
def detect(request: DetectionRequest):
    return run_detection(request)


@app.get("/api/detection-runs")
def detection_runs():
    with connect() as db:
        return [
            dict(r)
            for r in db.execute("SELECT * FROM detection_runs ORDER BY started_at DESC LIMIT 50")
        ]


@app.get("/api/alerts")
def alerts():
    with connect() as db:
        return [
            dict(r)
            for r in db.execute("""SELECT a.id,a.account_id,a.score,a.status,a.owner,
            a.rule_version,a.window_start,a.cutoff,c.name customer
            FROM alerts a JOIN accounts ac ON ac.id=a.account_id
            JOIN customers c ON c.id=ac.owner_id ORDER BY score DESC,a.id""")
        ]


@app.get("/api/alerts/{alert_id}")
def alert_detail(alert_id: str):
    with connect() as db:
        row = db.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Alert not found")
        result = dict(row)
        result["evidence"] = json.loads(result["evidence"])
        result["customer"] = dict(
            db.execute(
                """SELECT c.* FROM customers c
            JOIN accounts a ON a.owner_id=c.id WHERE a.id=?""",
                (row["account_id"],),
            ).fetchone()
        )
        case = db.execute("SELECT * FROM cases WHERE alert_id=?", (alert_id,)).fetchone()
        result["case"] = dict(case) if case else None
        return result


class AlertUpdate(BaseModel):
    owner: str = Field(max_length=100)
    status: Literal["New", "Assigned", "Investigating", "Resolved"]


@app.patch("/api/alerts/{alert_id}")
def update_alert(alert_id: str, update: AlertUpdate):
    with connect() as db:
        if not db.execute("SELECT id FROM alerts WHERE id=?", (alert_id,)).fetchone():
            raise HTTPException(404, "Alert not found")
        db.execute(
            "UPDATE alerts SET owner=?,status=? WHERE id=?", (update.owner, update.status, alert_id)
        )
    return {"updated": True}


@app.post("/api/alerts/{alert_id}/case")
def open_case(alert_id: str):
    with connect() as db:
        if not db.execute("SELECT id FROM alerts WHERE id=?", (alert_id,)).fetchone():
            raise HTTPException(404, "Alert not found")
        db.execute(
            "INSERT OR IGNORE INTO cases (id,alert_id,created_at) VALUES (?,?,?)",
            (f"case-{alert_id}", alert_id, datetime.now(timezone.utc).isoformat()),
        )
        return dict(db.execute("SELECT * FROM cases WHERE alert_id=?", (alert_id,)).fetchone())


class NoteRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


@app.post("/api/cases/{case_id}/notes")
def add_note(case_id: str, note: NoteRequest):
    with connect() as db:
        if not db.execute("SELECT id FROM cases WHERE id=?", (case_id,)).fetchone():
            raise HTTPException(404, "Case not found")
        note_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO case_notes VALUES (?,?,?,?)",
            (note_id, case_id, note.content, datetime.now(timezone.utc).isoformat()),
        )
    return {"id": note_id}


@app.get("/api/cases/{case_id}/notes")
def notes(case_id: str):
    with connect() as db:
        if not db.execute("SELECT id FROM cases WHERE id=?", (case_id,)).fetchone():
            raise HTTPException(404, "Case not found")
        return [
            dict(r)
            for r in db.execute(
                "SELECT * FROM case_notes WHERE case_id=? ORDER BY created_at,id", (case_id,)
            )
        ]


class EvidenceRequest(BaseModel):
    max_hops: int = Field(default=2, ge=1, le=3)


@app.post("/api/alerts/{alert_id}/evidence")
def gather_evidence(alert_id: str, request: EvidenceRequest):
    try:
        return collect_evidence(alert_id, max_hops=request.max_hops)
    except LookupError:
        raise HTTPException(404, "Alert not found") from None


@app.get("/api/alerts/{alert_id}/evidence")
def evidence_history(alert_id: str):
    with connect() as db:
        if not db.execute("SELECT id FROM alerts WHERE id=?", (alert_id,)).fetchone():
            raise HTTPException(404, "Alert not found")
        return [
            json.loads(r["snapshot"])
            for r in db.execute(
                "SELECT snapshot FROM evidence_runs WHERE alert_id=? "
                "ORDER BY created_at DESC LIMIT 10",
                (alert_id,),
            )
        ]
