# Follow The Money

Evidence-grounded financial investigation for the Meta hackathon. All fixture data is fictional.

## Current delivery

Foundation API, SQLite schema, seeded six-month collection-network fixture and React source-data screen. Alert detection and AI investigation are not yet implemented. No live Meta call has been verified.

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
