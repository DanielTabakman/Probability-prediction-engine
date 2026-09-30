# Market Thesis workflow v1 — inventory, schema, and state machine

**Status:** Sequence steps 1–3 on main. Step 5 UI slice in progress: Strategy Lab confirm syncs a `market_thesis` document through `/api/theses/market-thesis` and the display-api apply boundary. Step 4 (public machine catalog) remains with the API lane.  
**Issue:** [#5491](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5491)  
**Parent:** #5488  
**Sequence covered:** steps 1–3 (inventory, canonical schema / state machine, read-only validator).  
**As-of:** 2026-09-30  
**Machine schema:** [`market_thesis_v1.schema.json`](market_thesis_v1.schema.json)

This document is the contract for the thesis object. Step 4 (machine API) and step 5 (simplified UI) are not in this slice.

Execution and brokerage stay outside v1. The thesis document never gains an order, venue ticket, or “executed” state.

---

## Current state

A person can already capture pieces of a market view, but no single serializable object walks the issue’s path:

`thesis → horizon → direction / magnitude / uncertainty → market-implied evidence → disagreement / fit → candidate exposure structures → cost / risk / payoff comparison → saved artifact`

What exists today is four owner-scoped records plus several read-only math payloads.

| Record | Where it lives | What it actually stores |
|--------|----------------|-------------------------|
| `ThesisRecord` | `apps/msos-web/src/lib/thesisPersistence.ts`; `GET/PUT /api/theses` | One current confirm snapshot: instrument, horizon days, `marketRangePct`, `thesisRangePct`, reference/trust labels, lifecycle `exploring \| draft \| confirmed`, optional Strategy Lab `forwardMult` / `volMult` |
| `HorizonRegionIntent` | `apps/msos-web/src/lib/horizonRegion.ts`; `docs/VISION/OPTIONS_HORIZON/REGION_INTENT_SCHEMA_V1.md`; `/api/theses/horizon-region` | Price × time box, bias, optional `computed.implied_mass_pct` on the same object |
| `RegionBetContract` | `apps/msos-web/src/lib/regionBet.ts`; guided steps in `regionBetGuidedShell.ts` | Asset, entry spot, region, target expiry, market snapshot, risk constraints, selected expression ref. Lifecycle `draft \| active \| monitoring \| closed \| archived` |
| `ExpressionRecord` | `apps/msos-web/src/lib/expressionPersistence.ts`; `/api/theses/expression` | Planned or simulated paper plan, legs, optional paper-trade status `open \| closed \| expired` |

`apps/msos-web/src/lib/msosWorkflowStore.ts` keeps those four arrays in `msos_workflow_v1.json` and points each owner at one current id. They are not one document.

Mounted trader path on current main, from the #5490 surface audit: Strategy Lab compare → confirm → plan paper trade, plus Options Horizon and Exposure as separate doors. The Region Bet guided shell (`asset → window → region → compare → review`) is implemented and not mounted as its own route.

Storyboard semantics (`docs/VISION/MSOS/storyboard-v0.6/semantics/MSOS_Product_Semantics_State_Model_v0.1.md`) still say Exploring → Draft thesis → Confirmed thesis → Expression saved → Simulated or Executed → Monitoring → Reviewed. “Executed” is out of this charter. Monitoring and review stay on the existing Monitor / Region Bet surfaces; they are not Market Thesis v1 states.

---

## Primitives to reuse

Math stays in Python. The thesis document stores citations and frozen payloads. It does not recompute distributions, implied mass, or fit scores.

### Options Horizon

| Primitive | Contract | Role in the thesis |
|-----------|----------|--------------------|
| Horizon comparison | `src/engine/options_horizon_comparison.py` `kind: options_horizon_comparison`, schema 1. HTTP `GET /ppe-display-api/horizon/comparison.json` | Listed expiry buckets 30/60/90/180/365. Forward, ATM IV, one-sigma move, trust and data flags, time-decay language. `meta.read_only` and `meta.simulation_only` are true |
| Region intent | `REGION_INTENT_SCHEMA_V1` and `src/engine/horizon_region.py` `compute_region_implied_mass` | User box is horizon intent. `implied_mass_pct` plus `method` (`lognormal_reference` or `breeden_litzenberger`) is market evidence |
| Chart / archive | `GET /ppe-display-api/horizon/chart.json`, `GET /ppe-display-api/horizon/surface.json` | Display and replay inputs. Not a second evidence engine |

`apps/msos-web/src/lib/optionsHorizonComparison.ts` also builds comparison rows from a chart payload. That TypeScript copy is not the citation source. Citations use the Python payload.

### Implied range

`GET /v1/implied-range` is not the live contract. `docs/API/OPTIONS_MARKET_READ_V1.md` replaces that proposal.

Reuse `GET /v1/options-market-read` (`src/viz/options_market_read.py`):

- `schema_version` `1.3`, `ruleset_version` `options-market-read.v1.3`
- `distribution_method` `lognormal`
- Public implied range is `metrics.middle_50_range` (q25–q75), plus median, spot, implied forward, and `atm_iv_percent`
- `answer` is a deterministic two-sentence read. No LLM
- Product boundary already excludes exposure selection, ranking, strategy construction, and recommendations
- V1 asset is BTC. ETH returns 422 `unsupported_asset`

The thesis calls this the implied-range evidence citation. It does not revive `/v1/implied-range` or add a second options engine.

### Exposure

| Primitive | Contract | Role |
|-----------|----------|------|
| Exposure paths | `src/engine/exposure_paths.py`, catalog `config/exposure_path_catalog.yaml` | Candidate structures. `recommendation_status` is `path_not_recommendation` |
| Menu payload | `scripts/exposure_path_core.py` `kind: exposure_paths`. HTTP `GET /ppe-display-api/exposure-menu.json` | Asset menu: cost hint, leverage, time bound, pros/cons, trust badge, fit lenses |

Exposure answers “what paths exist?”. It does not know the user’s belief.

### Expression fit

Authoritative ranker: `src/engine/options_expression_fit_ranking.py`.

- `kind: options_expression_fit_ranking`
- `recommendation_status: educational_fit_not_recommendation`
- Preferences: `direction` (`long \| short \| neutral`), `belief` text, `target_horizon_days`, `max_loss_usd`, `payoff_preference`
- Weights: direction 30, horizon 20, max loss 20, payoff 15, trust 15
- HTTP: `GET /ppe-display-api/options-expression-fit-ranking.json`
- Candidates come from the exposure menu, plus an optional Strategy Lab suggestion when an expiry is supplied (`src/viz/options_expression_fit_ranking_boundary.py`)

`apps/msos-web/src/lib/optionsExpressionFitRanking.ts` repeats those weights for the Region Bet bridge. The thesis workflow calls the Python ranker. It does not extend the TypeScript scorer.

### Belief versus market, already partly drawn

Strategy Lab confirm (`buildThesisLabContext.ts`) writes a plain-language gap from user tuning (`forward_mult`, `vol_mult`) against display-payload implied width. That copy is display. It is not a frozen disagreement record.

Region Bet `market_snapshot` holds implied probability and implied move beside user `risk_constraints` and `selected_region`. Horizon region stores `computed` on the same object as `bias`. Those mixes are why the canonical document splits the two sides.

---

## Gaps

1. **No thesis envelope.** Four records and four lifecycles. None is the issue’s end-to-end artifact.
2. **Belief grammar is not direction / magnitude / uncertainty.** `ThesisRecord` stores two percents and optional multipliers. Expression fit stores a direction enum plus free-text belief. They are not the same object.
3. **Market numbers sit on user objects.** `marketRangePct` on `ThesisRecord`, `computed` on region intent, `market_snapshot` on Region Bet. A later reader cannot tell which fields the user asserted.
4. **Implied range is easy to mis-cite.** The backlog id `msos_implied_range_api_v1` is not the shipped API. The shipped read is Options Market Read, BTC only.
5. **Duplicate scorers.** Horizon comparison and expression-fit both exist as Python engines and TypeScript ports. A thesis that cites the TypeScript port will drift from the Python payload.
6. **Comparison prose is incomplete for the issue.** Fit ranking has `why` / `why_lower`. Exposure has `pros` / `cons` and `capital_shape`. Nothing stable lists cost, maximum loss, time horizon, payoff shape, and failure modes as one row.
7. **Saved does not mean reproducible.** Workflow JSON and `localStorage` are owner drafts. They do not pin ruleset versions, payload hashes, or a content hash of the comparison.
8. **Region Bet goes past v1 and is not the mounted path.** Its monitoring lifecycle and paper expression lanes are useful later. They are not this state machine. The shell is also unmounted.
9. **Paper-trade status is not thesis state.** `ExpressionRecord.paperTradeStatus` and any executed/monitoring storyboard state stay outside the v1 machine.
10. **No thesis machine API.** `/api/theses` persists `ThesisRecord` only. A stable thesis document API is sequence step 4.

---

## Thesis schema

Canonical kind: `market_thesis`. Schema id: `market-thesis.v1`. JSON Schema: [`market_thesis_v1.schema.json`](market_thesis_v1.schema.json).

`workflow_state` is not an independently editable flag. It is the furthest state whose guards pass. Writers recompute it after every event. A stored state that disagrees with `derive_state(document)` is invalid.

### Document

| Field | Owner | Rule |
|-------|--------|------|
| `schema_version` | system | Always `market-thesis.v1` |
| `id` | system | Stable id for this thesis |
| `revision` | system | Integer, starts at 1. A revise event increments it |
| `workflow_state` | derived | One of the states below |
| `asset` | user | `asset_id` required. `symbol` and `venue` optional |
| `user_belief` | user | Null in `draft`. From `belief_captured` on: direction, magnitude, uncertainty, assumptions, plain-language statement. No market snapshot fields |
| `horizon` | user | Null before `horizon_bound`. Then how far out the belief applies |
| `market_evidence` | market primitives | Citations only. Empty array until `evidence_attached` |
| `disagreement` | derived | Null until evidence and belief can be compared |
| `expression_comparison` | derived | Null until fit ranking has been attached |
| `artifact` | derived | Null until save. Self-contained frozen export |
| `prior_artifacts` | system | Earlier frozen exports kept on revise |
| `links` | system | Optional ids into the four existing stores. Links do not change those stores’ schemas |
| `authority` | system | `execution: out_of_scope`, `recommendation_status: educational_comparison_not_recommendation` |

### User belief

Required once the document leaves `draft`:

| Field | Values |
|-------|--------|
| `source` | Always `user` |
| `direction` | `long`, `short`, or `neutral`. Edge copy may say bullish, bearish, up, or down; persist the expression-fit canonical enum (`_DIRECTION_ALIASES` in `options_expression_fit_ranking.py`) |
| `statement` | Non-empty plain language |
| `magnitude.kind` | `price_band`, `percent_move`, or `qualitative` |
| `uncertainty.kind` | `wider_than_market`, `narrower_than_market`, `similar_to_market`, or `unspecified` |
| `assumptions` | Array of `{id, text}`. Empty array is allowed and means none stated |

`uncertainty` is the user’s claim about how wide outcomes are. ATM IV, middle-50 width, and implied mass are not stored here.

Optional `legacy_strategy_lab` may cite an existing confirm tuning (`forward_mult`, `vol_mult`, `thesis_range_pct`) so Strategy Lab is not rewritten. Those numbers remain a citation of the old confirm record. They are not market evidence.

### Horizon

`horizon.mode`:

| Mode | Required fields | Reuses |
|------|-----------------|--------|
| `listed_expiry` | `target_date` (`YYYY-MM-DD`) or `expiry_date` | Options Market Read expiry resolution |
| `bucket` | `target_bucket_days` in `30, 60, 90, 180, 365` | Horizon comparison buckets |
| `price_time_region` | `region.time_start_utc`, `region.time_end_utc`, `region.price_min_usd`, `region.price_max_usd` with end after start and max price above min | Region intent box |

Region `bias` maps into `user_belief.direction` (`bullish_in_region` → `long`, `bearish_in_region` → `short`, `neutral` → `neutral`). Region `computed` maps into a market citation, never into `user_belief`.

### Market evidence

`market_evidence.citations` is an array. Each citation:

| Field | Rule |
|-------|------|
| `citation_id` | Unique inside the document |
| `primitive` | `options_market_read`, `options_horizon_comparison`, or `horizon_region_implied_mass` |
| `endpoint` | The HTTP path above, or `compute_region_implied_mass` for region mass |
| `schema_version` or `ruleset_version` | Copied from the payload |
| `as_of_utc` | Copied from the payload |
| `request` | The exact query inputs |
| `payload` | Embedded response. Required on any citation that the saved artifact depends on |
| `payload_sha256` | Hex sha256 of canonical JSON (`separators=(",", ":")`, `sort_keys=True`) |

Forbidden inside a citation: user direction, user statement, fit score, order id.

Options Market Read is the implied-range citation. Horizon comparison’s `one_sigma_move_usd` is a second implied-move fact. Region implied mass is probability mass in a band, not a range. Do not collapse the three into one number.

### Disagreement

Present only in `disagreement_recorded` and later states.

| Field | Rule |
|-------|------|
| `method` | Named method string. V1 method id: `belief_vs_cited_evidence.v1` |
| `user_side` | Points at `user_belief` fields actually compared |
| `market_side` | One `citation_id` |
| `summary` | Plain language that names both sides |
| `read_only` | `true` |

The user does not type the disagreement. If belief or the cited evidence changes, disagreement is cleared and recomputed.

V1 comparison is descriptive, not a new probability. Allowed summary inputs are the user’s magnitude and uncertainty beside the cited middle-50, one-sigma move, or implied mass. No expected-profit sentence.

### Expression comparison

Present only in `expressions_ranked` and `artifact_saved`.

The block embeds one Python `options_expression_fit_ranking` payload. Preferences are copied from `user_belief` and user risk limits (`max_loss_usd`, `payoff_preference`). They are not copied from market evidence.

`rows` is the plain-language comparison. Each row:

| Field | Source |
|-------|--------|
| `candidate_id` | Exposure `path_id` or strategy candidate id, prefixed as the ranker already does (`exposure:…`) |
| `label` | Exposure label or ranker label |
| `source_primitive` | `exposure_paths` or `strategy_suggestion` |
| `rank`, `score` | Ranker output |
| `cost` | `cost_hint_usd` or strategy net cost. `status: estimated` or `unavailable`. Do not invent a price |
| `max_loss` | Ranker / exposure loss value. `bounded: false` when unknown, and a failure line that says so |
| `time_horizon` | Candidate horizon days, else the thesis horizon |
| `payoff_shape` | Exposure `headline` or `capital_shape` |
| `failure_modes` | Short strings drawn from exposure `cons`, fit `why_lower`, trust flags, and time-decay language. At least one string |
| `recommendation_status` | `educational_fit_not_recommendation` |

Empty candidate sets are legal: `rows: []` and `empty_reason` set. State can still be `expressions_ranked` so the artifact can say nothing fit.

### Artifact

`artifact_saved` adds:

| Field | Rule |
|-------|------|
| `frozen_at_utc` | ISO-8601 UTC |
| `content_sha256` | Canonical JSON of `user_belief`, `horizon`, `market_evidence`, `disagreement`, `expression_comparison`, `authority` |
| `shareable` | `true` means the JSON document is self-contained. It does not mean a public URL |
| `execution` | `out_of_scope` |

A revise keeps the previous artifact in `prior_artifacts` and clears every derived section that the edit invalidates.

### Separation rule

A field is either user-asserted, market-cited, or derived. Derived objects cite the other two. Mixing is a validation error `belief_market_mix`. Examples that fail: ATM IV inside `user_belief`, user direction inside a citation payload’s thesis fields, a fit score stored as something the market implied.

---

## State machine

States, in order:

1. `draft`
2. `belief_captured`
3. `horizon_bound`
4. `evidence_attached`
5. `disagreement_recorded`
6. `expressions_ranked`
7. `artifact_saved`

`artifact_saved` is the v1 terminal state. There is no `executed`, `monitoring`, or `reviewed` transition on this object.

```text
draft
  --set_belief--> belief_captured
  --set_horizon--> horizon_bound
  --attach_evidence--> evidence_attached
  --record_disagreement--> disagreement_recorded
  --rank_expressions--> expressions_ranked
  --save_artifact--> artifact_saved
```

`revise` is legal from every state except a brand-new empty id. It increments `revision`, appends a frozen artifact when one exists, and drops derived data from the edited section downward. `derive_state` then returns the furthest still-valid state.

### Guards

| Target state | Required in addition to the previous state |
|--------------|-----------------------------------------------|
| `draft` | `id`, `asset.asset_id`, `revision >= 1`, `authority.execution = out_of_scope` |
| `belief_captured` | `user_belief` complete per the table above |
| `horizon_bound` | `horizon.mode` and the mode’s required fields |
| `evidence_attached` | At least one citation whose primitive is `options_market_read`, `options_horizon_comparison`, or `horizon_region_implied_mass` |
| `disagreement_recorded` | `disagreement` cites `user_belief` and exactly one evidence `citation_id`, `read_only: true` |
| `expressions_ranked` | Embedded fit-ranking payload plus `rows` or `empty_reason`. Every row has cost, max loss, time horizon, payoff shape, and at least one failure mode |
| `artifact_saved` | `artifact.content_sha256` matches the canonical body. Every citation the disagreement or comparison uses has `payload` and `payload_sha256` |

### Illegal events

| Code | When |
|------|------|
| `illegal_transition` | Event skips a guard. Example: `rank_expressions` while `market_evidence.citations` is empty |
| `belief_market_mix` | User object contains a market metric, or a citation is labeled as user belief |
| `execution_out_of_scope` | Any order, broker, venue ticket, or transition named executed / filled / submitted |
| `stale_derived` | Disagreement or ranking hashes do not match the belief, horizon, and citation ids they name |
| `state_drift` | Stored `workflow_state` ≠ `derive_state(document)` |

Same document in, same state and same `content_sha256` out. Timestamps inside the hashed artifact body are the payload `as_of_utc` values and `frozen_at_utc` only. Do not hash “now” from a clock that is not stored.

### Invalidation

| Edit | Clears |
|------|--------|
| `user_belief` | disagreement, expression comparison, artifact |
| `horizon` | evidence citations that depend on that horizon, then disagreement, comparison, artifact |
| `market_evidence` citation used by disagreement | disagreement, comparison, artifact |
| risk limits or payoff preference | expression comparison, artifact |
| `save_artifact` | nothing, until the next revise |

Horizon evidence that does not depend on the edited field stays. An Options Market Read citation for a different expiry than the new horizon does not stay.

---

## Dependencies

Already on main, read-only:

- Options Market Read v1.3 for BTC (`GET /v1/options-market-read`)
- `build_options_horizon_comparison` and its display boundary
- `compute_region_implied_mass` when mode is `price_time_region`
- Exposure menu payload (`kind: exposure_paths`)
- `rank_expression_candidates` and `GET /ppe-display-api/options-expression-fit-ranking.json`
- Owner workflow store only as optional `links` targets

Not dependencies of the schema:

- `/v1/implied-range`
- TypeScript ports of comparison or fit scoring
- Region Bet monitoring, paper-trade status, or brokerage
- A public share URL
- Qatom or any other distribution adapter (sequence step 4 may add a machine route; this schema does not)

---

## First implementation slice

Sequence step 3 is the read-only validator in `src/engine/market_thesis.py`, with `tests/test_horizon_market_thesis.py` and the canned BTC document `tests/test_horizon_market_thesis_btc.json`. Optional workflow-store persist is not part of that module.

The slice is:

1. Pure Python validator and `derive_state` for `market-thesis.v1`, with the illegal-event codes above. No network in the state function.
2. One BTC fixture document that embeds canned Options Market Read, horizon comparison, exposure, and expression-fit payloads already produced by those primitives.
3. Tests: happy path to `artifact_saved`, skipped transition, `belief_market_mix`, revise invalidation, and byte-stable hash.
4. Optional persist of the document beside the existing workflow store via `links`. Do not change `ThesisRecord`, `RegionBetContract`, or `ExpressionRecord` shapes in that slice.

Still out of that slice: new HTTP route, MSOS page, TypeScript scoring, live order language, and retiring Region Bet or Strategy Lab confirm.

Layer for this module: `ppe-core`. UI stays a later `msos-shell` slice.

---

## Founder decision needed

None to start the read-only document slice above.

One product-meaning choice is open before sequence step 5 (the simplified UI), not before the validator:

Market Thesis v1 is specified as an envelope that cites Strategy Lab `ThesisRecord`, Horizon region intent, and Region Bet. It does not rename or retire them. Step 5 needs an explicit decision only if the mounted screen should replace one of those surfaces instead of citing it.

Live execution remains out of scope and is not a decision inside this charter.
