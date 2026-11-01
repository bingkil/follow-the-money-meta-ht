# Follow The Money — Implementation Plan
## v0.1 · 1 November 2026

**Owner:** Chris Prakoso  
**Status:** Proposed development plan; implementation has not started.  
**Baseline:** Follow The Money Product and MVP Design v0.2 (the existing filename remains Follow_The_Money_Design_v0.1.md).  
**Goal:** Deliver a functioning, visually compelling investigation from a generated AML alert, using Meta AI at runtime and traceable deterministic evidence.

## 1. Delivery approach

Build one complete investigation path before adding breadth:

Synthetic source data → scheduled rule execution → prioritised alert → Follow The Money investigation → graph and evidence exploration → human-reviewed case decision.

The scenario includes salary payments to workers, several collection accounts, documented ownership connections and a common onward beneficiary. Branch and ATM records provide structured context. Personal teller observations and victim disclosures are excluded. Possible mule activity and labour exploitation remain hypotheses to test alongside ordinary explanations.

The same fixture drives the monitoring engine, tools, graph and reports. The model is never given the hidden scenario answer.

## 2. Who implements it

Implementation can be performed in this Codex-enabled workspace. A separate handoff to Codex is not necessary.

The assistant can scaffold the repository, build frontend/backend code, generate synthetic fixtures, integrate an available Meta API, write meaningful tests, debug failures and prepare a runnable application and demo documentation.

Chris provides domain review, confirms any consequential scope decisions, and supplies access that cannot be inferred or created automatically: a usable Meta API credential, a repository destination if desired, and a deployment target/account when needed. Credentials belong in a secret mechanism or local environment, never in the document or committed source.

A live Meta integration and deployment can only be claimed after actual verification. Missing credentials need not block fixture, tool, UI or explicitly labelled development-stub work. Model-generated claims must not be simulated and presented as live AI results.

Code should be maintained in a Git repository. If a separate coding session is used later, the repository, this plan, design baseline, commands, test status and outstanding issues form the handoff.

## 3. Proposed architecture

| Layer | Proposed implementation | Responsibility |
|---|---|---|
| Browser | React + TypeScript, Vite | Queue, investigation workspace, case review |
| Graph UI | Select after a small interaction spike | Directed edges, expansion, selection, grouping, stable layout |
| Map UI | Select after checking tile/service requirements | Branch/ATM event locations |
| API | Python + FastAPI | Typed endpoints, validation and data access |
| Storage | SQLite initially | Source records, alerts, cases, findings and audit trail |
| Analytics | SQL and NetworkX | Rule calculations, bounded graph traversal and history comparisons |
| Execution | One lightweight durable worker | Scheduled monitoring and queued investigations |
| Progress | Server-sent events | Persisted investigation progress and incremental findings |
| AI | Server-side Meta adapter | Tool selection, interpretation and structured report synthesis |

This is a proposed stack, not a dependency compatibility assessment. Stage 0 verifies official documentation, versions, licences and Meta capabilities before locking packages.

Use relational data as the source of truth. Build bounded graph projections for investigations. A dedicated graph database is deferred. A single-worker SQLite deployment is adequate for the demo scope; production concurrency and scaling are separate work.

### Execution boundaries

- Deterministic code computes amounts, scores, graph paths, statistics and aggregation.
- Agents select permitted tools, interpret their outputs and test competing explanations.
- The frontend receives evidence-backed graph changes, not arbitrary executable model output.
- The investigator owns case disposition.
- Tool results, findings and progress events persist before they are displayed.

### Proposed repository layout

- apps/web/ — React application and frontend tests.
- services/api/ — API, storage, worker, monitoring, tools and agents.
- data/synthetic/ — reproducible generator and scenario configuration.
- tests/ — integration and scenario evaluation.
- docs/ — design, implementation plan, runbook and demo script.
- scripts/ — setup, seed, reset and verification commands.

Keep hidden fixture labels outside application-accessible data and agent retrieval.

## 4. Stage overview

| Stage | Deliverable | Completion gate |
|---|---|---|
| 0. Foundation and feasibility | Runnable skeleton and verified integration assumptions | Browser calls API; database opens; Meta capability probe completed or blocker recorded |
| 1. Scenario and data | Reproducible synthetic dataset | Ledger, ownership and time relationships validate |
| 2. Monitoring and case foundation | Real rule-generated alert queue | Reproducible scores, no duplicate alerts, persistent cases |
| 3. Investigation tools | Deterministic reconstruction and exploration APIs | Expected evidence discovered without an LLM |
| 4. Runtime agents | Meta-assisted preliminary investigation | Real tool calls, grounded findings, explicit partial failures |
| 5. Visual investigation | Linked graph, timeline and location views | Findings and interactions use the same evidence |
| 6. Review and reporting | Editable investigation brief and case decisions | Decisions, evidence and versions persist |
| 7. Validation and demo | Reproducible application and rehearsed demo | End-to-end checks pass; live integration limitations documented |

Stages are dependency milestones, not guaranteed time estimates. Record actual latency and effort early, then cut secondary features if needed.

## 5. Stage 0 — Foundation and feasibility

### Work

1. Create the Git project and record setup commands, dependency lockfiles and configuration conventions.
2. Start the React client and FastAPI service; add a health endpoint.
3. Create migrations and a SQLite connection layer.
4. Configure secrets through environment variables; provide a placeholder-only example configuration.
5. Verify the chosen Meta model's current API: authentication, request/response format, tool calling, structured output or validation strategy, quotas and errors.
6. With credentials available, run a minimal real model request and one harmless tool round-trip.
7. Evaluate graph rendering with a small directed graph, selectable edges, grouped accounts and stable layout.
8. Establish formatting, type checking and targeted test commands.

### Deliverables

Runnable skeleton, configuration guide, model adapter interface and a short recorded capability result.

### Done when

The browser reaches the backend, migrations run from an empty database and a clean checkout has documented startup commands. A live Meta probe either passes or has a clearly stated credential/capability blocker. Do not treat a development stub as passing the live integration gate.

## 6. Stage 1 — Synthetic scenario and source data

### Work

Create a seeded generator with an adjustable six-month window, dozens of customers and enough ordinary transactions to provide context. Start small and expand only if it improves the demo.

Include:

- Meridian Workforce Services as the fictional salary payer.
- Eight workers with salary credits and ordinary spending.
- Three collection accounts: two owned by one individual and one owned by a separate company that individual owns.
- A common onward destination connected through available records to the staffing business.
- Recurring pay-cycle transfers, plus ordinary transfers and internal movements.
- Branch and ATM records with plausible shared-location explanations.
- Supporting records that explain a subset of payments; remaining payments unresolved.
- Unknown external counterparties, missing documents and uncertain entity matches.
- Opening balances, reversals and unrelated inflows to exercise attribution.

Define customer/account roles and company ownership separately. Record relationship source and validity dates. The alerted subject is one collection account; broader connections emerge through investigation.

### Data conventions

Store monetary values in integer minor units or an exact decimal representation, not binary floating point. Use one currency initially. Store timestamps in UTC and render a selected local timezone. Keep business dates explicit.

A transaction has one canonical ID. Do not double-count separate debit/credit representations of the same internal transfer. Distinguish posted, pending and reversed entries.

### Deliverables

Schemas, migrations, generator, seed/reset command, fixture documentation and separate evaluation truth.

### Done when

Generation is reproducible for a seed; identifiers and relationships validate; balances reconcile within defined coverage; transaction ordering is consistent. Workers are not universally anomalous and ordinary activity can be explained from visible evidence.

## 7. Stage 2 — Monitoring and case foundation

### Work

1. Implement one versioned rule: multiple incoming senders with rapid onward movement.
2. Set explicit configurable windows, counterparties, amount and timing thresholds.
3. Define the metric as observed aggregate activity; do not imply exact provenance of fungible funds.
4. Add an explainable 1–100 priority score and contribution breakdown.
5. Persist detection-run parameters, cutoff, rule version, evidence and outcome.
6. Support a configurable daily schedule and a manual Run detection action through the same execution path.
7. Use a deterministic alert identity to suppress duplicate runs for the same subject/rule/window.
8. Build the table queue with sorting, filters, owner, status and Follow The Money.
9. Add minimal persistent cases, notes and linked alerts.

### Deliverables

Working monitoring engine, scheduler, alert details and case records.

### Done when

A seeded run produces expected alerts; the highest-priority case is accessible; repeated execution does not duplicate it. Every score and trigger can be reproduced. Original detection values remain unchanged by later investigation findings.

## 8. Stage 3 — Deterministic investigation tools

### Initial tools

| Tool | Result |
|---|---|
| Reconstruct alert | Rule inputs, contributing records and reproduced values |
| Get customer context | KYC, accounts, expected activity and documented relationships |
| Compare behaviour | Current and baseline volumes, counts, timing and coverage |
| Expand network | Bounded neighbours with typed relationship edges |
| Trace onward activity | Time-respecting paths with attribution assumptions and limits |
| Inspect shared attributes | Addresses, branch/ATM usage and optional access links |
| Aggregate entity flows | Owner/group totals with internal/external movement separated |
| Retrieve supporting records | Relevant fixture documents with precise source references |

All tools return a common envelope: execution ID, parameters, data cutoff, source IDs, result, limitations and status.

### Work

Implement these as independently testable services before wiring them to agents. Enforce entity/time scope, maximum hops and result limits. Make unknown external-bank activity a visible boundary.

Use simple transparent anomaly measures first. Sparse or unstable baselines produce an insufficient-data result.

### Done when

API calls can uncover the collection network, ownership links, repeated timing and ordinary explanations without model assistance. Totals reconcile; group views do not merge separate legal entities or count transfers twice. Fund tracing cannot create backward-in-time paths.

## 9. Stage 4 — Meta runtime agents

### Workflow

1. Coordinator starts an investigation run with fixed scope and cutoff.
2. Alert reconstruction and customer-context tasks run concurrently.
3. Behaviour/network agent selects bounded follow-up calls.
4. Alternative-explanations agent examines ordinary explanations, contradictions and data gaps.
5. Coordinator produces a structured preliminary brief.
6. Investigator follow-up commands trigger new scoped analysis linked to the existing case.

The coordinator may be an explicit state machine; it does not need an LLM call for every routing decision. The analytical agents use Meta at runtime.

### Work

- Implement typed tool definitions and validate all arguments.
- Define findings as observed facts, calculations, hypotheses or unresolved questions.
- Require evidence references and reject unknown citation IDs.
- Separate shared evidence from independent corroboration.
- Record model identifier, configuration, tool executions and report versions.
- Set budgets for calls, elapsed time and expansion size.
- Persist progress events with sequence IDs for reconnect/replay.
- Handle cancellation, model errors and partial completion.
- Treat retrieved content as data rather than instructions.

### Deliverables

A working Follow The Money run with genuine tool activity, progress and a cited preliminary brief.

### Done when

The agents discover the configured pattern from visible records; test an ordinary explanation; identify missing evidence; and avoid unsupported claims of coercion, knowledge or criminality. A failed task leaves an explicit gap. Model integration is verified with a real call.

## 10. Stage 5 — Visual investigation workspace

### Work

Build a desktop-first workspace with:

- Persistent alert/case header.
- Interactive directed graph.
- Findings and evidence panel.
- Transaction timeline and date-range selection.
- Branch/ATM location view.
- Typed investigation commands.

Reveal new nodes and edges as tools discover them. Maintain stable positions where possible; avoid continual graph rearrangement.

Implement reversible account/entity views. Group accounts by documented legal owner. Show ownership links between people and companies without merging their legal identities. Display grouping sources, selected period and aggregation basis.

Selecting a finding highlights the supporting graph elements and source records. Selecting an ATM highlights the relevant events/accounts. A graph view should retain filter context when switching to the map.

Support “explained activity” as a proposed or human-reviewed classification; muting it is reversible. Label facts, inferred relationships and unknown identities distinctly. Use text/line styles as well as colour.

### Done when

The investigator can reveal common ownership, inspect pay cycles, explore ATM context and open evidence without losing their place. The graph, report and tables agree numerically. If the map cannot ship reliably, retain location-event tables and filters as the explicit fallback.

## 11. Stage 6 — Case review and report

### Work

- Assemble the brief from stored findings and their evidence.
- Include trigger, customer context, network/history, competing explanations, concerns, gaps and next steps.
- Allow investigator notes, corrections and evidence annotations.
- Preserve generated drafts separately from edited/approved versions.
- Record reviewer decisions and case disposition.
- Export a readable Markdown or HTML brief initially.
- Keep an audit trail for runs, findings, edits and decisions.

### Done when

A case can be reopened with the same evidence and decision history. Human edits are not overwritten by agent retries. No model output automatically files a report, restricts an account or closes the case.

## 12. Stage 7 — Validation, packaging and demo

### Scenario tests

| Variant | Expected behaviour |
|---|---|
| Concerning collection arrangement | Discover concentration and unresolved purpose; recommend targeted investigation |
| Documented ordinary arrangement | Identify evidence explaining the relevant payments |
| Missing ownership records | Leave ownership unresolved rather than inventing a common controller |
| Shared ATM without concerning financial links | Explain the connection's limited significance |
| Internal transfers and opening balances | Reconcile totals and preserve attribution limits |
| Tool/model failure | Report partial completion and permit safe retry |
| Incorrect or injected document instructions | Treat text as evidence; preserve tool permissions |

Use unit tests for calculations and identity/aggregation rules, integration tests for API/worker persistence, and a small number of browser tests for the main path. Do not build a broad test suite for cosmetic details.

Measure latency, model/tool calls, token/cost data where available, unsupported claims and evidence coverage. Record observations rather than claiming production accuracy from synthetic data.

### Packaging

Provide setup, reset and run commands; pinned dependencies; synthetic-data disclosure; secret-handling instructions; known limitations; and a deployment configuration appropriate to the selected target. Verify the deployed app separately if deployment is requested and credentials are available.

### Demo sequence

1. Open a real generated alert.
2. Start Follow The Money and show agent progress.
3. Expand the collection accounts.
4. Switch to entity view to expose documented ownership connections.
5. Inspect recurring pay-cycle and location patterns.
6. Challenge the accommodation explanation.
7. Review cited findings and unresolved questions.

A three-minute recording can transparently compress waits. Cached or recorded results must not be presented as new live executions.

### Done when

A clean reset produces the same investigable dataset, the core end-to-end workflow passes, Meta has been exercised live, and the demo has been rehearsed against the actual app.

## 13. Scope priorities

**Must ship:** synthetic data; one rule; score explanation; queue; one case; deterministic tools; real Meta investigation; evidence citations; collection-network graph; account/entity grouping; competing explanations; persistent review.

**Next priority:** timeline, ATM/branch map, richer export and polished progress animation. Structured location evidence remains available even if map work is deferred.

**Stretch:** voice input, extra typologies, device/IP analysis, multiple-user administration and additional anomaly models.

The product's most important visual moment is the transition from separate collection accounts to documented entity relationships. Protect that interaction when reducing scope.

## 14. Risks and responses

| Risk | Response |
|---|---|
| Meta API access or tool-call incompatibility | Probe early; isolate adapter; record any fallback explicitly |
| Slow or costly agent runs | Bound calls and data; parallelise independent work; measure early |
| Hallucinated findings | Typed results, citation validation, calculation tools and scenario evaluation |
| A predetermined investigation | Keep hidden labels out of prompts; test ordinary and incomplete variants |
| Overloaded graph | Bounded expansion, progressive disclosure and stable grouping |
| Unavailable external-bank information | Explicit coverage boundaries and unresolved endpoints |
| SQLite write contention | Single worker, short writes and simple deployment topology |
| Scope exceeds hackathon time | Deliver the complete core path before stretch features |

## 15. Development checkpoints

At each stage, record:

- Completed behaviour and changed files.
- Verification performed and results.
- Material limitations or blockers.
- Next stage and any decision needed from Chris.

Keep code and documentation in sync. Mark proposed choices as selected only after implementation/verification. Do not claim completion based solely on a mock, successful build or generated report.

## 16. Immediate next actions

1. Establish the repository location.
2. Verify Meta access and tool-calling behaviour.
3. Define the fixture entities and exact observable relationships.
4. Implement Stage 0 and Stage 1.
5. Review the first generated alert with Chris before broadening the scenario.

No additional handoff is required to start implementation in this workspace.

