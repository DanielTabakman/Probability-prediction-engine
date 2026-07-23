# Market Proposal + Hedge Capacity Preview v0

**Readiness:** `SHAREABLE_DESIGN`  
**As of:** 2026-07-19T01:30:00Z

**PREVIEW ONLY - NO MARKET OR HEDGE HAS BEEN CREATED OR TRADED**

## Proposed Question

Will the official Deribit BTC delivery price for the option expiry at 08:00 UTC on 2026-09-25 be strictly above $95,000? YES pays $1 and NO pays $0.

## Resolution

Resolution uses the official Deribit BTC delivery price for the selected option expiry at 2026-09-25T08:00:00Z. The delivery price is the 30-minute TWAP of the Deribit BTC index from 07:30 to 08:00 UTC, using snapshots every 4 seconds as described by the recorded Deribit settlement provenance. YES pays $1 if the delivery price is strictly above $95,000; otherwise NO pays $1.

## Thresholds

- Requested threshold: $93,000
- Proposed listed-strike threshold: $95,000
- Delta: $2,000

## Requested And Supported Payout

- Requested maximum event payout: $8,000.00
- YES hedge supported payout: $8,000.00
- NO hedge supported payout: $6,000.00
- Unsupported remainder at best side: $0.00

## Hedge Candidates

### YES Hedge - `SUPPORTED`

- Strike width: $5,000
- Top-of-book capacity: $4,000.00
- Policy capacity: $9,000.00
- Synthetic cost per $1 maximum payout: 0.4553887
- Unsupported requested payout: $0.00
- BUY BTC-25SEP26-90000-C (call, strike $90,000) using asks
- SELL BTC-25SEP26-95000-C (call, strike $95,000) using bids
- Payoff ramp: $90,000 < delivery < $95,000
- Maximum local mismatch: $5,000.00

### NO Hedge - `SUPPORTED`

- Strike width: $5,000
- Top-of-book capacity: $3,000.00
- Policy capacity: $6,000.00
- Synthetic cost per $1 maximum payout: 0.44983975
- Unsupported requested payout: $2,000.00
- BUY BTC-25SEP26-95000-P (put, strike $95,000) using asks
- SELL BTC-25SEP26-90000-P (put, strike $90,000) using bids
- Payoff ramp: $90,000 < delivery < $95,000
- Maximum local mismatch: $5,000.00

## Constraints

- Read-only public-data preview; no order entry or account access.
- Capacity is a snapshot from displayed book depth, not a guaranteed fill.
- Finite vertical spreads create a visible payoff ramp rather than exact binary replication.
- BTC inverse options settle premium and exercise value in BTC; preview normalizes terminal payoff to USD.

## Unknowns

- Prediction venue fees and listing rules are UNKNOWN_NOT_SELECTED in v0.
- Customer demand, market-maker interest and legal/terms approval are unknown.
- Collateral/margin for short spread legs is account-specific and not reserved.

## Provenance

- Data mode: fixture
- Deribit sources: public/get_instruments, public/get_order_book, public/ticker
- Settlement references: https://support.deribit.com/hc/en-us/articles/29734325712413-Settlement, https://support.deribit.com/hc/en-us/articles/31424939096093-Inverse-Options, https://docs.deribit.com/api-reference/market-data/public-get_instruments, https://docs.deribit.com/api-reference/market-data/public-get_order_book, https://support.deribit.com/hc/en-us/articles/25944746248989-Fees

## Review Stop

Preview only. No prediction market, hedge, order, venue submission, capital reservation, customer outreach, pilot or arbitrage claim is authorized.
