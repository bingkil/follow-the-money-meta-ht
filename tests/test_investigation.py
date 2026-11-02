from datetime import datetime, timezone

from fastapi.testclient import TestClient
from ftm.api import app
from ftm.db import connect
from ftm.investigation import collect_evidence
from ftm.monitoring import DetectionRequest, run_detection
from ftm.seed import seed


def setup(path):
    seed(path)
    run_detection(DetectionRequest(cutoff=datetime(2026, 11, 1, tzinfo=timezone.utc)), path)
    with connect(path) as db:
        return db.execute("SELECT id FROM alerts WHERE account_id='collector-a'").fetchone()[0]


def test_source_evidence_grouping_and_documents(tmp_path):
    path = str(tmp_path / "tools.db")
    alert_id = setup(path)
    run = collect_evidence(alert_id, path)
    tools = {t["tool"]: t for t in run["tools"]}
    assert len(tools) == 8
    accounts = {a["id"]: a["owner_id"] for a in run["graph"]["accounts"]}
    assert accounts["collector-a"] == accounts["collector-b"] == "collector"
    assert accounts["collection_co-a"] == "collection_co"
    groups = tools["aggregate_entity_flows"]["result"]
    collector = next(g for g in groups if g["owner_id"] == "collector")
    expected = sum(
        t["amount_cents"]
        for t in run["graph"]["transactions"]
        if t["target_account"] in collector["account_ids"]
        and t["source_account"] not in collector["account_ids"]
    )
    assert collector["incoming_cents"] == expected
    assert len(tools["retrieve_documents"]["result"]) == 3
    assert len(tools["shared_locations"]["result"]["events"]) == 36
    for e in tools["shared_locations"]["result"]["events"]:
        assert e["event_type"] == "balance enquiry"
    assert all(t["source_ids"] for t in run["tools"])
    # Saved source records remain immutable even when underlying records change.
    with connect(path) as db:
        db.execute("UPDATE documents SET content='Changed' WHERE id='agreement-1'")
        saved = db.execute(
            "SELECT snapshot FROM evidence_runs WHERE id=?", (run["id"],)
        ).fetchone()[0]
        assert "Monthly accommodation contribution" in saved


def test_time_bounds_paths_and_internal_aggregation(tmp_path):
    path = str(tmp_path / "bounds.db")
    alert_id = setup(path)
    with connect(path) as db:
        db.execute(
            "INSERT INTO transactions VALUES (?,?,?,?,?,?)",
            (
                "internal-test",
                "collector-a",
                "collector-b",
                12000,
                "2026-10-28T10:00:00+00:00",
                "Internal",
            ),
        )
        db.execute(
            "INSERT INTO transactions VALUES (?,?,?,?,?,?)",
            (
                "future-test",
                "collector-a",
                "merchant-a",
                99999,
                "2026-11-01T00:00:00+00:00",
                "Future",
            ),
        )
    result = collect_evidence(alert_id, path)
    tools = {t["tool"]: t["result"] for t in result["tools"]}
    assert "future-test" not in {t["id"] for t in result["graph"]["transactions"]}
    group = next(g for g in tools["aggregate_entity_flows"] if g["owner_id"] == "collector")
    assert group["internal_cents"] == 12000
    with connect(path) as db:
        timestamps = {r["id"]: r["timestamp"] for r in db.execute("SELECT * FROM transactions")}
    for trail in tools["trace_onward_activity"]["paths"]:
        assert 1 <= len(trail) <= 2
        dates = [timestamps[t] for t in trail]
        assert dates == sorted(dates)


def test_api_snapshots_validation_and_reset(tmp_path, monkeypatch):
    path = str(tmp_path / "api.db")
    monkeypatch.setenv("FTM_DB_PATH", path)
    alert_id = setup(path)
    client = TestClient(app)
    url = "/api/alerts/" + alert_id + "/evidence"
    assert client.post(url, json={"max_hops": 9}).status_code == 422
    assert client.post("/api/alerts/unknown/evidence", json={}).status_code == 404
    result = client.post(url, json={})
    assert result.status_code == 200
    assert client.get(url).json()[0] == result.json()
    seed(path)
    with connect(path) as db:
        assert db.execute("SELECT count(*) FROM evidence_runs").fetchone()[0] == 0
        assert not db.execute("PRAGMA foreign_key_check").fetchall()
