# Development status

## Foundation increment — 1 November 2026

Implemented: uv backend configuration, SQLite schema version 1, health/overview APIs, deterministic May–October fixture, React source-account screen and Meta connectivity probe.

Pending Stage 0 gates: browser visual QA, graph-library interaction spike and live Meta request/tool round-trip. Model/tool calling support was checked against official docs at https://dev.meta.ai/docs/cookbook/tool-function-calling and https://dev.meta.ai/docs/cookbook/quickstart-chat-completions on 1 November 2026.

Stage 1 is partial: eight workers, three collection accounts, ownership relationships and common destination are seeded. ATM events, supporting accommodation records, ordinary scenario variants and uncertain identities remain to implement. All seed records are fictional. Fixture reset is explicit and never runs on startup.

Next increment: complete the fixture variants and location/document evidence, implement the first monitoring rule and reproduce its alert calculation before adding agents.

## Verification

- uv sync completed and uv.lock committed.
- Backend: 2 tests pass (fixture reproducibility, balances, relations and persistent API reads).
- Ruff lint and formatting pass.
- Web TypeScript check and Vite production build pass.
- TestClient emits an upstream httpx deprecation warning; tests currently pass.
- Browser visual QA and live Meta connectivity are pending. No credential has been requested or used.
- Hosting options documented in hosting.md; no infrastructure deployed.

## Monitoring increment — 1 November 2026

Implemented: additive schema v2, versioned rapid-movement rule, parameter-specific deduplication, persisted detection runs and trigger snapshots, reproducible score breakdown, queue filtering, alert inspection, assignment, case creation and persistent notes. Same monitoring service exposed through API and CLI.

Fixture: three accommodation agreements cover EUR 600 monthly contributions for workers 1, 4 and 7. Other transfers remain unexplained by these agreements. ATM balance-enquiry events supply location evidence without claiming cash withdrawal or identifying who operated the card.

Default synthetic parameters: 7-day window, at least 3 distinct sender owners and EUR 1,000 incoming, at least 80% aggregate onward turnover within 48 hours of an incoming event. Internal same-owner transfers excluded. Each qualifying outflow counted once. No exact-funds attribution or historical anomaly score is claimed. Priority is a documented provisional rule-only calculation. These thresholds are implementation choices.

Checks: 5 backend tests pass; Ruff and frontend production build pass. Browser execution initially blocked by missing Playwright Chromium binary; final browser result recorded below if available.

Remaining: automated scheduling, case audit/disposition, fixture variants and unknown external identities, full historical/network tools, live Meta agents, graph/timeline/map. Stage 2 is partial; this is an operational monitoring slice, not the complete FTM application.

Browser QA remains unverified: Chromium installation returned truncated/invalid archives. No browser-interaction pass is claimed.

## Windows developer restart

Added restart.ps1 and scripts/dev-server.ps1: checkout-scoped process cleanup, locked installs, separate server windows, next-free ports, dynamic frontend proxy and readiness checks. No data reset. Static review completed; Windows PowerShell execution is unverified in this Linux workspace.

## Deterministic evidence increment — 1 November 2026

Chris verified the application runs on Windows. Added eight evidence services, immutable saved evidence runs (schema v3), bounded graph exploration and legal-owner grouping UI. Tools expose source identifiers, time windows and coverage limits. Account grouping preserves separate corporate identity; internal transfers remain separate from external totals. Source comparisons are period totals, not a calibrated anomaly model.

Two-hop exploration from collector-a reaches six workers; it intentionally does not expose the two workers beyond the other collection account at three hops. Node and transaction limits are explicit. ATM evidence is balance-enquiry location, not cash withdrawal.

Validation: backend tests cover grouping, source documents, time cutoff, forward path ordering, snapshots, API bounds and dependent-data reset. Frontend production build passes. Browser visual QA remains pending in this environment. Live Meta requests remain pending.

Next: runtime agent adapter/orchestration and report synthesis using these tools, plus graph interaction refinement. Scheduling, audit/disposition and fixture variants remain open.
