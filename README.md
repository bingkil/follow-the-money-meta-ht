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

Set `META_API_KEY` in `.env`, then run `uv run --env-file .env python scripts/meta_probe.py`. This explicitly makes a real API request. Keys remain server-side. The probe tests connectivity only. `scripts/meta_tool_probe.py` runs the same way and verifies one tool-call round-trip.

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

## Windows restart

From PowerShell in the repository root:

```powershell
.\restart.ps1 -OpenBrowser
```

If the local execution policy blocks it, run this single invocation:

```powershell
powershell -ExecutionPolicy Bypass -File .\restart.ps1 -OpenBrowser
```

The script stops recognised FTM server process trees belonging to this checkout, starts backend/frontend in separate windows, installs locked dependencies, and waits for API, frontend and proxy readiness. It leaves unrelated servers running and selects the next free ports starting at 8000 (backend) and 5173 (frontend). The frontend proxy uses the selected backend port. Ports are checked immediately before launch; if another process takes one during startup, retry the script. It can be invoked from any directory by its full path. Use `-TimeoutSeconds 180` for a slow first dependency install. It preserves the database and does not seed/reset data. Windows, uv and npm are required.

## Evidence workspace

Inspect an alert, then select **Collect evidence** below its details. The deterministic tools retrieve the stored trigger, customer context, 30-day comparisons, a bounded two-hop account network, legal-owner totals, branch/ATM context, supporting documents and forward observed paths. Select graph nodes to filter source transfers; switch to legal-owner grouping to see common ownership. **Load saved evidence** reopens the latest stored snapshot.

This is deterministic investigation support; Meta agents are not integrated yet. A two-hop view is deliberately incomplete: an intermediate account may be visible before all of its senders are. The API accepts up to three hops. Group totals cover displayed accounts/edges, and transfer paths do not attribute specific funds. Existing databases upgrade additively to schema v3 without resetting cases. New fixture documents/events require explicitly reseeding if your database predates them.
