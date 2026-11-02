"""Deterministic evidence collection. This module makes no AI or criminality claims."""

import json
import uuid
from collections import deque
from datetime import datetime, timedelta, timezone

from ftm.db import connect


def collect_evidence(alert_id: str, path=None, max_hops=2):
    if not 1 <= max_hops <= 3:
        raise ValueError("max_hops must be 1–3")
    with connect(path) as db:
        alert = db.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
        if alert is None:
            raise LookupError("Alert not found")
        cutoff = datetime.fromisoformat(alert["cutoff"])
        start = cutoff - timedelta(days=180)
        customers = {r["id"]: dict(r) for r in db.execute("SELECT * FROM customers")}
        accounts = {r["id"]: dict(r) for r in db.execute("SELECT * FROM accounts")}
        rows = [
            dict(r)
            for r in db.execute(
                """SELECT * FROM transactions
            WHERE timestamp>=? AND timestamp<? ORDER BY timestamp,id LIMIT 2001""",
                (start.isoformat(), cutoff.isoformat()),
            )
        ]
        truncated = len(rows) > 2000
        rows = rows[:2000]
        relationships = [dict(r) for r in db.execute("SELECT * FROM relationships ORDER BY id")]
        tools = []

        def record(name, result, sources, limitations=()):
            envelope = {
                "execution_id": str(uuid.uuid4()),
                "tool": name,
                "parameters": {"alert_id": alert_id, "max_hops": max_hops},
                "window_start": start.isoformat(),
                "cutoff": cutoff.isoformat(),
                "status": "partial" if truncated else "completed",
                "source_ids": sorted(set(sources)),
                "result": result,
                "limitations": list(limitations)
                + (
                    ["Transaction coverage truncated to earliest 2000 records."]
                    if truncated
                    else []
                ),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }
            tools.append(envelope)
            return result

        root = alert["account_id"]
        owner = accounts[root]["owner_id"]
        record(
            "reconstruct_alert",
            json.loads(alert["evidence"]),
            ["alert:" + alert_id],
            ["Stored detection snapshot; original score and parameters preserved."],
        )
        record(
            "customer_context",
            {
                "customer": customers[owner],
                "accounts": [a for a in accounts.values() if a["owner_id"] == owner],
                "relationships": [
                    r for r in relationships if owner in (r["source_id"], r["target_id"])
                ],
            },
            ["customer:" + owner, "account:" + root],
            ["KYC and ownership are current fixture records; historical validity is unavailable."],
        )

        # Bounded account-neighbour expansion through observed transfers and documented ownership.
        adjacency = {a: set() for a in accounts}
        for tx in rows:
            adjacency[tx["source_account"]].add(tx["target_account"])
            adjacency[tx["target_account"]].add(tx["source_account"])
        for a in accounts.values():
            for b in accounts.values():
                if a["owner_id"] == b["owner_id"] and a["id"] != b["id"]:
                    adjacency[a["id"]].add(b["id"])
        visited = {root}
        queue = deque([(root, 0)])
        while queue:
            node, depth = queue.popleft()
            if depth == max_hops:
                continue
            for neighbour in sorted(adjacency[node]):
                if neighbour not in visited and len(visited) < 50:
                    visited.add(neighbour)
                    queue.append((neighbour, depth + 1))
        scoped = [
            t for t in rows if t["source_account"] in visited and t["target_account"] in visited
        ]
        owners = {accounts[a]["owner_id"] for a in visited}
        links = [r for r in relationships if r["source_id"] in owners or r["target_id"] in owners]
        linked_people = owners | {r["source_id"] for r in links} | {r["target_id"] for r in links}
        graph = record(
            "expand_network",
            {
                "root": root,
                "accounts": [accounts[a] for a in sorted(visited)],
                "customers": [customers[c] for c in sorted(linked_people)],
                "transactions": scoped,
                "relationships": links,
                "depth": max_hops,
                "node_limit": 50,
            },
            ["transaction:" + t["id"] for t in scoped] + ["relationship:" + r["id"] for r in links],
            [
                "Known internal accounts only. No external-bank visibility.",
                "Traversal includes incoming/outgoing links; "
                "connectivity does not establish control.",
                "At most 50 accounts. Documented ownership links do not merge legal entities.",
            ],
        )

        def totals(begin, end):
            txs = [t for t in rows if begin <= datetime.fromisoformat(t["timestamp"]) < end]
            incoming = [t for t in txs if t["target_account"] == root]
            outgoing = [t for t in txs if t["source_account"] == root]
            return {
                "incoming_cents": sum(t["amount_cents"] for t in incoming),
                "outgoing_cents": sum(t["amount_cents"] for t in outgoing),
                "incoming_count": len(incoming),
                "outgoing_count": len(outgoing),
                "counterparties": len(
                    {t["source_account"] for t in incoming}
                    | {t["target_account"] for t in outgoing}
                ),
            }

        current = totals(cutoff - timedelta(days=30), cutoff)
        previous = totals(cutoff - timedelta(days=60), cutoff - timedelta(days=30))
        record(
            "compare_behaviour",
            {
                "current_30_days": current,
                "previous_30_days": previous,
                "incoming_change_cents": current["incoming_cents"] - previous["incoming_cents"],
                "baseline_status": "observed_period_totals_only",
            },
            [
                "transaction:" + t["id"]
                for t in rows
                if root in (t["source_account"], t["target_account"])
            ],
            [
                "Calendar coverage and seasonality are not inferred from missing transactions.",
                "A period difference is not a calibrated anomaly score.",
            ],
        )

        groups = []
        for customer in sorted(owners):
            members = {a for a in visited if accounts[a]["owner_id"] == customer}
            incoming = [
                t
                for t in scoped
                if t["target_account"] in members and t["source_account"] not in members
            ]
            outgoing = [
                t
                for t in scoped
                if t["source_account"] in members and t["target_account"] not in members
            ]
            internal = [
                t
                for t in scoped
                if t["source_account"] in members and t["target_account"] in members
            ]
            groups.append(
                {
                    "owner_id": customer,
                    "account_ids": sorted(members),
                    "incoming_cents": sum(t["amount_cents"] for t in incoming),
                    "outgoing_cents": sum(t["amount_cents"] for t in outgoing),
                    "internal_cents": sum(t["amount_cents"] for t in internal),
                }
            )
        record(
            "aggregate_entity_flows",
            groups,
            ["transaction:" + t["id"] for t in scoped] + ["account:" + a for a in visited],
            [
                "Totals cover only displayed accounts and observed in-scope edges.",
                "Company accounts stay with their legal owner, not the shareholder.",
            ],
        )

        events = [
            dict(r)
            for r in db.execute(
                """SELECT e.*, l.name, l.latitude, l.longitude
            FROM location_events e JOIN locations l ON l.id=e.location_id
            WHERE timestamp>=? AND timestamp<? ORDER BY timestamp,id""",
                (start.isoformat(), cutoff.isoformat()),
            )
            if r["account_id"] in visited
        ]
        branches = {}
        for a in visited:
            branches.setdefault(accounts[a]["branch_id"], []).append(a)
        record(
            "shared_locations",
            {"events": events, "home_branch_groups": branches},
            ["location_event:" + e["id"] for e in events] + ["account:" + a for a in visited],
            [
                "Home branch is not transaction location. Balance enquiries are not withdrawals.",
                "Location records do not identify the person operating the account.",
            ],
        )
        documents = [
            dict(r)
            for r in db.execute(
                "SELECT * FROM documents WHERE effective_from<? ORDER BY id",
                (cutoff.date().isoformat(),),
            )
            if r["customer_id"] in owners
        ]
        record(
            "retrieve_documents",
            documents,
            ["document:" + d["id"] for d in documents],
            [
                "Missing documents are information gaps, "
                "not proof that an arrangement does not exist."
            ],
        )

        # Forward, time-ordered observed paths. This is not fungible-funds attribution.
        paths = []
        frontier = [(root, start, [], {root})]
        while frontier and len(paths) < 100:
            node, after, trail, seen = frontier.pop(0)
            for tx in rows:
                when = datetime.fromisoformat(tx["timestamp"])
                if (
                    tx["source_account"] == node
                    and when >= after
                    and tx["target_account"] not in seen
                ):
                    next_trail = trail + [tx["id"]]
                    paths.append(next_trail)
                    if len(paths) >= 100:
                        break
                    if len(next_trail) < max_hops:
                        frontier.append(
                            (tx["target_account"], when, next_trail, seen | {tx["target_account"]})
                        )
        record(
            "trace_onward_activity",
            {"paths": paths, "limit_reached": len(paths) == 100},
            ["transaction:" + t for trail in paths for t in trail],
            [
                "At most 100 observed forward paths; no cycles. Equal timestamps may qualify.",
                "Path amounts are not attributable sums; balances may finance later payments.",
            ],
        )

        run_id = str(uuid.uuid4())
        response = {
            "id": run_id,
            "alert_id": alert_id,
            "mode": "deterministic_evidence",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tools": tools,
            "graph": graph,
        }
        db.execute(
            "INSERT INTO evidence_runs VALUES (?,?,?,?)",
            (run_id, alert_id, response["created_at"], json.dumps(response)),
        )
        return response
