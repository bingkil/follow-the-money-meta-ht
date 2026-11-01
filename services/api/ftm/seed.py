"""Explicit, atomic fixture reset. Never called on application startup."""

import argparse
import random
from datetime import datetime, timezone

from ftm.db import connect


def seed(path: str | None = None, seed_value: int = 42):
    rng = random.Random(seed_value)
    with connect(path) as db:
        for table in ("transactions", "relationships", "accounts", "customers", "fixture_metadata"):
            db.execute(f"DELETE FROM {table}")
        people = [
            ("staffing", "Meridian Workforce Services", "business", "Staffing"),
            ("collector", "Alex Mercer", "person", "Salaried employee"),
            ("collection_co", "Harbour Services", "business", "Services"),
            ("destination", "Meridian Accommodation Services", "business", "Accommodation"),
            ("director", "Jordan Vale", "person", "Company director"),
            ("merchant", "Everyday Retail", "business", "Retail"),
        ] + [(f"worker{i}", f"Demo Worker {i}", "person", "Temporary worker") for i in range(1, 9)]
        db.executemany("INSERT INTO customers VALUES (?,?,?,?)", people)
        accounts = [
            (p[0] + "-a", p[0], 0 if p[0].startswith("worker") else 1000000, "branch-central")
            for p in people
        ]
        accounts += [("collector-b", "collector", 0, "branch-central")]
        accounts = [(a, o, 100000000 if o == "staffing" else b, br) for a, o, b, br in accounts]
        db.executemany("INSERT INTO accounts VALUES (?,?,?,?)", accounts)
        db.executemany(
            "INSERT INTO relationships VALUES (?,?,?,?,?)",
            [
                ("rel1", "collector", "collection_co", "owns", "synthetic KYC extract"),
                ("rel2", "director", "staffing", "director", "synthetic company extract"),
                ("rel3", "director", "destination", "owns", "synthetic company extract"),
            ],
        )
        txs = []

        def add(src, dst, amount, month, day, purpose):
            ts = datetime(2026, month, day, 10, tzinfo=timezone.utc).isoformat()
            txs.append((f"tx-{len(txs) + 1:05}", src, dst, amount, ts, purpose))

        collectors = ["collector-a", "collector-b", "collection_co-a"]
        for month in range(5, 11):
            for i in range(1, 9):
                worker = f"worker{i}-a"
                add("staffing-a", worker, 180000, month, 25, "Payroll")
                amount = rng.randrange(55000, 85000, 1000)
                add(worker, collectors[(i - 1) % 3], amount, month, 26, "Transfer")
                add(
                    worker,
                    "merchant-a",
                    rng.randrange(15000, 25000, 1000),
                    month,
                    27,
                    "Household purchases",
                )
            for account in collectors:
                received = sum(t[3] for t in txs if t[2] == account and t[4][5:7] == f"{month:02}")
                add(account, "destination-a", received * 9 // 10, month, 27, "Transfer")
        db.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?)", txs)
        db.execute("INSERT INTO fixture_metadata VALUES ('seed', ?)", (str(seed_value),))
        return {"customers": len(people), "accounts": len(accounts), "transactions": len(txs)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace local data with synthetic FTM fixtures")
    parser.add_argument("--reset", action="store_true", required=True)
    args = parser.parse_args()
    print(seed())
