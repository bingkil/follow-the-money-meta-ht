# Follow The Money

Evidence-grounded financial investigation for the Meta hackathon. All fixture data is fictional.

## Current delivery

FastAPI/SQLite backend, seeded six-month collection-network fixture, rule-generated alert queue, trigger inspection and basic persistent cases/notes. AI investigation is upcoming. No live Meta call has been verified.

## Prerequisites

Python 3.11+, uv, Node 22.12+ and npm.

## Run

From the repository root:

```sh
uv sync --locked
PYTHONPATH=services/api uv run --env-file .env python -m ftm.seed --reset
```

On Windows omit the inline `PYTHONPATH=services/api` above and set `PYTHONPATH=services/api` before the Python commands (PowerShell: `$env:PYTHONPATH="services/api"`; Bash: `export PYTHONPATH=services/api`). Copy `.env.example` to `.env` first. The reset command replaces the local fixture database.

```sh
uv run --env-file .env uvicorn ftm.api:app --reload
```

In another terminal:

```sh
cd apps/web
npm ci
npm run dev
```

Open the URL printed by Vite. The API binds to loopback by default. This is a local development application without authentication; do not expose it with real customer data.

## Checks

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
cd apps/web
npm run build
```

## Meta

Set `META_API_KEY` in `.env`, then run `uv run --env-file .env python scripts/meta_probe.py`. This explicitly makes a real API request. Keys remain server-side. The probe tests connectivity only; the agent/tool round-trip remains pending.

## Design

- [Product design](docs/design.md)
- [Implementation stages](docs/implementation.md)
- [Development status](docs/status.md)

## Monitoring

After seeding, use Run detection in the UI with the default exclusive cutoff 2026-11-01 UTC. The default 7-day rule produces two synthetic alerts. Re-running retains existing alerts. The same service can be called from the CLI:

```sh
PYTHONPATH=services/api uv run --env-file .env python -m ftm.monitoring --cutoff 2026-11-01T00:00:00Z
```

Scheduling is not yet configured. The score is a provisional uncalibrated rule priority, not a probability. Follow The Money is visibly disabled until agent integration.
