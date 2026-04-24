# Contracts (normalized data shapes)

These contracts define the normalized shapes that cross boundaries between layers.
They are intentionally small and stable to support a future “library + app” upgrade.

## General rules

- Every record that can be snapshotted has:
  - **`as_of_utc`**: ISO-8601 timestamp in UTC (e.g. `2026-04-23T12:34:56Z`)
  - **`source`**: `"yahoo" | "polymarket" | "deribit" | "derived"`
- Prefer **numeric types** (float/int) after normalization; keep raw strings only when needed for provenance.

## Yahoo price row (normalized)

Fields:

- `symbol`: e.g. `BTC-USD`
- `asset`: e.g. `bitcoin`
- `timestamp_utc`: ISO date/time or pandas timestamp stored as ISO string
- `open`, `high`, `low`, `close`: float
- `volume`: float | int | null
- `source`, `as_of_utc`

## Polymarket probability row (normalized)

Fields:

- `event_title`, `event_slug`
- `market_question`
- `outcome`: e.g. `Yes`
- `probability`: float in \([0,1]\)
- `end_date_iso`: optional resolution date string
- `source`, `as_of_utc`

## Deribit option mark row (normalized)

Fields:

- `expiry_ts_ms`: int (Deribit epoch ms)
- `expiry_date`: `YYYY-MM-DD`
- `option_type`: `"call" | "put"`
- `strike`: float
- `mark_btc`: float
- `source`, `as_of_utc`

## Implied-lab state (user truth)

Fields:

- `expiry_str`: `YYYY-MM-DD`
- `mode`: `"exact_strikes" | "target_payoff"`
- `qty`: int
- `strikes_exact`: `{k1,k2,k3,k4}`
- `payoff_targets`: `{body_left, body_right, left_wing, right_wing}`
- `legs_enabled`: `{use_k1,use_k2,use_k3,use_k4}`
- `reverse`: bool
- `net_pnl_mode`: bool
- `user_belief`: `{enabled, center_usd, width}` where width is σ_ln

## Implied-lab outputs (derived)

Minimum stable fields:

- `summary`: name/cost/max_gain/max_loss/breakevens
- `overlay.payoff_usd`: list of payoff values aligned to chart grid
- `verification`: anomaly flags + provenance lines

## Implied-lab `market_data` payload (stable keys)

`market_data` is the normalized, UI-facing payload prepared by `probability_engine.services` (not by Streamlit). It is intentionally stable so UI remains layout-only while internals evolve.

Producer: `build_implied_lab_market_data` in `src/probability_engine/services/implied_lab_inputs.py`.

Stable top-level keys:

- `forward`: number (forward reference used for distribution/strategy)
- `vol`: number (annualized ATM IV, decimal; fallback defaults allowed)
- `T_years`: number (time-to-expiry in years; clamped away from 0 for display)
- `price_min`: number
- `price_max`: number
- `dist`: Distribution chart data (see below)
- `marks_full`: object (option marks payload; treated as opaque by UI except where explicitly normalized below)
- `call_marks`: array[object]
- `put_marks`: array[object]
- `avail_strikes`: array[number] (sorted unique strikes present in marks)
- `call_by_k`: map[number → number] (strike → mark)
- `put_by_k`: map[number → number]
- `data_sources`: array[string] (human-readable provenance lines)
- `as_of_utc`: timestamp (ISO-8601 UTC string)
- `quote_cache_ttl_s`: int (cache TTL used for the underlying quotes)

Distribution chart data (`market_data.dist`) stable keys:

- `prices`: array[number] (x-grid in USD, monotonically increasing)
- `pdf_pct`: array[number] (scaled density for charting; aligns 1:1 with `prices`)
- `pdf_raw`: array[number] (raw lognormal density per $; aligns 1:1 with `prices`)
- `cumulative_at`: array[tuple[number, number]] (pairs of (price, cdf_pct))
- `forward`: number
- `vol_annual`: number
- `T_years`: number

# Contracts (normalized, implementation-agnostic)

These contracts define the **canonical data shapes** exchanged across layers (`app` → `services` → `domain`/`infra`). They are intentionally **implementation-agnostic** (no pandas/ORM assumptions) but **concrete** enough to validate and test.

General rules:

- **Timestamps**: use ISO-8601 UTC strings (e.g. `2026-04-23T19:41:00Z`) or an equivalent timezone-aware datetime in code.
- **Currency/units**: be explicit; do not mix “USD” with “quote currency” implicitly.
- **Nullability**: absent/unknown values should be `null`/`None` (not magic numbers).
- **IDs**: vendor IDs are preserved, but internal keys should be separate and stable.

## 1) Spot / OHLCV row

Represents one time-bucket (or last trade snapshot) for an underlying.

Fields:

- **symbol**: string (internal symbol, e.g. `BTC-USD`, `GC=F`, `GLD`)
- **venue**: string (e.g. `yahoo`, `coingecko`, `exchange`)
- **ts**: timestamp (bucket end or snapshot timestamp)
- **open**: number | null
- **high**: number | null
- **low**: number | null
- **close**: number | null
- **volume**: number | null (base units if known; otherwise venue-defined)
- **currency**: string | null (e.g. `USD`)
- **interval**: string | null (e.g. `1m`, `1h`, `1d`)

Invariants:

- If `high`/`low` are present: \(high \ge \max(open, close)\) and \(low \le \min(open, close)\) when those exist.
- `volume` is non-negative when present.

## 2) Polymarket probability row

Represents a normalized probability snapshot for a Polymarket market/outcome.

Fields:

- **vendor**: literal `polymarket`
- **market_id**: string (vendor market identifier)
- **event_id**: string | null (vendor event identifier if available)
- **question**: string (human-readable market question/title)
- **outcome**: string (e.g. `YES`, `NO`, or outcome label)
- **probability**: number (0.0 to 1.0 inclusive)
- **ts**: timestamp (snapshot timestamp)
- **source**: string (e.g. `gamma`, `clob_mid`, `clob_last`)
- **liquidity_usd**: number | null
- **volume_usd_24h**: number | null
- **resolved**: boolean | null
- **resolution_ts**: timestamp | null
- **url**: string | null

Invariants:

- `0 ≤ probability ≤ 1`.
- If market is binary and both outcomes are present at the same `ts`, probabilities should sum to ~1 within tolerance (document tolerance per integration).

## 3) Option mark row

Represents a normalized option quote/mark snapshot (per strike, expiry, type).

Fields:

- **venue**: string (e.g. `deribit`)
- **underlying**: string (e.g. `BTC`)
- **quote_ccy**: string (e.g. `USD`)
- **ts**: timestamp (snapshot timestamp)
- **expiry_ts**: timestamp
- **option_type**: enum: `call` | `put`
- **strike**: number
- **mark_price**: number | null (venue-native, e.g. option price in quote currency or vol-derived; must be documented per venue adapter)
- **bid**: number | null
- **ask**: number | null
- **mid**: number | null
- **iv**: number | null (implied volatility, decimal, e.g. 0.65 for 65%)
- **delta**: number | null
- **open_interest**: number | null
- **volume**: number | null
- **instrument_id**: string | null (vendor instrument identifier)

Invariants:

- `strike > 0`.
- `expiry_ts > ts` for live quotes (allow equal/less for historical/resolved snapshots with explicit flag, if needed).
- If `bid` and `ask` present: `bid ≤ ask`. If `mid` present: `bid ≤ mid ≤ ask` (within tolerance).

## 4) Implied-lab state (inputs)

Represents the complete “lab” configuration required to reproduce a run deterministically.

Fields:

- **run_id**: string (unique per run; may be UUID)
- **ts**: timestamp (when the run was executed)
- **underlying**: string (e.g. `BTC`)
- **quote_ccy**: string (e.g. `USD`)
- **asof_ts**: timestamp (market data as-of timestamp used for the run; may equal `ts`)
- **expiry_ts**: timestamp
- **spot**: number (spot/forward reference used by the run)
- **rate**: number | null (risk-free rate used; decimal)
- **div_yield**: number | null

User-mode configuration:

- **mode**: enum: `exact_strikes` | `target_payoff`
- **legs**: array of leg definitions (see below)
- **target_payoff**: object | null (present when `mode=target_payoff`)

Leg definition:

- **side**: enum: `long` | `short`
- **option_type**: `call` | `put`
- **strike**: number
- **quantity**: number (contracts; sign is not used—use `side`)
- **price_ref**: enum: `mark` | `mid` | `bid` | `ask` | `manual`
- **premium**: number | null (required when `price_ref=manual`)

Invariants:

- `legs.length >= 1`.
- `quantity > 0`.
- If `mode=exact_strikes`, `target_payoff` must be null.

## 5) Implied-lab outputs (results)

Represents the computed outputs of the implied-lab given a specific state.

Fields:

- **run_id**: string (must match inputs)
- **asof_ts**: timestamp (echoed from inputs)
- **inputs_hash**: string | null (optional: stable hash of canonicalized inputs for reproducibility)

Pricing summary:

- **net_premium**: number (positive = debit, negative = credit; see sign conventions in `docs/SEMANTIC_CONTRACTS.md`)
- **max_gain**: number | null
- **max_loss**: number | null
- **breakevens**: array[number] (sorted)

Distribution outputs:

- **implied_distribution**: array of rows:
  - **x**: number (underlying price grid point at expiry)
  - **pdf**: number | null
  - **cdf**: number | null
- **implied_probability**: array of events:
  - **event_id**: string (internal event key, e.g. `underlying_above_K`)
  - **description**: string
  - **probability**: number (0..1)

Payoff outputs:

- **payoff_curve**: array of rows:
  - **x**: number (underlying price at expiry)
  - **payoff**: number (P&L or payoff in quote_ccy; document which)

Provenance:

- **data_provenance**: object
  - **option_marks_used**: array[Option mark row] (or references/keys to them)
  - **spot_source**: string
  - **assumptions**: array[string]

Invariants:

- All probabilities must be within [0, 1].
- `payoff_curve` and `implied_distribution` should share the same `x` grid when feasible.

## 6) Implied-lab `market_data` payload (stable keys)

`market_data` is the normalized, UI-facing payload prepared by `probability_engine.services` (not by Streamlit). It is intentionally **stable** so UI remains layout-only while internals evolve.

Stable top-level keys:

- **forward**: number (forward reference used for distribution/strategy)
- **vol**: number (annualized ATM IV, decimal; fallback defaults allowed)
- **T_years**: number (time-to-expiry in years; clamped away from 0 for display)
- **price_min**: number
- **price_max**: number
- **dist**: Distribution chart data (see below)
- **marks_full**: object (vendor-shaped option marks payload; treated as opaque by UI except where explicitly normalized below)
- **call_marks**: array[object] (vendor-shaped call mark rows; see “Normalized option marks” recommendation below)
- **put_marks**: array[object]
- **avail_strikes**: array[number] (sorted unique strikes present in marks)
- **call_by_k**: map[number → number] (strike → mark)
- **put_by_k**: map[number → number]
- **data_sources**: array[string] (human-readable provenance lines)
- **as_of_utc**: timestamp (ISO-8601 UTC string)
- **quote_cache_ttl_s**: int (cache TTL used for the underlying quotes)

Distribution chart data (`market_data.dist`) stable keys:

- **prices**: array[number] (x-grid in USD, monotonically increasing)
- **pdf_pct**: array[number] (scaled density for charting; aligns 1:1 with `prices`)
- **pdf_raw**: array[number] (raw lognormal density per $; aligns 1:1 with `prices`)
- **cumulative_at**: array[tuple[number, number]] (pairs of (price, cdf_pct))
- **forward**: number
- **vol_annual**: number
- **T_years**: number

### Recommendation: contract types to codify

To make the boundary explicit, add code-level contracts (TypedDict or dataclasses) mirroring the above:

- `DistributionChartData` (keys listed above)
- `ImpliedLabMarketData` (the `market_data` payload)

Also consider normalizing option mark rows into a stable `OptionMark` contract (even if the underlying venue is Deribit) so the implied-lab never depends on vendor payload drift:

- `OptionMark`: `strike: number`, `option_type: call|put`, `mark: number | null`, `bid: number | null`, `ask: number | null`, `expiry_ts: timestamp`, `ts: timestamp`, `venue: string`, `instrument_id: string | null`

