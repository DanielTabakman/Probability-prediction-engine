# API / Distribution Lane Charter v1

**Status:** Founder-approved lane charter.  
**Repository canon:** `DanielTabakman/Probability-prediction-engine`  
**API documentation home:** `docs/API/`  
**Execution authority / live queue:** existing PPE control plane in `docs/SOP/`; this charter does not create a second pipeline or queue.  
**Founder intent:** productize approved MSOS/PPE products as stable callable APIs, initially using no more than the five free Qatom API slots.

## Mission

Turn approved MSOS/PPE financial products into stable, documented, externally callable interfaces without creating a second source of financial logic.

The API lane is a **distribution and productization lane**. MSOS/PPE owns product meaning and financial reasoning. The API lane owns the contract and external delivery of that approved product.

## Core architecture rule

```text
market data / PPE engines
          ↓
     product interface
          ↓
      API adapter
          ↓
  Qatom / agents / web / partners
```

An API consumes an approved product interface. It must not fork or reimplement core product semantics in a second stack.

## What this lane owns

- request and response contracts;
- endpoint and schema versioning;
- input validation and stable error behavior;
- OpenAPI / machine-help / partner handoff;
- adapters from approved product logic to public interfaces;
- authentication, access, rate-limit and partner-integration controls when explicitly decided;
- conformance tests;
- isolated staging validation;
- production promotion and rollback evidence;
- uptime / telemetry / privacy-safe operational monitoring;
- Qatom integration acceptance and other external distribution surfaces.

## What this lane does not own

Without a separate founder/product decision, the API lane does **not**:

- invent or change financial methodology;
- create a second options calculation, cache, strategy engine or market-data producer;
- change product semantics to make an integration easier;
- add new assets merely because the schema supports them;
- create recommendation, execution, payment, ratings or ranking behavior not already approved as a product;
- edit Qatom source/configuration from this repository;
- create a new PPE pipeline, queue or authority class.

Product-meaning changes route back through MSOS/PPE product canon before API work continues.

## Qatom five-slot policy

Treat Qatom API slots as **product slots**, not endpoint slots.

A slot is consumed only when a distinct user-facing MSOS/PPE product needs its own callable surface. Internal calculations, helper functions, expiry resolution, payoff math, IV calculations, probability calculations and similar primitives remain internal.

| Slot | Product | State | Working rule |
|---|---|---|---|
| **1** | **Options Market Read** | EXISTING / ACTIVE PRODUCTIZATION | Current public contract: `GET /v1/options-market-read`. Finish partner/Qatom acceptance under the existing charter before broadening semantics. |
| **2** | **Best Exposure** | NEXT PRODUCT | Turn a user belief, horizon/date range and risk/payoff constraints into the approved best-fit exposure output. Reuse approved PPE/MSOS product logic; charter the public API contract separately before implementation. |
| **3** | **Exposure Compare** | WAIT | Do not consume a slot yet. First determine whether compare is a distinct product or a mode of Best Exposure. |
| **4** | **Reserved** | RESERVED | Requires a product-level founder decision and charter. |
| **5** | **Reserved** | RESERVED | Requires a product-level founder decision and charter. |

**Do not fill slots 4–5 merely because they are available.**

## Product 1 — Options Market Read

Canonical product contract:

- `docs/API/OPTIONS_MARKET_READ_V1.md`
- `docs/API/options-market-read.openapi.yaml`
- `docs/API/QATOM_OPTIONS_MARKET_READ_HANDOFF_V1.md`
- `docs/API/OPTIONS_MARKET_READ_STAGING_PLAN_V1.md`
- `docs/API/OPTIONS_MARKET_READ_UPTIME_V1.md`

Current execution chapter:

- `docs/SOP/SPRINT_OPTIONS_MARKET_READ_PARTNER_ACCEPTANCE_V1.md`
- `docs/SOP/PHASE_PLANS/options_market_read_partner_acceptance_v1_relay.json`
- `docs/SOP/OPTIONS_MARKET_READ_PARTNER_ACCEPTANCE_V1_EVIDENCE_STATUS.md`

As of this charter, the product API already exists and is production-live for BTC. The partner-acceptance chapter remains the canonical first API-lane execution job. Its status must be read from the live PPE phase machinery before work begins; this charter does not manufacture READY state.

## Product 2 — Best Exposure

Working product question:

> Given an asset, a belief about where/when it may move, and relevant loss/payoff constraints, what approved exposure structure best fits that belief?

Likely inputs include:

- asset;
- direction / target or target region;
- target date or date range;
- maximum loss / risk budget where applicable;
- payoff preference or exposure preference where applicable.

The public API contract is **not yet frozen**. Before implementation, reconcile it with current approved Options Made Simple / best-fit expression logic, including existing product canon such as `docs/SOP/SPRINT_OPTIONS_EXPRESSION_FIT_RANKING_V1.md`.

The API lane must not silently reinterpret existing educational/comparison semantics as execution advice.

## Product 3 — Exposure Compare

Hold as a product question, not an API commitment.

Decision to make after Best Exposure contract work:

- if comparison is simply another view over the same Best Exposure product, expose it as a mode or response capability of slot 2;
- if it has a distinct user job, contract, lifecycle and acceptance surface, charter it as slot 3.

## Definition of done for every API product

An API is not done because an endpoint returns HTTP 200.

### Contract

- purpose and product boundary are explicit;
- inputs are documented and validated;
- stable response schema exists;
- examples exist;
- errors are documented;
- schema/ruleset versioning is explicit;
- human-readable and machine-readable surfaces are aligned where applicable.

### Product behavior

- output uses approved product logic;
- deterministic behavior is deterministic by test;
- market information, interpretation and disclosures are separated clearly;
- unsupported behavior fails explicitly instead of being inferred;
- no hidden expansion into execution/advice/new assets.

### Engineering

- contract tests and conformance tests are green;
- staging is isolated where required;
- production promotion has an evidence receipt;
- rollback is tested/bounded;
- monitoring detects meaningful failures without collecting unnecessary personal data.

### Distribution

- Qatom/partner tool description matches the actual contract;
- external request/response is witnessed from outside the repo/runtime;
- access/auth/rate-limit/CORS decisions are recorded rather than guessed;
- machine help / OpenAPI / partner handoff match production;
- pricing or payment settings remain outside this repo unless explicitly added to scope.

### Closeout

- exact PR/head and CI evidence recorded;
- production version identified;
- runtime/monitoring evidence recorded;
- queue/phase state terminalized through the existing PPE machinery;
- next product slot remains unchanged unless separately approved.

## Storage and source-of-truth map

| Material | Canonical location |
|---|---|
| API lane entry point | `docs/API/README.md` |
| Lane charter / five-slot policy | `docs/API/API_LANE_CHARTER_V1.md` |
| Product contracts / OpenAPI / handoffs | `docs/API/` |
| Sprint charters / selection records / phase plans | `docs/SOP/` |
| Live execution state | `docs/SOP/ACTIVE_PHASE_MANIFEST.json`, `PHASE_QUEUE.json`, `PHASE_CHAPTER_BACKLOG.json` |
| Runtime API implementation | existing PPE product/runtime modules selected by each charter |
| Conformance / acceptance scripts | `scripts/` |
| Tests | `tests/` |
| Human/API help surfaces | approved `apps/msos-web/` paths for the selected product only |
| Deployment topology | `docs/DEPLOY/` and approved deployment configuration |

There is deliberately **no second API queue file** under `docs/API/`. Live work uses the existing PPE control plane so API state cannot drift from the rest of the build.

## Work flow

```text
founder product intent
    ↓
product-level decision / charter
    ↓
freeze API contract + allowed paths
    ↓
register/select through existing PPE phase machinery
    ↓
isolated API worktree / branch
    ↓
implementation + contract/conformance tests
    ↓
review + exact-head CI
    ↓
isolated staging
    ↓
production promotion + rollback witness
    ↓
external Qatom/partner acceptance
    ↓
monitoring receipt + terminal closeout
```

Shared-interface changes are serialized before dependent UI work. API and MSOS tasks may run in parallel only when their exact allowed file sets and contracts are non-overlapping.

## Desktop / Cursor lane

The API lane should use the **same PPE repository** in an isolated desktop worktree/workspace, not a new repository.

Recommended local convention, consistent with the existing lane layout:

`C:\Users\USER\MSOS-Lanes\02-API-Distribution`

Use an `api/` branch prefix. Before creating or reusing a worktree, inspect existing worktrees and active agents per `docs/SOP/THREE_TRACK_COORDINATION_HANDOFF_V1.md`. Do not repurpose the active MSOS Product worktree or the factory's disposable worktrees.

The local folder is a working surface only. GitHub `main` plus the accepted control-plane documents remain source of truth.

## Immediate queue

1. **Options Market Read partner acceptance v1** — use the already-chartered phase plan; recheck current eligibility and unresolved partner controls before selecting.
2. **Best Exposure API contract** — next product-contract charter after/alongside slot 1 only when the existing PPE control plane permits a non-overlapping planning slice.
3. **Exposure Compare decision** — WAIT until Best Exposure contract clarifies whether it is a separate product.
4. **Slots 4–5** — RESERVED.

## Decision rule

> Create a new public API when we have a distinct approved user-facing financial product. Do not create a public API merely because we have a new calculation.
