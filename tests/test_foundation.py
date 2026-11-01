import sqlite3

from fastapi.testclient import TestClient
from ftm.api import app
from ftm.seed import seed


def test_fixture_reproducible_and_conserves_balances(tmp_path):
    path = str(tmp_path / "data.sqlite3")
    counts = seed(path)
    with sqlite3.connect(path) as db:
        before = db.execute("SELECT * FROM transactions ORDER BY id").fetchall()
        assert not db.execute("PRAGMA foreign_key_check").fetchall()
        accounts = db.execute("SELECT id, opening_balance_cents FROM accounts").fetchall()
        balances = dict(accounts)
        for _, src, dst, amount, *_ in before:
            balances[src] -= amount
            balances[dst] += amount
            assert balances[src] >= 0
        assert sum(balances.values()) == sum(v for _, v in accounts)
        assert (
            db.execute("SELECT count(*) FROM accounts WHERE owner_id='collector'").fetchone()[0]
            == 2
        )
    assert seed(path) == counts
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT * FROM transactions ORDER BY id").fetchall() == before


def test_api_reads_persistent_fixture(tmp_path, monkeypatch):
    path = str(tmp_path / "api.sqlite3")
    monkeypatch.setenv("FTM_DB_PATH", path)
    monkeypatch.delenv("META_API_KEY", raising=False)
    client = TestClient(app)
    health = client.get("/api/health").json()
    assert health["status"] == "ok"
    assert health["database_version"] == 1
    assert health["meta_configured"] is False
    assert health["meta_verified"] is False
    assert client.get("/api/overview").json()["accounts"] == []
    expected = seed(path)
    overview = client.get("/api/overview").json()
    assert overview["counts"] == expected
    assert overview["synthetic"] is True
    assert len(overview["accounts"]) == expected["accounts"]
