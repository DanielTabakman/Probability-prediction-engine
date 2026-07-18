# Market Proposal + Hedge Capacity Preview — program v1

**Program ID:** `market_proposal_hedge_capacity_preview`  
**Chapter:** `ppe_market_proposal_hedge_capacity_preview_v0`  
**Plane:** OPERATOR PRODUCT + RESEARCH  
**Pillars:** EDGE + LEGIBILITY + WORKFLOW  
**First ship-to:** OPERATOR / founder demo  
**As-of:** 2026-07-18  
**Status:** **SELECTED AS NEXT STEP; IMPLEMENTATION BLOCKED UNTIL #5388 ACCEPTANCE**

## Agent load bundle

| Role | Path |
|---|---|
| Program (charter) | this file |
| Selection | [`POST_MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_V0_SELECTION.md`](POST_MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_V0_SELECTION.md) |
| Implementation packet | [`MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_V0_CODEX_PACKET.md`](MARKET_PROPOSAL_HEDGE_CAPACITY_PREVIEW_V0_CODEX_PACKET.md) |
| Resolve | `python scripts/resolve_sop.py --chapter ppe_market_proposal_hedge_capacity_preview_v0 --json` |

## Purpose

Turn a proposed terminal BTC prediction-market idea into a shareable, evidence-backed preview that answers:

1. What exact question could be listed?
2. What objective settlement language would make it comparable to available options?
3. Which listed option structures approximate YES and NO exposure?
4. How much event payout can be supported by currently executable hedge depth?
5. What requested size remains unsupported?
6. What fees, payoff mismatch, currency basis, legging risk, collateral, venue and legal constraints remain?

This is the smallest product step toward prediction-market liquidity infrastructure as a service. It is a proposal and hedge-capacity tool, not a market-creation or execution system.

## Product statement

> Enter the financial event a customer wants. Receive a canonical terminal market proposal, current option-backed hedge capacity, unsupported size, conservative cost range, residual risk and a shareable one-page brief.

## Relationship to prior work

The accepted hedge-backed event-liquidity research stopped the Polymarket-specific branch because discovered contracts were touch/path-dependent rather than terminal contracts.

This program changes the order of operations:

```text
available listed option expiry and settlement
→ hedge-compatible threshold and payoff grammar
→ canonical prediction-market question
→ executable hedge-capacity preview
→ share/review
```

It does not restart the Polymarket scanner and does not assume any venue will list the generated question.

## Sequencing

1. `#5388` Research Decision Dashboard is implemented and independently accepted.
2. This chapter is implemented on a separate Codex branch and draft PR.
3. Regular Chat independently reviews contract semantics, calculations, live witness, UI and exported proposal.
4. The chapter stops for founder discussion.
5. No venue submission, customer outreach automation, capital commitment or further chapter begins without a new explicit decision.

## v0 market universe

- underlying: BTC only;
- event type: binary terminal `above` or `below`;
- hedge venue: Deribit public BTC inverse options path already used by the repository;
- hedge grammar: adjacent-strike vertical call or put spreads;
- payout: YES `$1`, NO `$0`;
- settlement: generated to match the selected Deribit expiry and official delivery-price method as closely as the public specification permits;
- requested size: total maximum binary payout in USD;
- mode: read-only public-data preview.

Linear USDC options, ETH, SOL, touch/barrier markets, dynamic hedging and venue-specific order entry are deferred.

## Required operator flow

### 1. Describe the desired event

Inputs:

- direction: `above` or `below`;
- requested threshold in USD;
- desired expiry horizon or selected listed expiry;
- requested maximum event payout/notional in USD;
- maximum order-book levels and slippage tolerance used for the capacity witness.

The tool must not accept unconstrained free-text resolution language as authoritative.

### 2. Generate a canonical proposal

The tool shows both:

- **requested threshold**;
- **proposed hedge-aligned threshold** selected from actual listed strikes.

It must never silently change the threshold.

The generated question must name:

- BTC as the only underlying;
- above/below comparator;
- one exact threshold;
- one listed expiry;
- `08:00 UTC` expiry time;
- the named Deribit BTC index/delivery price;
- the official delivery calculation window/method;
- explicit YES `$1` / NO `$0` payout.

Example form:

```text
Will the official Deribit BTC delivery price for the option expiry at
08:00 UTC on <date> be strictly above $<threshold>?

YES pays $1 and NO pays $0.
Resolution uses the official Deribit BTC delivery price calculated for that expiry.
```

The implementation must attach an as-of source pointer for the settlement specification and must not hardcode a stale method without provenance.

### 3. Compile hedge candidates

For each proposal, calculate where safely available:

- `long_yes_hedge`;
- `long_no_hedge`.

For an `above` market:

- YES exposure uses an adjacent-strike call spread around the proposed threshold;
- NO exposure uses an adjacent-strike put spread around the proposed threshold.

For a `below` market, the roles reverse.

Every candidate must show:

- long and short instrument names;
- strikes and strike width;
- expiry;
- contract multiplier;
- minimum tradable amount;
- exact order-book sides consumed;
- source timestamps;
- payoff ramp/band;
- maximum payout per spread unit;
- known settlement and currency-basis differences.

A structure may return `NOT_SAFELY_HEDGEABLE`; the compiler must never force a candidate.

## Hedge-capacity definition

“Hedge capacity” is not one venue-wide number. It is a snapshot conditional on side, price and depth.

The v0 output must include:

- top-of-book capacity;
- cumulative capacity through the configured number of levels;
- capacity within the configured maximum slippage;
- requested payout supported;
- requested payout unsupported;
- capacity timestamp and freshness state.

For a vertical spread with strike width `W` USD and executable spread amount `Q`, the maximum terminal USD payoff represented by that spread is approximately `W × Q`, before residual-risk reserves and settlement/currency adjustments.

Executable spread amount is limited by the smaller executable quantity across the two required legs after applying the correct buy/sell sides and cumulative depth.

The implementation must unit-test this normalization and must not label displayed book size as guaranteed fill capacity.

## Cost stack

Show separately:

- gross option-leg premium;
- bid/ask crossing cost;
- option trading fees;
- expected depth slippage under the selected policy;
- legging-risk reserve;
- stale/synchronization reserve;
- settlement/currency-basis reserve;
- predicted synthetic cost per `$1` maximum event payout;
- prediction-venue fees: `UNKNOWN_NOT_SELECTED` in v0;
- capital/collateral requirement: estimated or explicitly unknown.

The output must distinguish observed data, deterministic calculations, configurable assumptions and unknowns.

## Residual-risk disclosure

A finite-width vanilla vertical spread is not a perfect digital option.

The preview must visibly show:

- zero-payoff region;
- linear ramp region between strikes;
- full-payoff region;
- binary threshold;
- maximum local replication error within the ramp;
- strike-width percentage of threshold;
- any mismatch between event payout currency and option settlement currency;
- expiry/source/method alignment status.

The UI must never use “fully hedged,” “risk free,” or “arbitrage” when a residual payoff band or operational uncertainty remains.

## Readiness states

| State | Meaning |
|---|---|
| `SHAREABLE_DESIGN` | Contract is deterministic; at least one hedge side has fresh executable capacity; all material residual risks and unsupported size are visible. |
| `REVIEW_ONLY` | Proposal is understandable but capacity, freshness, settlement alignment or risk assumptions require operator review. |
| `NOT_SAFELY_HEDGEABLE` | No bounded static hedge candidate passes the v0 rules. |

These states do not authorize listing or trading.

## Required output contract

```text
MarketProposalHedgeCapacityPreviewV0
  schema_version
  as_of_utc
  requested_event
  proposed_contract
  settlement_spec
  threshold_adjustment
  requested_payout_usd
  yes_hedge
  no_hedge
  capacity_summary
  cost_stack
  residual_risk
  constraints[]
  unknowns[]
  readiness_state
  provenance
  review_stop
```

Each hedge side includes:

```text
status
legs[]
strike_width_usd
payoff_ramp
book_snapshot
capacity_levels[]
top_of_book_capacity_usd
policy_capacity_usd
synthetic_cost_per_1_usd
fees
unhedged_requested_usd
flags[]
```

## Operator/demo surface

Feature flag:

```text
PPE_MARKET_PROPOSAL_PREVIEW_UI=1
```

The surface may live beside Research Review or as a separate operator-only section, whichever causes less ownership conflict after `#5388` lands.

Required sections:

1. Proposed event inputs.
2. Generated canonical question and resolution language.
3. Requested versus proposed threshold.
4. YES and NO hedge cards.
5. Capacity ladder and requested/covered/uncovered bar.
6. Payoff mismatch visualization or table.
7. Constraints and unknowns.
8. Provenance and timestamps.
9. Copy/download one-page Markdown and JSON proposal.
10. Explicit banner: `PREVIEW ONLY — NO MARKET OR HEDGE HAS BEEN CREATED OR TRADED`.

## Offline and live modes

- A committed fixture must render and test without network access.
- Live public-data refresh occurs only after an explicit operator action.
- Live refresh must fail closed to stale/unknown rather than reuse old data silently.
- The share artifact records whether it came from a fixture or live public data.

## Hard boundaries

This chapter does not:

- submit, deploy or create a prediction market;
- select a production prediction venue;
- place prediction-market or option orders;
- access private accounts or balances;
- reserve or move capital;
- contact customers or venues automatically;
- claim independent price discovery;
- claim profitability or arbitrage;
- authorize a pilot;
- add assets beyond BTC;
- implement dynamic hedging;
- start the next chapter automatically.

## Acceptance criteria

1. `#5388` is merged and independently accepted before product-code implementation begins.
2. With the feature flag off, default app behavior is unchanged.
3. A BTC above/below proposal can be generated only from deterministic fields.
4. Requested threshold and proposed listed-strike threshold are both visible; no silent snapping.
5. Settlement wording matches the selected option expiry/source/method and carries an as-of provenance pointer.
6. YES and NO hedge candidates are shown independently; unsupported sides explain why.
7. Capacity is derived from the correct executable book sides and limited by the smaller leg quantity.
8. Top-of-book and configured depth/slippage capacity are distinct.
9. Requested payout, supported payout and unsupported remainder reconcile exactly.
10. Option fees and configurable reserves are separated from observed premium.
11. The finite spread payoff ramp and maximum residual mismatch are visible.
12. BTC settlement/currency basis is disclosed in the inverse-options v0 path.
13. Stale, crossed, missing or asynchronous books fail to `REVIEW_ONLY` or `NOT_SAFELY_HEDGEABLE`.
14. A deterministic offline fixture and unit tests cover capacity, normalization, fees, residual risk and status decisions.
15. A live public-data witness records selected instruments, timestamps, levels, capacity and constraints without placing orders.
16. The exported Markdown/JSON proposal is understandable without opening the app.
17. No execution, wallet, custody, treasury, customer outreach or venue-submission paths are touched.
18. Independent regular-Chat review checks the implementation against this program and issue `#5391`.
19. After acceptance, the workflow stops and returns to the founder for discussion.

## Validation expectations

```powershell
python -m pytest -q tests/test_market_proposal_hedge_capacity.py
python scripts/run_market_proposal_hedge_capacity_smoke.py
python scripts/run_market_proposal_hedge_capacity_witness.py --fixture
python scripts/run_market_proposal_hedge_capacity_witness.py --live
python scripts/run_pushable_gate.py
python scripts/run_pushable_gate.py --pre-push
```

The implementation PR must include structured smoke evidence and one exported proposal from the committed fixture. Live witness failure caused by public-data availability must be reported honestly and must not be replaced by an unsupported runtime claim.

## Official specification references to verify at implementation time

Use current official Deribit documentation and API metadata as the source of truth for:

- expiry and delivery-price calculation;
- contract multiplier and minimum order amount;
- settlement currency;
- option fees and delivery fees;
- strike availability;
- order-book amount semantics;
- account/position limits where displayed.

Do not treat this charter’s planning assumptions as a substitute for current venue specifications.

## Review stop

Successful completion means only:

> We can generate and share a credible market proposal with a current, bounded hedge-capacity preview.

It does not answer whether a venue will list it, whether customers want it, whether independent traders will participate, or whether the business is profitable. Those are the subjects of the mandatory founder review after this chapter.
