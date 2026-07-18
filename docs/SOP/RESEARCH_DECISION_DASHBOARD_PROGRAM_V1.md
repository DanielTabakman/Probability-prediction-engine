# Research Decision Dashboard — program v1

**Program ID:** `research_decision_dashboard`  
**Chapter:** `ppe_research_decision_dashboard_v0`  
**Plane:** CONTROL + OPERATOR PRODUCT  
**Pillars:** INFRA + LEGIBILITY  
**First ship-to:** OPERATOR  
**As-of:** 2026-07-18  
**Status:** **SELECTED FOR BOUNDED IMPLEMENTATION**

## Purpose

Give the founder and operator one inspectable surface for answering:

1. What theory are we testing?
2. What exact gates were tested?
3. What passed, failed, was blocked, or was never tested?
4. What evidence supports the interpretation?
5. Why did the branch continue, narrow, stop, or remain unresolved?
6. What specific evidence would reopen it?

The first initiative shown is hedge-backed event liquidity, using accepted Stage 0 and Stage 0.1 evidence. The surface is reusable governance infrastructure, not a Polymarket trading product.

## Problem

Current research outputs are technically reproducible but founder-hostile. Evidence is distributed across Markdown reports, JSON artifacts, commands, PR bodies, and terminal recommendations. This creates three risks:

- `NOT_TESTED` can be misread as `FAILED`;
- a venue-specific branch can be confused with the underlying theory;
- future strategy work can begin before prior assumptions, gates, and reopen conditions are understood.

## Canon

- [`CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md`](CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md)
- [`RESEARCH_PIPELINE_V1.md`](RESEARCH_PIPELINE_V1.md)
- [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md)
- [`../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md`](../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md)
- [`HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md`](HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md)
- [`HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_1_TERMINAL_AVAILABILITY_REPORT_V1.md`](HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_1_TERMINAL_AVAILABILITY_REPORT_V1.md)

## Product boundary

This is an internal, read-only research review surface.

It is not:

- a new analytical module class;
- a customer-facing Strategy Lab workflow;
- a live market scanner;
- an execution, custody, treasury, or order-routing surface;
- permission to restart the Polymarket hedge-scanner branch;
- permission to create or fund prediction markets.

The initial Streamlit entry point is feature-flagged:

```text
PPE_RESEARCH_REVIEW_UI=1
```

The page must render from frozen local evidence or committed fixtures. It must not perform live market-network calls during render.

## Core semantic rule

Every research gate must use one of these states:

| State | Meaning |
|---|---|
| `PASS` | The stated gate was positively demonstrated by evidence. |
| `FAIL` | The stated gate was tested and contradicted by evidence. |
| `BLOCKED` | A prerequisite failed or was absent, so this gate could not be run. |
| `NOT_TESTED` | The gate was in scope conceptually but no valid test was performed. |
| `NOT_AUTHORIZED` | The gate was intentionally outside the authorized stage. |
| `INCONCLUSIVE` | Evidence was gathered but is insufficient or conflicting. |

The UI must never collapse `BLOCKED`, `NOT_TESTED`, `NOT_AUTHORIZED`, or `INCONCLUSIVE` into `FAIL`.

## Required status separation

Each initiative must separately report:

- `theory_status` — status of the general economic or product thesis;
- `venue_or_branch_status` — status of the concrete venue/implementation branch;
- `profitability_status` — whether economics were actually tested;
- `execution_status` — whether live or shadow execution was tested or authorized;
- `recommendation` — continue, narrow, stop branch, watch, or select next stage.

For the first accepted fixture:

```text
theory_status: PLAUSIBLE_NOT_ECONOMICALLY_TESTED
venue_or_branch_status: STOPPED_POLYMARKET
profitability_status: NOT_TESTED
execution_status: NOT_AUTHORIZED
recommendation: STOP_POLYMARKET_BRANCH
```

## Dashboard information architecture

### 1. Decision header

Show initiative, stage, as-of timestamp, recommendation, and the four separated status fields above.

### 2. Theory and mechanism

Show a short theory statement and a compact mechanism chain. For hedge-backed event liquidity:

```text
terminal event contract
→ deterministic payoff specification
→ compatible listed-option hedge
→ executable synthetic bid/ask
→ costs and residual risk
→ quote / watch / abstain
```

Also show the observed mismatch between touch/path-dependent contracts and terminal option payoffs.

### 3. Test funnel

Show counts and where work stopped. The accepted Stage 0.1 fixture must display:

```text
general market objects discovered: 1100
BTC threshold candidates frozen: 7
semantically eligible: 0
synthetic hedges constructed: 0
executable discrepancies tested: 0
shadow trades: 0
```

### 4. Gate matrix

At minimum:

| Gate | Accepted Stage 0/0.1 state |
|---|---|
| Public market discovery | PASS |
| Deribit option availability | PASS |
| Deterministic semantic parsing | PASS |
| Terminal BTC contract availability | FAIL |
| Hedge compilation | BLOCKED |
| Full executable cost stack | NOT_TESTED |
| Historical profitability | NOT_TESTED |
| Shadow execution | NOT_TESTED |
| Live execution | NOT_AUTHORIZED |

### 5. Candidate inspector

For every frozen candidate show:

- market identifier and exact question;
- active/closed state;
- parsed contract fields;
- canonical classification;
- rejection/watch reasons;
- whether hedge compilation ran;
- source pointer and evidence timestamp when available.

### 6. Interpretation

Four explicit fields:

- `what_we_learned`;
- `what_we_did_not_learn`;
- `why_the_branch_stopped_or_continued`;
- `reopen_conditions`.

### 7. Provenance

Show canonical reports, PRs, accepted merge commit, witness timestamp, validation commands/results, artifact paths, and known coverage limitations.

## Data contract

A versioned JSON document must back the UI.

```text
ResearchDecisionDashboardV1
  schema_version
  initiative_id
  display_name
  stage
  as_of_utc
  theory_statement
  mechanism_steps[]
  theory_status
  venue_or_branch_status
  profitability_status
  execution_status
  recommendation
  funnel[]
  gates[]
  candidates[]
  interpretation
  reopen_conditions[]
  provenance
  warnings[]
```

The transformation from source evidence into this contract must be pure Python and unit-tested. Streamlit must only render the contract; it must not reinterpret research evidence.

## Initial artifact and fixture

Committed fixture:

```text
fixtures/research_decision_dashboard/hedge_backed_event_liquidity_stage0_1_v1.json
```

Optional generated operator artifact:

```text
artifacts/control_plane/RESEARCH_DECISION_DASHBOARD.json
```

The fixture is the deterministic acceptance witness. The generated artifact may later aggregate multiple initiatives, but v0 must not create a broad archival program.

## Chapter sequence

| Chapter | Status | Delivers |
|---|---|---|
| `ppe_research_decision_dashboard_v0` | SELECTED | Schema, accepted fixture, pure model/loader, feature-flagged Streamlit operator surface, tests, smoke witness |
| `research_decision_registry_v1` | DEFERRED | Multi-initiative registry and aggregation after two real initiatives prove the common schema |
| `research_decision_history_v1` | DEFERRED | Decision-change history only after an archive charter and demonstrated review need |

Do not generalize into a registry framework before the second initiative. The v0 schema may be reusable, but the implementation should remain small and reversible.

## Acceptance criteria

1. With `PPE_RESEARCH_REVIEW_UI=1`, an operator can open a Research Review surface from the existing Streamlit app.
2. With the flag absent or false, default customer/demo behavior is unchanged.
3. The accepted Stage 0.1 fixture renders without any network access.
4. The header visibly distinguishes: theory still plausible, Polymarket branch stopped, profitability not tested, execution not authorized.
5. The funnel shows `1100 → 7 → 0 → 0` and does not imply that 1,100 contracts were semantically inspected.
6. The gate matrix distinguishes `FAIL`, `BLOCKED`, `NOT_TESTED`, and `NOT_AUTHORIZED`.
7. All seven frozen candidates are inspectable with their rejection reasons.
8. Provenance includes PRs `#5384`, `#5385`, `#5386`, accepted merge commit `e162a4dc48a8c724d37502ca90bdebe49029d493`, canonical report paths, and witness timestamp.
9. Streamlit presentation contains no hedge math, market parsing, or independent interpretation logic.
10. Pure model/contract tests, UI smoke, pushable gate, pre-push gate, and CI are green before acceptance.
11. No order entry, wallet, custody, treasury, customer funds, or live execution paths are touched.
12. No new customer-facing navigation or MSOS product route is added.

## Validation expectations

```powershell
python -m pytest -q tests/test_research_decision_dashboard.py
python scripts/run_research_decision_dashboard_smoke.py
python scripts/run_pushable_gate.py
python scripts/run_pushable_gate.py --pre-push
```

The implementation PR must include a screenshot or structured smoke evidence showing the four separated statuses and the funnel.

## Review rule

Regular Chat independently reviews the implementation PR against this program, the SELECTION, and the Codex packet. Acceptance requires a mandatory `COORDINATION STATUS` block and direct inspection of changed files plus test/runtime evidence.

## Future initiative boundary

After this dashboard is accepted, the next proposed research charter is **issuer-created hedgeable event markets**: define terminal financial questions ourselves, determine where they may be listed, model market-creation incentives and conflicts, and test whether a separately hedged liquidity strategy is economically and operationally valid.

That future initiative requires its own venue, legal/terms, market-integrity, capital, and conflict-of-interest gates. It is not authorized by this program.