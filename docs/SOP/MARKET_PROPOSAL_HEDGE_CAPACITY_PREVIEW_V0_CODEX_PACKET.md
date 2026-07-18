# Market Proposal + Hedge Capacity Preview v0 — Codex implementation packet

**THREAD_ROLE:** `codex_build`  
**Issue:** `#5391`  
**Program:** [`MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_PROGRAM_V1.md`](MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_PROGRAM_V1.md)  
**SELECTION:** [`POST_MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_V0_SELECTION.md`](POST_MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_V0_SELECTION.md)

## Preconditions

Do not begin product-code edits until issue `#5388` has been merged and independently accepted.

Before editing, report:

- current accepted commit for `#5388`;
- ownership overlap in `src/viz/app.py`, `src/viz/app_sidebar.py`, smoke scripts and Deribit adapter paths;
- any disagreement with the program or selection;
- exact branch and base commit.

If another writer owns overlapping paths, stop and report the conflict.

## Goal

Implement the smallest operator/demo surface that generates a deterministic terminal BTC market proposal and calculates current, bounded option-hedge capacity from public Deribit order books.

The implementation ends with a shareable preview and a draft PR. Do not list a market, place orders, contact customers, or start a later chapter.

## Read first

- `docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md`
- `docs/SOP/RESEARCH_DECISION_DASHBOARD_PROGRAM_V1.md`
- `docs/SOP/MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_PROGRAM_V1.md`
- `docs/SOP/POST_MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_V0_SELECTION.md`
- `docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md`
- `docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_1_TERMINAL_AVAILABILITY_REPORT_V1.md`
- `src/data/fetch_deribit.py`
- `scripts/hedge_backed_event_stage0_1_terminal_witness.py`
- accepted `#5388` implementation files and smoke patterns

Do not rediscover or redesign the whole repository.

## Expected ownership

Prefer a bounded set such as:

- `src/engine/market_proposal_hedge_capacity.py` — pure contracts/calculations;
- `src/data/fetch_deribit.py` — only the smallest reusable public order-book addition if needed;
- `src/viz/market_proposal_hedge_capacity_view.py` — Streamlit rendering only;
- `src/viz/app.py` and/or `src/viz/app_sidebar.py` — minimal feature-flag integration;
- `fixtures/market_proposal_hedge_capacity/btc_terminal_v0.json`;
- `tests/test_market_proposal_hedge_capacity.py`;
- `scripts/run_market_proposal_hedge_capacity_smoke.py`;
- `scripts/run_market_proposal_hedge_capacity_witness.py`;
- one evidence/closeout doc required by existing repo convention.

Do not duplicate the Stage 0.1 script’s order-book helper into another script if a small reusable public adapter can own it safely.

## Required domain objects

Use frozen dataclasses, TypedDicts, Pydantic models or the repository’s smallest established pure-Python pattern.

At minimum:

```text
RequestedTerminalEvent
  underlying
  comparator
  requested_threshold_usd
  selected_expiry_utc
  requested_payout_usd
  max_depth_levels
  max_slippage_bps

ProposedTerminalContract
  question
  resolution_language
  proposed_threshold_usd
  threshold_delta_usd
  settlement_source
  settlement_method
  expiry_utc
  yes_payout
  no_payout

HedgeLeg
  instrument_name
  action
  option_type
  strike
  expiry_utc
  contract_multiplier
  book_timestamp
  levels_consumed[]

HedgeCapacitySide
  exposure
  status
  legs[]
  strike_width_usd
  top_of_book_capacity_usd
  policy_capacity_usd
  requested_payout_usd
  supported_payout_usd
  unsupported_payout_usd
  synthetic_cost_per_1_usd
  observed_premium
  fees
  reserves
  payoff_ramp
  residual_risk
  flags[]

MarketProposalHedgeCapacityPreviewV0
  schema_version
  as_of_utc
  requested_event
  proposed_contract
  yes_hedge
  no_hedge
  capacity_summary
  constraints[]
  unknowns[]
  readiness_state
  provenance
  review_stop
```

## Contract generation rules

1. BTC only.
2. Comparator exactly `above` or `below`.
3. One selected listed Deribit expiry.
4. Requested threshold is never silently changed.
5. Proposed threshold is an exact listed strike chosen by a deterministic rule.
6. UI shows the requested threshold, proposed threshold and delta.
7. Question and resolution language are generated from structured fields.
8. Expiry time and settlement method come from current official specification/API metadata with provenance.
9. Explicit YES `$1`, NO `$0`.
10. No fallback, alternative source, secondary condition, range, touch, reach, hit, dip or discretionary clause.

If official settlement metadata cannot be established, return `REVIEW_ONLY` or `NOT_SAFELY_HEDGEABLE`; do not invent wording.

## Hedge selection rules

Use adjacent listed strikes for the selected expiry.

For an `above` proposal:

- long YES candidate: adjacent call spread around the proposed threshold;
- long NO candidate: adjacent put spread around the proposed threshold.

For a `below` proposal, reverse the exposure mapping.

The exact choice of lower/upper strike relative to the binary threshold must be deterministic, documented and tested. Do not describe the finite-width spread as an exact digital replication.

Return an unsupported side with reasons when:

- fewer than two suitable strikes exist;
- required book side is missing;
- quote timestamps are stale or outside synchronization tolerance;
- order books are crossed or malformed;
- threshold lies outside supported strikes;
- policy capacity is below minimum executable size;
- settlement metadata is incompatible or unknown.

## Executable-book rules

Public data only.

For every leg:

- use asks to buy;
- use bids to sell;
- preserve price and amount at each consumed level;
- calculate cumulative quantity and VWAP;
- limit by configured depth and slippage policy;
- limit spread amount by the smaller executable amount across required legs;
- record source timestamps and freshness;
- do not call marks, mids or displayed raw size “executable capacity.”

The live witness must use one coherent snapshot process and must report timestamp skew.

## Capacity normalization

For vertical-spread amount `Q` and strike width `W` USD:

```text
maximum gross terminal USD payoff capacity ≈ Q × W
```

Apply contract multiplier from current instrument metadata.

Then calculate:

```text
supported_payout_usd = min(requested_payout_usd, policy_capacity_usd)
unsupported_payout_usd = requested_payout_usd - supported_payout_usd
```

These must reconcile exactly within explicit rounding rules.

For inverse options, disclose that premium and settlement occur in BTC and show the current-index conversion assumption separately from the terminal USD payoff normalization.

## Cost calculation

Separate:

- observed long-leg cost;
- observed short-leg proceeds;
- net spread premium;
- current index used for USD conversion;
- option fees using current official formula;
- depth slippage already embedded in VWAP;
- configurable legging reserve;
- configurable stale/synchronization reserve;
- configurable settlement/currency-basis reserve;
- prediction venue fees as `UNKNOWN_NOT_SELECTED`;
- collateral requirement as observed/estimated/unknown.

Never hide assumptions inside the observed premium.

## Payoff mismatch

For each vertical spread, produce a pure payoff table or function showing:

- below lower strike;
- inside ramp;
- above upper strike;
- corresponding binary payout;
- replication error;
- maximum error over the ramp;
- ramp width in USD and as a percentage of threshold.

This output must be rendered visibly and included in the export.

## Readiness decision

Implement only:

- `SHAREABLE_DESIGN`;
- `REVIEW_ONLY`;
- `NOT_SAFELY_HEDGEABLE`.

`SHAREABLE_DESIGN` requires deterministic contract wording, current settlement provenance, at least one safely constructed hedge side, fresh/synchronized books, positive policy capacity and visible residual-risk disclosure.

It still means no listing or trading authorization.

## UI

Feature flag:

```text
PPE_MARKET_PROPOSAL_PREVIEW_UI=1
```

With the flag false or absent, default behavior must not change.

Required UI:

- structured input form;
- explicit public-data refresh button;
- generated contract card;
- requested/proposed threshold comparison;
- YES and NO hedge cards;
- capacity ladder;
- requested/supported/unsupported summary;
- payoff mismatch table/visual;
- constraints and unknowns;
- timestamps and provenance;
- copy/download Markdown;
- download JSON;
- banner: `PREVIEW ONLY — NO MARKET OR HEDGE HAS BEEN CREATED OR TRADED`.

Do not add a default public/demo route or customer-facing navigation.

## Offline fixture

Commit one deterministic fixture containing:

- option instrument metadata;
- two-leg books with multiple levels;
- index price;
- settlement metadata/provenance;
- one requested above event;
- expected selected strikes;
- expected top-of-book and policy capacities;
- expected supported/unsupported payout;
- expected fees and reserves;
- expected payoff ramp;
- expected exported proposal fields.

The fixture must render with networking disabled.

## Tests

At minimum cover:

1. requested threshold is not silently changed;
2. proposed threshold selection is deterministic;
3. above and below hedge-side mapping;
4. buy uses asks and sell uses bids;
5. smaller leg limits spread amount;
6. top-of-book versus cumulative depth capacity;
7. slippage policy truncation;
8. multiplier and strike-width normalization;
9. minimum order amount;
10. requested/supported/unsupported reconciliation;
11. option fee cap and rounding;
12. inverse BTC conversion disclosure;
13. payoff ramp and maximum binary mismatch;
14. stale quote rejection;
15. timestamp-skew rejection;
16. missing/crossed book rejection;
17. one-sided supported result;
18. `SHAREABLE_DESIGN`, `REVIEW_ONLY`, `NOT_SAFELY_HEDGEABLE` decisions;
19. export schema and human-readable Markdown;
20. no-network fixture render.

## Live witness

`scripts/run_market_proposal_hedge_capacity_witness.py --live` must:

- fetch current public BTC inverse option instruments;
- choose one listed expiry with at least two adjacent strikes near current index;
- fetch public books for required legs;
- generate one deterministic proposal;
- calculate capacity and constraints;
- write a timestamped JSON plus compact Markdown summary under a dedicated artifact path;
- place no orders and use no authentication.

The witness must not claim success if books are missing, stale or empty. A fail-closed evidence result is valid.

## Share artifact

The Markdown export must fit on one practical page and include:

- proposed question;
- exact resolution language;
- requested payout;
- hedge-supported payout by side;
- unsupported remainder;
- selected legs and strike width;
- synthetic cost range;
- payoff mismatch;
- material constraints/unknowns;
- data timestamp and provenance;
- explicit no-listing/no-trade disclaimer.

## Validation commands

```powershell
python -m pytest -q tests/test_market_proposal_hedge_capacity.py
python scripts/run_market_proposal_hedge_capacity_smoke.py
python scripts/run_market_proposal_hedge_capacity_witness.py --fixture
python scripts/run_market_proposal_hedge_capacity_witness.py --live
python scripts/run_pushable_gate.py
python scripts/run_pushable_gate.py --pre-push
```

Also run the existing UI smoke required by the accepted `#5388` implementation if shared app/sidebar paths change.

## PR requirements

Open a draft PR. Include:

- exact base and head SHAs;
- changed files and why;
- ownership/overlap report;
- fixture expected values;
- unit/smoke/pushable/pre-push results;
- live witness outcome with artifact path;
- screenshot or structured UI evidence;
- one exported Markdown proposal;
- limitations;
- mandatory Coordination Status block.

Do not merge.

## Non-goals

No prediction venue adapter, listing submission, market deployment, customer messaging, CRM, order entry, private account access, wallet, custody, treasury, capital reservation, dynamic hedging, multi-asset support, profitability backtest or arbitrage claim.

## Completion rule

Completion means the draft PR is ready for independent regular-Chat review.

After acceptance, stop and return to the founder. Do not infer authorization for venue outreach, customer discovery, a listing pilot or live capital.