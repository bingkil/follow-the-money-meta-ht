from datetime import datetime, timezone

from fastapi.testclient import TestClient
from ftm.api import app
from ftm.db import connect
from ftm.monitoring import DetectionRequest, evaluate, run_detection
from ftm.seed import seed


def request(**kwargs):
    return DetectionRequest(cutoff=datetime(2026, 11, 1, tzinfo=timezone.utc), **kwargs)


def test_detection_snapshot_deduplication_and_rule_parameters(tmp_path):
    path = str(tmp_path / "rules.db")
    seed(path)
    first = run_detection(request(), path)
    assert first["created"] == first["matched"] == 2
    again = run_detection(request(), path)
    assert again["matched"] == 2 and again["created"] == 0
    assert run_detection(request(min_senders=2), path)["created"] == 3
    with connect(path) as db:
        result = evaluate(db, "collector-a", request())
        assert result["incoming_cents"] == 180000
        assert result["onward_cents"] == 162000
        assert result["distinct_sender_owners"] == 3
        assert result["score"] == sum(result["score_components"].values())
        assert len({t["id"] for t in result["transactions"]}) == 4
        # Reseeding safely clears dependent cases, alerts and runs.
    seed(path)
    with connect(path) as db:
        assert db.execute("SELECT count(*) FROM alerts").fetchone()[0] == 0


def test_internal_transfers_and_preceding_outflows_are_excluded(tmp_path):
    path = str(tmp_path / "edge.db")
    seed(path)
    with connect(path) as db:
        db.execute("DELETE FROM transactions")
        db.executemany(
            "INSERT INTO transactions VALUES (?,?,?,?,?,?)",
            [
                (
                    "internal",
                    "collector-b",
                    "collector-a",
                    999999,
                    "2026-10-26T10:00:00+00:00",
                    "Internal",
                ),
                (
                    "before",
                    "collector-a",
                    "destination-a",
                    500000,
                    "2026-10-25T10:00:00+00:00",
                    "Transfer",
                ),
                (
                    "incoming",
                    "worker1-a",
                    "collector-a",
                    100000,
                    "2026-10-26T10:00:00+00:00",
                    "Transfer",
                ),
                (
                    "too-late",
                    "collector-a",
                    "destination-a",
                    100000,
                    "2026-10-29T10:00:00+00:00",
                    "Transfer",
                ),
            ],
        )
        result = evaluate(db, "collector-a", request())
        assert result["incoming_cents"] == 100000
        assert result["distinct_sender_owners"] == 1
        assert result["onward_cents"] == 0
        assert result["matched"] is False


def test_case_persistence_and_input_validation(tmp_path, monkeypatch):
    path = str(tmp_path / "case.db")
    monkeypatch.setenv("FTM_DB_PATH", path)
    seed(path)
    client = TestClient(app)
    assert client.post("/api/detection-runs", json={"cutoff": "2026-11-01"}).status_code == 422
    assert (
        client.post("/api/detection-runs", json={"cutoff": "2026-11-01T00:00:00Z"}).status_code
        == 200
    )
    alert = client.get("/api/alerts").json()[0]
    detail = client.get("/api/alerts/" + alert["id"]).json()
    assert detail["evidence"]["matched"]
    case = client.post("/api/alerts/" + alert["id"] + "/case").json()
    assert client.post("/api/alerts/" + alert["id"] + "/case").json() == case
    url = "/api/cases/" + case["id"] + "/notes"
    assert client.post(url, json={"content": "Check accommodation evidence"}).status_code == 200
    assert client.get(url).json()[0]["content"] == "Check accommodation evidence"
    assert (
        client.patch(
            "/api/alerts/" + alert["id"], json={"owner": "Chris", "status": "Assigned"}
        ).status_code
        == 200
    )
    assert client.get("/api/alerts/" + alert["id"]).json()["owner"] == "Chris"
    assert client.get("/api/alerts/unknown").status_code == 404
