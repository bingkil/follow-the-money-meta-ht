# Follow The Money (FTM)
## Product and MVP Design — v0.2

**Date:** 1 November 2026  
**Owner:** Chris Prakoso  
**Status:** Design baseline for the Meta hackathon. Implemented so far: fixture, rapid-movement rule, alert queue and basic cases (see status.md). Agents, graph/timeline/map and reporting are not implemented.  
**Positioning:** AI-assisted financial investigation, grounded in transaction evidence.

## 1. Purpose

FTM combines a basic AML case manager and scheduled rule-based transaction monitoring with an agent-led investigation workspace. An investigator starts with a prioritised alert, selects **Follow The Money**, and receives an evidence-backed preliminary assessment. They can then explore historical behaviour, money flows, connected entities, locations and alternative explanations.

The core question is: **What explains this activity, what remains unresolved, and what should we investigate next?**

The demonstration uses a fictional network potentially associated with labour exploitation. The product is useful for ordinary AML investigations; it does not need to establish trafficking to deliver value.

## 2. Decisions and assumptions

| Topic | Status | Decision |
|---|---|---|
| Name | Agreed | Follow The Money; abbreviation FTM. |
| Foundation | Agreed | Basic case management and regular rule-based transaction monitoring. |
| Alert prioritisation | Agreed | Score from 1–100, higher meaning greater concern/priority; highest first. |
| Investigation entry | Agreed | Each alert has a Follow The Money action that launches collaborating agents. |
| Core evidence | Agreed | Triggering rule and transactions, account/customer KYC, history and connected network. |
| Investigative tools | Agreed | Graph analysis and anomaly detection. |
| Contextual links | Agreed | Shared addresses, employers, counterparties, branches and ATM usage; IP/device data when available. |
| Excluded scenario dependencies | Agreed | No personal teller observations or victim disclosure. |
| Reasoning | Agreed | Investigate credible ordinary explanations alongside concerning ones. |
| Case narrative | Agreed direction | Possible labour exploitation/human trafficking; do not claim criminal proof from financial patterns. |
| Collection network | Agreed extension | Explore salary payments distributed across collection accounts with common ownership or a common onward beneficiary; investigate possible mule activity. |
| Main demo rule | Proposed | Rapid onward movement of funds received from multiple individuals. |
| Presentation | Proposed | Alert table followed by linked graph, timeline, location view and evidence panel. |
| Demo shape | Proposed | One case with competing explanations, rather than two complete investigations. |
| Technology and deployment | Open | Architecture below is a proposal, not a selected or verified stack. |

The alert score is a prioritisation score, not a calibrated probability of crime. The original detection score remains visible; investigation findings do not silently overwrite it.

## 3. Users and jobs

**Primary user:** AML investigator at a financial institution.

The investigator must reconstruct an alert, understand the customer and activity, discover relevant connections, test explanations, capture findings and decide the next action.

**Secondary user:** Reviewer or team lead who needs reproducible evidence, a clear rationale and an audit history.

The MVP assumes one institution's permitted data. External counterparties are not automatically customers: their KYC, balances, transactions and ownership may be unknown. The interface must make this boundary visible.

## 4. MVP scope

### Included

- Scheduled monitoring with a manual Run detection action for demonstration.
- Versioned rules, run history, reproducible triggering calculations and duplicate suppression.
- Alert queue: sorting, filters, score breakdown, owner and status.
- Basic cases: linked alerts, assignment, notes, evidence, investigation history and disposition.
- Follow The Money investigation with visible agent progress.
- Preliminary report with citations to records and deterministic calculations.
- Historical behaviour analysis and bounded network expansion.
- Linked graph, timeline and ATM/branch location exploration.
- Explicit competing explanations and missing-evidence tracking.
- Human-reviewed case conclusion and downloadable investigation brief.

### Deferred

Production banking connectors, enterprise-scale graph infrastructure, autonomous regulatory filing or account restrictions, unrestricted web investigations, biometric identity inference, gesture controls and a full regulatory reporting system.

Voice input is a stretch feature. Typed investigation commands must provide the complete core experience.

## 5. Fictional scenario

All names, locations, amounts, people, relationships and records in the demo are synthetic. Thresholds and behaviour parameters are engineering choices, not official typology thresholds.

### 5.1 Starting alert

A personal account receives transfers from several individuals and moves much of the aggregate value onward quickly. The customer's recorded occupation is salaried employment, and the activity differs from the account's prior baseline.

This is the initial monitored subject. The staffing company is discovered during investigation; it is not implicitly the initial alert subject.

### 5.2 Evidence discovered

1. Several senders receive regular payments from **Meridian Workforce Services**, a fictional staffing company.
2. They repeatedly transfer portions of those payments to several collection accounts shortly after payday; one is the initially alerted account.
3. Network expansion reveals two collection accounts owned by the same individual and a third owned by a separate company that individual owns. These accounts send funds onward to **Meridian Accommodation Services**, a fictional company.
4. Available company/KYC records link the destination company to a director of the staffing business. The exact relationship and its source are shown.
5. Some workers share addresses or account-opening branches.
6. Across several pay cycles, subsets use the same ATM within a short period after payday.
7. Historical comparisons reveal whether the arrangement is stable, new, growing or inconsistent.

These facts support investigation of a collection arrangement. They do not establish who controlled a withdrawal, whether a worker consented, or whether exploitation occurred.

### 5.3 Collection network and possible mule activity

The investigative question is: **Are these separate recipients, or does the money converge under common ownership or control?**

The expanded fixture uses eight workers and three collection accounts. Salary portions may be split across recipients; workers retain ordinary spending and other payments. Exact amounts and timing remain configurable synthetic choices.

Account-level analysis initially shows separate recipients. Entity-level analysis groups the two personally owned accounts and exposes the ownership relationship to the third account's corporate owner. The company remains a separate legal entity; its funds are not labelled the individual's personal receipts merely because that individual owns it.

| Pattern | Interpretation to investigate |
|---|---|
| Several accounts owned by one person | Activity distributed across that person's accounts; not by itself a mule ring |
| Accounts owned by different people forwarding to a common destination | Possible intermediary or mule network; assess purpose and each person's role |
| Company receiving recurring payments from workers | Potential accommodation, services or unexplained collection arrangement |
| Evidence of operation by someone other than the account owner | Possible third-party control; requires supporting evidence beyond shared location or IP |

Use **collection network with possible mule activity** as a working hypothesis. Account ownership, company ownership, authorised access and inferred control are distinct relationships. Do not presume the workers are confirmed victims or that intermediaries knowingly participate; an intermediary could also be exploited.

This extends the existing case rather than creating a second demo: salary distribution → multiple collection accounts → common onward beneficiary. Retain the same ordinary explanations and structured branch/ATM context, without teller observations or victim disclosures.

### 5.4 Competing explanations

| Hypothesis | Supporting evidence to seek | Evidence that could challenge it |
|---|---|---|
| Shared accommodation or household expenses | Existing agreements, consistent payment amounts, documented recipient role | Amounts materially inconsistent with the agreements; unclear onward beneficiary |
| A person collects payments for coworkers | Documented collection arrangement, consistent stated purpose | Activity inconsistent with recorded role; unexplained aggregation or onward transfers |
| Wage diversion or employer-linked compulsory repayments | Recurring pay-cycle flows benefiting an employer-connected entity | Credible documented purpose explaining those specific transfers |
| Family or community support | Available relationship and payment-purpose evidence | Relationships unsupported or amounts/timing inconsistent with the explanation |

Absence of an agreement in bank records is an information gap, not proof that no agreement exists. A document matching some transfers explains those transfers, not every aspect of the relationship.

### 5.5 Expected conclusion

A defensible preliminary finding might be:

> A recurring collection network routes part of several workers' income through several collection accounts to an employer-connected entity. Shared accommodation is a plausible explanation. Available records explain some activity but do not establish the purpose of the remaining transfers. Further investigation is recommended; coercion and trafficking are not established.

The generated report must follow the actual evidence supplied. This sample is not a hard-coded outcome.

## 6. Monitoring and scoring

### 6.1 Detection lifecycle

A configurable schedule starts a detection run against a fixed data cutoff. Each run stores its identifier, rule versions, parameters, cutoff, start/end time, coverage and outcome.

Proposed initial cadence: daily. A manual demo run uses the same code path.

For every match, retain the subject, relevant window, triggering transaction IDs, metric values, thresholds and rule version. A deterministic alert key prevents duplicate alerts for the same rule version, subject and window. Later overlapping matches can link to an existing case without erasing the original alert.

### 6.2 Proposed first rule

**Multiple incoming senders with rapid onward movement.**

Configurable inputs:

- Evaluation window.
- Minimum distinct incoming counterparties.
- Minimum aggregate incoming value.
- Maximum elapsed time for onward movement.
- Minimum proportion moved onward.

Define exclusions such as reversals and internal transfers explicitly. Use posted transactions, consistent time zones and a single currency for the first demo.

An outflow occurring after an inflow is not proof that the same money moved onward. Keep aggregate turnover separate from time-respecting flow estimates, document the attribution method, and account for opening balance and other inflows.

### 6.3 Proposed scoring

Start with an explainable deterministic weighted score covering rule severity, magnitude of threshold exceedance and deviation from historical activity. Weights and breakpoints are configurable and versioned; selecting them is an implementation task.

Each alert exposes its component contributions. Scores must be reproducible, bounded to 1–100 and labelled uncalibrated for the synthetic MVP. Avoid counting the same signal repeatedly under different names.

### 6.4 Anomaly analysis

Use transparent baseline comparisons initially: current versus prior transaction volume, counterparty count, outflow timing and concentration. Display underlying values and observation coverage. Sparse history returns insufficient baseline rather than a fabricated anomaly score.

Graph-derived findings may include shared recipients, repeated convergence of flows and connected components. A connected component is not automatically a criminal ring.

## 7. Investigator workflow and UI

### 7.1 Alert queue

Use a table for efficient triage. Columns: score, subject, rule, detected date, triggering amount/window, status, owner and Follow The Money.

Provide score sorting, rule/status filters, run coverage and a clear distinction between new alerts and existing cases. Selecting a row opens details; the action starts an investigation run.

### 7.2 Investigation workspace

- **Header:** subject, alert, original score, rule, date range, owner and case status.
- **Centre:** interactive graph of customers, accounts, counterparties and relevant shared attributes.
- **Side panel:** preliminary brief, selected evidence, explanations and follow-up actions.
- **Bottom:** timeline with payday and flow events.
- **Location view:** map for observed branch/ATM events, synchronised with the selected time range.
- **Command input:** bounded requests such as “Trace the next recipient”, “Compare the last three pay cycles” or “What supports accommodation payments?”

Keep financial edges distinct from shared-address, ownership and access links. Expose amounts, dates, counts and source records on selection. Use visual labels and line styles in addition to colour.

Selecting a statement highlights its supporting records and graph elements. Selecting a node updates context without discarding the current investigation.

### 7.3 Account and entity views

Provide a reversible **Accounts / Entities** toggle. Account view shows the distinct accounts and transfers. Entity view groups accounts by documented legal owner, sums relevant external flows and displays company ownership as a separate link. A related-entity group can highlight the individual and their company without merging their legal identities.

Show the ownership source and validity date. Keep unknown owners and uncertain matches separate. Switching views preserves the selected window, evidence and investigation context. Expanding a group restores its accounts and source transactions.

Count each transaction once in totals for the selected boundary. Distinguish external receipts, onward payments and transfers within the group; do not inflate totals by adding every hop of the same flow. State group membership and aggregation rules beside the calculation.

### 7.4 Explained activity

The investigator can mark specific activity as explained with a rationale and evidence. Explained edges may be muted, but remain reversible and accessible. An agent may propose this classification; the UI must distinguish a proposal from the investigator's decision.

### 7.5 Location semantics

Home branch, account-opening branch and transaction branch are separate attributes. An account's home branch is not a transaction location.

ATM usage identifies where a recorded event occurred. It does not establish who physically used the card. Shared IP addresses or devices are access signals, not proof of common ownership or control. Maps must not imply continuous tracking between observed events.

## 8. Agents and tools

A coordinator creates a bounded investigation plan and dispatches independent tasks. The “flock” is visible through useful progress and findings, not simulated conversations or private reasoning transcripts.

| Agent | Task | Main output |
|---|---|---|
| Alert reconstruction | Recompute trigger and validate contributing records | Verified trigger explanation or discrepancy |
| Customer context | Retrieve permitted KYC and documented relationships | Profile, expected activity, source coverage |
| Behaviour and network | Compare history and inspect paths, convergence and shared attributes | Quantified patterns and graph evidence |
| Alternative explanations | Test ordinary explanations and challenge unsupported claims | Supporting/contradictory evidence and gaps |
| Coordinator | Reconcile outputs and assemble findings | Preliminary report and recommended next steps |

The alternative-explanations agent can begin with initial evidence and run again after network findings. It must be able to change the assessment rather than merely append a generic disclaimer.

### Proposed tool contracts

- get_alert(alert_id)
- get_customer_context(customer_id, as_of)
- get_transactions(subject_id, start, end, filters)
- compare_activity(subject_id, baseline_window, current_window)
- trace_funds(account_id, window, max_hops, constraints)
- expand_network(entity_id, relationship_types, limits)
- find_shared_attributes(entity_ids, attribute_types)
- aggregate_entity_flows(entity_ids, window, ownership_as_of, boundary)
- analyse_location_events(account_ids, window, grouping)
- retrieve_documents(entity_ids, document_types)
- save_investigation_draft(case_id, structured_findings)

Every result contains source IDs, parameters, time range, coverage limitations and execution time. Tools compute amounts, graph metrics and anomaly statistics; the model interprets and communicates them.

Set budgets for model calls, tool calls, expansion depth, result size and elapsed time. A failed agent yields a partial report with an explicit gap, not a fabricated completion. Cancel and retry operate at the investigation-run level; retries preserve provenance and avoid duplicate notes.

## 9. Evidence and report contract

A finding contains:

- Stable finding ID and plain-language claim.
- Classification: observed fact, derived calculation, hypothesis or unresolved question.
- Supporting and contradictory evidence references.
- Tool execution or document location that produced the evidence.
- Applicable time window and data coverage.
- Alternative explanations and missing information.
- Suggested next action and investigator review state.

Record source data separately from model-generated interpretation. Preserve contradictions. Evidence reused by multiple agents remains one source, not independent corroboration.

### Preliminary report

1. Triggering rule and transactions.
2. Customer/account context.
3. Historical and network findings.
4. Ordinary explanations and supporting evidence.
5. Remaining concerns and conflicting evidence.
6. Data gaps and proposed next steps.
7. Investigator decision, once recorded.

Use qualitative assessment with reasons rather than invented probabilities of trafficking. Every material factual claim must link to evidence. Reports identify the model/configuration and investigation-run version used.

## 10. Conceptual data model

| Entity | Key fields/relationships |
|---|---|
| Customer | ID, person/business type, occupation/business activity, expected activity, KYC as-of date |
| Account | ID, customer relationship, type, currency, open/close dates, home/opening branch |
| CustomerAccountRole | Customer, account, owner/signatory/other role, validity dates, source |
| Transaction | ID, source/destination reference, amount, currency, timestamp, status, channel, optional branch/ATM |
| Counterparty | ID, observed name/account identifiers, known/unknown identity, resolution evidence |
| Relationship | Endpoints, type, validity, source, observed/inferred status |
| LocationEvent | Transaction/access reference, location identifier, timestamp, location type |
| AccessEvent | Account, time, IP/device identifier, source and availability |
| Document | ID, related entities, date, type, source location, access permissions |
| Rule / DetectionRun | Versioned definition, parameters, cutoff, execution history |
| Alert | Subject, run/rule references, window, trigger evidence, score components, status |
| Case | Linked alerts/entities, owner, status, notes, disposition |
| InvestigationRun | Case, plan, model configuration, agent/tool events, coverage, completion state |
| Finding / EvidenceReference | Claims, source pointers, calculations, contradictions and review state |
| AuditEvent | Actor, action, timestamp, before/after references |

Do not merge entities solely because names, addresses or IPs match. Exact identifiers can establish deterministic links; uncertain matches remain explicitly tentative.

## 11. Proposed technical architecture

Technology selection remains open. A practical first implementation could use:

- TypeScript/React web interface with an interactive graph component and map.
- Python API and analysis layer for deterministic rules, statistics and graph traversal.
- Relational storage for records, cases and provenance.
- In-memory graph projection for the bounded synthetic dataset; a dedicated graph database is not required for the MVP.
- Background worker for scheduled detection and investigations.
- Server-sent events or equivalent for progress updates.
- Server-side Meta model adapter for planning, tool selection, evidence interpretation and report generation.

The Meta model must contribute at runtime. Deterministic tools supply facts and calculations. Exact Meta model names, API support, limits, latency and cost must be verified before implementation; this document does not assume a validated integration.

Persist investigation steps before emitting progress. Isolate data access from model prompts. Treat retrieved text as evidence, never as instructions to change tool permissions. Keep API credentials server-side.

## 12. Synthetic data and evaluation

Proposed fixture: six months of activity, dozens of customers and several thousand transactions, including routine background activity. Final sizes are adjustable for readability and response time.

Include:

- An alerted collection account and two additional collection accounts discovered through network expansion.
- Two accounts with one documented individual owner, plus a separate corporate account with a documented ownership link to that individual.
- Convergence on a common onward beneficiary, with internal transfers included to validate aggregation.
- Workers with recurring payments from the staffing company.
- A documented employer-connected destination.
- Shared branch/ATM patterns with ordinary geographic explanations.
- A legitimate payment subgroup with available supporting records.
- Unresolved transfers that are not fully explained by those records.
- Missing counterparties/documents and an uncertain entity match.
- Reversals, opening balances and unrelated flows to test attribution.

Keep generator ground truth separate from investigator-visible data. Agents must not receive hidden labels such as “trafficker” or “innocent”. Fixture outcomes must be recoverable through tools rather than embedded in prompts.

Validate financial consistency, dates, references, source visibility and the distinction between known and inferred links.

## 13. Case lifecycle and audit

Proposed alert states: New, Assigned, Investigating, Resolved.

Proposed case states: Open, Investigating, Pending information, Ready for review, Closed.

Closure records a human-selected disposition and rationale, such as explained activity, escalation recommended or inconclusive. An agent-generated recommendation does not itself close a case.

Retain the original detection result, subsequent evidence, report versions, investigator edits and actions. Do not equate an alert's resolution with a legal finding.

## 14. Three-minute demo

| Time | Action | What it demonstrates |
|---|---|---|
| 0:00–0:20 | Show completed monitoring run and prioritised queue; open the top alert | Familiar operational starting point |
| 0:20–0:55 | Select Follow The Money; display agent progress and initial brief | Runtime AI gathers evidence |
| 0:55–1:30 | Expand the collection network, switch to entity view and trace the common beneficiary | Hidden concentration across accounts |
| 1:30–1:55 | Move through pay cycles; select shared ATM events | Graph, time and location work together |
| 1:55–2:25 | Ask whether this is accommodation; inspect supporting and conflicting evidence | Competing explanations tested |
| 2:25–3:00 | Review the brief, unresolved questions and proposed next steps | Reviewable investigative outcome |

Measure latency early. Prepared fixtures are acceptable, but do not portray recorded or cached model outputs as fresh live execution. If a live run takes longer, the demo video can transparently compress waiting.

## 15. Acceptance criteria

- A fixed detection run produces reproducible alerts, trigger evidence and scores.
- Re-running the same window does not create duplicate alerts.
- Follow The Money executes real model/tool work and records each result.
- Trigger explanations reproduce the actual rule calculations.
- Graph expansion respects time, hop, permission and known-data boundaries.
- Opening balances and unrelated inflows do not become falsely attributed paths.
- Selecting a finding reveals its supporting records.
- Account/entity views preserve distinct legal owners and cite ownership evidence.
- Entity/group totals reconcile to unique source transactions without double-counting internal movements.
- Possible mule activity remains a hypothesis; the system does not infer knowledge or coercion from account ownership.
- Shared locations/access attributes do not automatically establish common control.
- An ordinary explanation is evaluated using actual fixture evidence.
- Missing documents are presented as gaps, not contradictions.
- Partial failures produce explicit incomplete sections and allow retry.
- Investigator edits and dispositions persist with an audit trail.
- The system does not assert trafficking or identify perpetrators from financial patterns alone.

Evaluation should include at least an explained variant, an unresolved variant, incomplete data, and a misleading shared-location connection. Measure grounded-claim coverage, unsupported claims, numerical accuracy, tool success rate, runtime and cost per investigation.

## 16. Implementation sequence

1. Lock the synthetic scenario, visible evidence and competing explanations.
2. Define schemas and create consistent fixtures.
3. Build one deterministic rule, detection runs, score explanation and alert queue.
4. Implement evidence retrieval, historical comparison and bounded graph tools.
5. Integrate the Meta model and structured findings contract.
6. Build the linked graph/timeline/location workspace.
7. Add alternative-explanation testing, report review and case audit.
8. Validate scenario variants, measure latency and rehearse the demo.

Defer additional typologies and voice until the core path is credible and reliable.

## 17. Open decisions

- Exact initial rule parameters and priority-score weights.
- Which supporting accommodation records are available in the fixture.
- Which ownership links are internal KYC versus an explicitly supplied registry extract.
- Whether digital-access data belongs in the first demo.
- Technology stack, model selection and deployment.
- Final visual design and graph/map libraries.
- Review/disposition wording and export format.

## 18. Research basis

The uploaded references informed the discussion. This document is a product design, not a legal standard, and does not claim that all supplied publications have been exhaustively reviewed.

- **OSCE, Following the Money (2019):** contextual investigation, the 360° workflow, consideration of ordinary activity and evidence provenance. Relevant discussion: printed pp. 50–52.
- **FinCEN, FIN-2014-A008:** trafficking-related financial patterns; human trafficking and smuggling indicators must remain distinct.
- **Polaris, A Roadmap for Systems and Industries to Prevent and Disrupt Human Trafficking (2018):** context for labour supply chains and financial activity.
- **FINTRAC, July 2021 operational alert:** specifically sexual exploitation; do not apply those indicators wholesale to this labour scenario.
- **FATF (2011), OSCE (2014) and ESAAMLG (2011)** uploaded reports provide further background for later review.
- [UNODC: Crime of trafficking in persons](https://www.unodc.org/e4j/en/tip-and-som/module-6/key-issues/crime-of-trafficking-in-persons.html)
- [FBI: Trafficking indicators](https://www.fbi.gov/investigate/violent-crime/human-trafficking/trafficking-indicators)

No institution's endorsement is implied. Operational or jurisdiction-specific requirements should be verified before production use.

## 19. Change log

**v0.1 — 1 November 2026:** Captures the agreed FTM foundation and scenario. Retains structured branch/ATM evidence; excludes personal teller observations and victim disclosures. Separates approved direction from proposed implementation details.


**v0.2 — 1 November 2026:** Adds multi-account salary collection, common ownership and onward-beneficiary analysis, possible mule activity, reversible account/entity views, aggregation safeguards, and corresponding fixture, tool, demo and acceptance updates.
