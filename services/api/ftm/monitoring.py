"""Aggregate rapid-movement rule. No claim of exact fund attribution."""

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field, model_validator

from ftm.db import connect

RULE_VERSION = "rapid-movement-v1"


class DetectionRequest(BaseModel):
    cutoff: datetime
    lookback_days: int = Field(default=7, ge=1, le=31)
    min_senders: int = Field(default=3, ge=2, le=100)
    min_incoming_cents: int = Field(default=100000, ge=1)
    max_hours: int = Field(default=48, ge=1, le=168)
    min_outflow_percent: int = Field(default=80, ge=1, le=100)

    @model_validator(mode="after")
    def aware_time(self):
        if self.cutoff.tzinfo is None:
            raise ValueError("cutoff requires a timezone")
        return self


def evaluate(db, account_id, request):
    end = request.cutoff.astimezone(timezone.utc)
    start = end - timedelta(days=request.lookback_days)
    # Internal transfers between accounts with the same legal owner are excluded.
    rows = [
        dict(r)
        for r in db.execute(
            """
        SELECT t.*, s.owner_id source_owner, d.owner_id target_owner
        FROM transactions t JOIN accounts s ON s.id=t.source_account
        JOIN accounts d ON d.id=t.target_account
        WHERE (source_account=? OR target_account=?) AND timestamp>=? AND timestamp<?
        AND s.owner_id != d.owner_id ORDER BY timestamp, t.id
        """,
            (account_id, account_id, start.isoformat(), end.isoformat()),
        )
    ]
    incoming = [r for r in rows if r["target_account"] == account_id]
    senders = len({r["source_owner"] for r in incoming})
    total = sum(r["amount_cents"] for r in incoming)
    # Count each qualifying outflow once, even if close to several incoming payments.
    onward = [
        r
        for r in rows
        if r["source_account"] == account_id
        and any(
            timedelta(0)
            <= datetime.fromisoformat(r["timestamp"]) - datetime.fromisoformat(i["timestamp"])
            <= timedelta(hours=request.max_hours)
            for i in incoming
        )
    ]
    outgoing = sum(r["amount_cents"] for r in onward)
    matched = (
        senders >= request.min_senders
        and total >= request.min_incoming_cents
        and outgoing * 100 >= total * request.min_outflow_percent
    )
    components = {
        "rule_base": 50,
        "sender_threshold_excess": min(15, max(0, senders - request.min_senders) * 5),
        "volume_threshold_excess": min(
            20, max(0, total - request.min_incoming_cents) * 10 // request.min_incoming_cents
        ),
        "outflow_threshold_excess": min(
            15, max(0, outgoing * 100 // max(total, 1) - request.min_outflow_percent)
        ),
    }
    return {
        "matched": matched,
        "incoming_cents": total,
        "onward_cents": outgoing,
        "distinct_sender_owners": senders,
        "score": min(100, sum(components.values())),
        "score_components": components,
        "transactions": incoming + onward,
        "parameters": request.model_dump(mode="json"),
        "limitation": "Aggregate turnover, not attribution of specific incoming funds. "
        "Opening balances and other funds may finance outflows. "
        "Internal same-owner transfers excluded. "
        "All fixture transactions are posted EUR transfers.",
    }


def run_detection(request, path=None):
    now = datetime.now(timezone.utc).isoformat()
    cutoff = request.cutoff.astimezone(timezone.utc)
    start = cutoff - timedelta(days=request.lookback_days)
    params = request.model_dump(mode="json")
    params["cutoff"] = cutoff.isoformat()
    canonical = json.dumps(params, sort_keys=True)
    run_id = str(uuid.uuid4())
    with connect(path) as db:
        # Serialize concurrent writers before computing the new-alert count.
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "INSERT INTO detection_runs VALUES (?,?,?,?,?,?,?,?,?)",
            (
                run_id,
                RULE_VERSION,
                canonical,
                start.isoformat(),
                cutoff.isoformat(),
                now,
                now,
                0,
                0,
            ),
        )
        matched = created = 0
        for account in db.execute("SELECT id FROM accounts ORDER BY id").fetchall():
            evidence = evaluate(db, account["id"], request)
            if not evidence["matched"]:
                continue
            matched += 1
            identity = hashlib.sha256(
                f"{RULE_VERSION}:{account['id']}:{canonical}".encode()
            ).hexdigest()[:24]
            changed = db.execute(
                """INSERT OR IGNORE INTO alerts
                (id,account_id,run_id,rule_version,window_start,cutoff,score,evidence)
                VALUES (?,?,?,?,?,?,?,?)""",
                (
                    identity,
                    account["id"],
                    run_id,
                    RULE_VERSION,
                    start.isoformat(),
                    cutoff.isoformat(),
                    evidence["score"],
                    json.dumps(evidence),
                ),
            ).rowcount
            created += changed
        db.execute(
            "UPDATE detection_runs SET matched=?, created=?, completed_at=? WHERE id=?",
            (matched, created, datetime.now(timezone.utc).isoformat(), run_id),
        )
    return {"run_id": run_id, "matched": matched, "created": created}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the same monitoring service used by the API")
    parser.add_argument("--cutoff", required=True, help="Timezone-aware ISO timestamp; exclusive")
    args = parser.parse_args()
    print(json.dumps(run_detection(DetectionRequest(cutoff=args.cutoff))))
