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
