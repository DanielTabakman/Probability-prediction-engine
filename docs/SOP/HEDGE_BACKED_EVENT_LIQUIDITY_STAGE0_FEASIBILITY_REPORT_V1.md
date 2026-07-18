# Hedge-backed event liquidity Stage 0 feasibility report v1

**Status:** Stage 0 evidence complete  
**As-of:** 2026-07-18 19:27-19:31 UTC  
**Thread role:** `codex_build`  
**Parent charter:** [`../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md`](../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md)  
**Recommendation:** `NARROW_AND_REPEAT`

## 1. Executive Answer

The existing Polymarket-Deribit cross-venue pipeline is reusable as a discovery and probability-gap witness, but the fresh Stage 0 evidence does **not** justify an unconditional Stage 1 hedge scanner.

The blocker is payoff compatibility. The current/recent BTC price-event universe discovered on Polymarket is recurring and liquid enough to study, but the active contracts are primarily **touch/path-dependent** contracts: "Will Bitcoin reach/hit/dip to K by December 31, 2026?" They resolve if any Binance one-minute candle high or low crosses the threshold during a window. A static terminal Deribit call spread or put spread does not replicate that payoff.

Observed quote quality is mixed:

- Polymarket CLOB top-of-book bid/ask and visible size are obtainable for active token IDs.
- Deribit individual option tickers expose top-of-book bid/ask, mark, open interest, and timestamps.
- The existing cross-venue snapshot stores Polymarket outcome prices, options-implied probabilities, and Deribit mark-derived spread proxies. It does **not** store depth-aware executable synthetic bid/ask or a full fee/slippage/collateral stack.

Result: continue only with a narrower repeat focused on genuinely terminal BTC `above` / `below` contracts. The authorized next action is a terminal-only repeat with a frozen Polymarket and Deribit bid/ask/depth witness. Touch-option/barrier-style replication is a separate possible future charter decision, not part of this continuation authorization.

## 2. Evidence Date And Commands

Commands run from `C:\Users\USER\Desktop\Probability-prediction-engine` on branch `codex/hedge-backed-liquidity-stage0`, based from PR #5384 (`agent/charter-hedge-backed-event-liquidity`).

```powershell
git fetch origin pull/5384/head:refs/remotes/origin/pr-5384
git switch -c codex/hedge-backed-liquidity-stage0 origin/pr-5384
python scripts\collect_cross_venue_snapshot.py --max-questions 20 --polymarket-limit 300
python scripts\run_cross_venue_scan.py --save-snapshot --max-questions 20 --top 20
python scripts\run_cross_venue_tradeability.py --latest-snapshot
python scripts\run_cross_venue_backtest.py
pytest -q tests/test_cross_venue_export.py
python scripts/run_pushable_gate.py
python scripts/run_pushable_gate.py --pre-push
```

Fresh artifacts:

| Artifact | Path | Result |
| --- | --- | --- |
| Snapshot | `artifacts/cross_venue_snapshots/2026-07-18/ppe_cross_venue_prob_panel_192648Z.csv` | 1 matched row |
| Scan | `artifacts/cross_venue_reports/latest.md`, `artifacts/cross_venue_reports/latest.json` | 1 ranked row |
| Tradeability | `artifacts/cross_venue_tradeability/latest_report.md`, `artifacts/cross_venue_tradeability/latest_summary.json` | 1 row flagged by spread proxy |
| Backtest | `artifacts/cross_venue_backtest/latest_report.md`, `artifacts/cross_venue_backtest/latest_summary.json` | 2 snapshots, 0 resolved questions |

Backtest warning: local history is too thin for accuracy or profitability conclusions: 2 snapshot files, 0 resolved questions, pending 2, with the default 14-snapshot minimum unmet.

## 3. Data-Quality And Quote-Type Audit

### Existing pipeline

The reusable collector path:

```text
fetch_polymarket_markets -> markets_to_probabilities -> btc_price_questions_from_polymarket
-> fetch_deribit_spreads_around_predictions -> enrich_prediction_spreads_pointwise
-> cross_venue snapshot / scan / tradeability
```

What it proves:

- Polymarket BTC price-question discovery can run against fresh public data.
- Deribit BTC option instruments, marks, ATM IV, and pointwise options-implied probabilities can be matched to event rows.
- The scan can rank probability gaps.
- The tradeability report can subtract a **spread proxy** from an options-implied probability gap.

What it does not prove:

- Exact event payoff compatibility.
- Exact resolution-time or resolution-index compatibility.
- Static hedge replication of touch contracts.
- Executable synthetic bid/ask from correct hedge legs and available size.
- Polymarket and Deribit fees, slippage, legging reserve, collateral/margin burden, and settlement reserve.

Quote labels:

| Source | Observed field | Label |
| --- | --- | --- |
| Polymarket Gamma `outcomePrices` | YES/NO probabilities such as `["0.0275","0.9725"]` | midpoint/market estimate, not executable by itself |
| Polymarket Gamma `bestBid` / `bestAsk` | e.g. 150k reach market `0.026 / 0.029` | top-of-book executable indicator |
| Polymarket CLOB `/book` | bid/ask levels and sizes per token | visible book depth |
| Deribit `get_book_summary_by_currency` mark_price | used by existing collector | mark, not executable |
| Deribit ticker `best_bid_price` / `best_ask_price` | e.g. `BTC-25DEC26-150000-C` `0.0006 / 0.0010` BTC | top-of-book executable indicator |
| Existing `spread_proxy_prob_pct` | normalized mark/top-of-book proxy from existing spread helper | proxy, not full synthetic hedge ask/bid |

Implementation note: the fresh CSV `question` column currently serializes a Python dict as a string for the matched row. This is legible enough for research evidence but should be cleaned before any Stage 1 scanner contract.

## 4. Contract Taxonomy

| Taxon | Found? | Hedge implication |
| --- | ---: | --- |
| Terminal `YES if BTC > K at T` | Not found in active fresh sample | Eligible target for future repeat |
| Terminal `YES if BTC < K at T` | Not found in active fresh sample | Eligible target for future repeat |
| Touch / reach high by deadline | Yes, recurring and active | Static terminal call spread is not safe replication |
| Touch / dip low by deadline | Yes, but mostly resolved/closed in sample | Static terminal put spread is not safe replication |
| Conditional timing, e.g. before GTA VI | Yes | Rejected: nonfinancial timing condition and possible 50/50 clause |
| Holdings/value of entity BTC | Yes | Rejected: not underlying BTC terminal price |
| Scalar BTC price market | Found only old/closed | Rejected for this binary hedge task |

## 5. Candidate Compatibility Matrix

Polymarket resolution source for the active reach contracts is Binance BTC/USDT one-minute candle high, not Deribit settlement. Deribit matched expiry for year-end 2026 candidates is `2026-12-25 08:00 UTC`, while Polymarket deadline is `2027-01-01 05:00 UTC`; this creates a roughly 6 day 21 hour timestamp/expiry gap.

| # | Market ID | Candidate | Event bid/ask, visible YES depth | Event payoff | Deribit witness | Compatibility | Outcome |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `2467210` | BTC reach $70,000 by Dec 31 2026 | `0.70 / 0.71`, size `1181.67 / 203.89` | Binance high touch | `BTC-25DEC26-70000-C` bid/ask `0.0760 / 0.0775`; `75000-C` `0.0515 / 0.0525` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 2 | `2467209` | BTC reach $75,000 by Dec 31 2026 | `0.45 / 0.47`, size `3420.32 / 100.00` | Binance high touch | `75000-C` `0.0515 / 0.0525`; `80000-C` `0.0345 / 0.0350` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 3 | `2467208` | BTC reach $80,000 by Dec 31 2026 | `0.31 / 0.32`, size `2028.45 / 4800.50` | Binance high touch | `80000-C` `0.0345 / 0.0350`; `85000-C` `0.0225 / 0.0230` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 4 | `2467207` | BTC reach $85,000 by Dec 31 2026 | `0.20 / 0.21`, size `4218.28 / 23430.32` | Binance high touch | `85000-C` `0.0225 / 0.0230`; nearest higher strike not captured in compact witness | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 5 | `2467206` | BTC reach $95,000 by Dec 31 2026 | `0.11 / 0.12`, size `1674.76 / 1191.66` | Binance high touch | `95000-C` `0.0100 / 0.0105`; higher strike needed for normalized spread | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 6 | `701493` | BTC reach $130,000 by Dec 31 2026 | `0.043 / 0.049`, size `360.40 / 2707.78` | Binance high touch | `130000-C` `0.0013 / 0.0018`; `140000-C` `0.0009 / 0.0011` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 7 | `701492` | BTC reach $140,000 by Dec 31 2026 | `0.034 / 0.035`, size `263.30 / 31.91` | Binance high touch | `140000-C` `0.0009 / 0.0011`; `150000-C` `0.0006 / 0.0010` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 8 | `701491` | BTC reach $150,000 by Dec 31 2026 | `0.026 / 0.029`, size `137.06 / 25.75` | Binance high touch | `150000-C` `0.0006 / 0.0010`; `160000-C` `0.0006 / 0.0008` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 9 | `701490` | BTC reach $160,000 by Dec 31 2026 | `0.025 / 0.026`, size `26.11 / 68.34` | Binance high touch | `160000-C` `0.0006 / 0.0008`; `170000-C` `0.0003 / 0.0007` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 10 | `701489` | BTC reach $170,000 by Dec 31 2026 | `0.020 / 0.021`, size `3025.48 / 9.80` | Binance high touch | `170000-C` `0.0003 / 0.0007`; `180000-C` `0.0003 / 0.0007` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 11 | `701488` | BTC reach $180,000 by Dec 31 2026 | `0.019 / 0.020`, size `372.19 / 20.10` | Binance high touch | `180000-C` `0.0003 / 0.0007`; `190000-C` `0.0003 / 0.0004` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 12 | `701487` | BTC reach $190,000 by Dec 31 2026 | `0.021 / 0.024`, size `76.72 / 984.66` | Binance high touch | `190000-C` `0.0003 / 0.0004`; `200000-C` `0.0002 / 0.0005` | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 13 | `701486` | BTC reach $200,000 by Dec 31 2026 | `0.022 / 0.023`, size `410.66 / 7695.75` | Binance high touch | `200000-C` `0.0002 / 0.0005`; higher strike needed for cap | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 14 | `573656` | BTC hit $150k by Dec 31 2026 | `0.035 / 0.036`, size `390.95 / 65.63` | Binance high touch | Dec 25 2026 150k strike exists | touch payoff, expiry and index mismatch | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 15 | `540844` | BTC hit $1m before GTA VI | `0.498 / 0.499`, size `12502.16 / 18186.53` | conditional touch plus GTA timing | no useful listed static strike match | conditional/nonfinancial timing; possible 50/50 clause | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 16 | `246539` | BTC hit $20,000 or less by Jun 30 2022 | closed | low touch | expired / unavailable | archived and path-dependent | `WATCH_EVIDENCE_INCOMPLETE` |

Cost-stack status for all active reach rows:

| Item | Status |
| --- | --- |
| Option bid/ask crossing cost | known for sampled Deribit legs; not assembled into stored synthetic bid/ask |
| Event-market bid/ask and visible depth | known for active Polymarket token books |
| Event fees | unavailable in collected artifact |
| Expected slippage and depth beyond top level | estimated/unavailable; book levels are visible but not consumed by existing pipeline |
| Hedge legging reserve | unavailable |
| Expiry mismatch | known: Deribit `2026-12-25 08:00 UTC` vs event `2027-01-01 05:00 UTC` |
| Timestamp mismatch | known: event observes any one-minute candle through deadline; Deribit settles at expiry instant |
| Settlement-index mismatch | known: Binance BTC/USDT high/low vs Deribit BTC index |
| Strike approximation error | known for sampled spreads; max ramp error can be material |
| Duplicated collateral or margin burden | unavailable |
| Stale-data risk | estimated; source timestamps differ |
| Maximum residual terminal loss | unavailable for touch payoff under static terminal spread |

## 6. Static Hedge Witnesses

These are **not executable scanner recommendations**. They are manual witnesses showing why the static terminal spread grammar is insufficient for the active Polymarket contracts.

Deribit option quotes below are top-of-book ticker fields from 2026-07-18 around 19:30 UTC. Existing collector marks are separate and must not be called executable.

### Witness A: $70k / $75k Call Spread vs $70k Touch

Candidate: `2467210`, "Will Bitcoin reach $70,000 by December 31, 2026?"

Event evidence:

- Polymarket YES top-of-book: `0.70 / 0.71`.
- Visible YES top level: bid size `1181.67`, ask size `203.89`.
- Resolution: YES if any Binance BTC/USDT one-minute candle high reaches threshold before the deadline.

Static terminal spread witness:

- Buy `BTC-25DEC26-70000-C` at ask `0.0775` BTC.
- Sell `BTC-25DEC26-75000-C` at bid `0.0515` BTC.
- Crossing debit: `0.0260` BTC.
- At sampled underlying about `$65,582`, approximate debit is `$1,705`; normalized by `$5,000` width, proxy cost is about `$0.34` per `$1` terminal payoff.

Terminal payoff:

Intended terminal digital threshold for comparison: `$70,000`, matching the event threshold. The listed spread is not centered around that threshold; it is lower-bounded at the threshold and ramps above it from `$70,000` to `$75,000`.

Normalized terminal ramp formula, with `S_T` as Deribit expiry settlement:

```text
V_A(S_T) = min(max((S_T - 70000) / 5000, 0), 1)
D_A(S_T) = 1{S_T >= 70000}
```

For the terminal digital approximation alone, the pointwise error over the transition interval is `|V_A(S_T) - D_A(S_T)|`. It is `1.00` at exactly `$70,000` if the terminal digital includes equality, and otherwise has supremum `1.00` immediately above `$70,000`. The earlier midpoint error of `0.50` at `$72,500` is only one sample point; it is not the maximum for this one-sided spread.

| BTC at Deribit expiry | Normalized spread payoff | Terminal digital at/above $70k | Error |
| ---: | ---: | ---: | ---: |
| $65,000 | 0.00 | 0.00 | 0.00 |
| $70,000 | 0.00 | 1.00 | 1.00 |
| $72,500 | 0.50 | 1.00 | 0.50 |
| $75,000 | 1.00 | 1.00 | 0.00 |
| $85,000 | 1.00 | 1.00 | 0.00 |

Rejection reason: the vertical-spread approximation error above is a terminal-payoff shape error. The separate and more important mismatch is touch versus terminal: even a well-quoted terminal call spread does not pay if BTC touched $70k earlier and finished below the spread at Deribit expiry. It also ignores the Binance/Deribit index mismatch and the 6 day 21 hour expiry gap.

### Witness B: $140k / $150k Call Spread vs $150k Touch

Candidate: `701491`, "Will Bitcoin reach $150,000 by December 31, 2026?"

Event evidence:

- Polymarket YES top-of-book: `0.026 / 0.029`.
- Visible YES top level: bid size `137.06`, ask size `25.75`.
- Resolution: YES if any Binance BTC/USDT one-minute candle high reaches threshold during the stated window.

Static terminal spread witness:

- Buy `BTC-25DEC26-140000-C` at ask `0.0011` BTC.
- Sell `BTC-25DEC26-150000-C` at bid `0.0006` BTC.
- Crossing debit: `0.0005` BTC.
- At sampled underlying about `$65,582`, approximate debit is `$32.79`; normalized by `$10,000` width, proxy cost is about `$0.0033` per `$1` terminal payoff.

Terminal payoff:

Intended terminal digital threshold for comparison: `$150,000`, matching the event threshold. The listed spread is not centered around that threshold; it is upper-bounded at the threshold and ramps below it from `$140,000` to `$150,000`.

Normalized terminal ramp formula, with `S_T` as Deribit expiry settlement:

```text
V_B(S_T) = min(max((S_T - 140000) / 10000, 0), 1)
D_B(S_T) = 1{S_T >= 150000}
```

For the terminal digital approximation alone, the pointwise error over the transition interval is `|V_B(S_T) - D_B(S_T)|`. It has supremum `1.00` immediately below `$150,000`; if the digital is strict `S_T > 150000`, the maximum is also `1.00` at `$150,000`. The midpoint error of `0.50` at `$145,000` is not the maximum because the target threshold is at the upper strike, not centered in the spread.

| BTC at Deribit expiry | Normalized spread payoff | Terminal digital at/above $150k | Error |
| ---: | ---: | ---: | ---: |
| $130,000 | 0.00 | 0.00 | 0.00 |
| $140,000 | 0.00 | 0.00 | 0.00 |
| $145,000 | 0.50 | 0.00 | 0.50 |
| $150,000 | 1.00 | 1.00 | 0.00 |
| $160,000 | 1.00 | 1.00 | 0.00 |

Rejection reason: the vertical-spread approximation error above is separate from the dominant touch-versus-terminal mismatch. The apparent cheapness of far-OTM terminal call spreads is not a tradable edge against a touch contract. Touch probability can be materially higher than terminal probability. The static spread can lose after a valid Polymarket YES event if BTC later falls back below the terminal threshold before Deribit expiry.

### Witness C: $190k / $200k Call Spread vs $200k Touch

Candidate: `701486`, "Will Bitcoin reach $200,000 by December 31, 2026?"

Event evidence:

- Polymarket YES top-of-book: `0.022 / 0.023`.
- Visible YES top level: bid size `410.66`, ask size `7695.75`.
- Resolution: YES if any Binance BTC/USDT one-minute candle high reaches threshold during the stated window.

Static terminal spread witness:

- Buy `BTC-25DEC26-190000-C` at ask `0.0004` BTC.
- Sell `BTC-25DEC26-200000-C` at bid `0.0002` BTC.
- Crossing debit: `0.0002` BTC.
- At sampled underlying about `$65,582`, approximate debit is `$13.12`; normalized by `$10,000` width, proxy cost is about `$0.0013` per `$1` terminal payoff.

Terminal payoff:

Intended terminal digital threshold for comparison: `$200,000`, matching the event threshold. The listed spread is not centered around that threshold; it is upper-bounded at the threshold and ramps below it from `$190,000` to `$200,000`.

Normalized terminal ramp formula, with `S_T` as Deribit expiry settlement:

```text
V_C(S_T) = min(max((S_T - 190000) / 10000, 0), 1)
D_C(S_T) = 1{S_T >= 200000}
```

For the terminal digital approximation alone, the pointwise error over the transition interval is `|V_C(S_T) - D_C(S_T)|`. It has supremum `1.00` immediately below `$200,000`; if the digital is strict `S_T > 200000`, the maximum is also `1.00` at `$200,000`. The midpoint error of `0.50` at `$195,000` is not the maximum because the target threshold is at the upper strike, not centered in the spread.

| BTC at Deribit expiry | Normalized spread payoff | Terminal digital at/above $200k | Error |
| ---: | ---: | ---: | ---: |
| $180,000 | 0.00 | 0.00 | 0.00 |
| $190,000 | 0.00 | 0.00 | 0.00 |
| $195,000 | 0.50 | 0.00 | 0.50 |
| $200,000 | 1.00 | 1.00 | 0.00 |
| $210,000 | 1.00 | 1.00 | 0.00 |

Rejection reason: the vertical-spread approximation error above is separate from the dominant touch-versus-terminal mismatch. The hedge is terminal and capped, while the event is first-passage/touch. It also relies on far-OTM option quotes with very small BTC premiums where tick size, stale quotes, and size constraints need a dedicated executable-cost stack.

## 7. Recurring Rejection Reasons

1. Touch/path-dependent payoff instead of terminal settlement.
2. Binance BTC/USDT one-minute candle high/low resolution versus Deribit BTC index settlement.
3. Deribit year-end 2026 option expiry is December 25, 2026 08:00 UTC, not the Polymarket December 31, 2026 23:59 ET deadline.
4. Existing collector stores marks and probability estimates, not depth-aware synthetic bid/ask.
5. Full fee, slippage, legging, collateral, and margin facts are not in the current evidence artifact.
6. Some active markets are conditional or nonfinancial, such as "before GTA VI" or El Salvador holdings value.
7. Closed/archived candidates have stale/no executable event books.

## 8. Qualifying-Market Frequency And Observed Depth

The broad fresh Gamma scan found at least 13 active BTC price-threshold markets with live Polymarket top-of-book/depth around year-end 2026, plus the `573656` $150k "hit by" market and a conditional $1m-before-GTA market.

However, the count of active contracts matching the charter's v0.1 terminal universe is **zero** in this run. The recurring set is useful for research, but it is not the chartered terminal-payoff set.

Observed event-side depth was nontrivial in several active touch markets:

- $70k reach: top ask size about `203.89`.
- $80k reach: top ask size about `4800.50`.
- $85k reach: top ask size about `23430.32`.
- $150k reach: top ask size about `25.75`.
- $200k reach: top ask size about `7695.75`.

These sizes are visible CLOB book sizes, not guaranteed fill sizes. No claim is made that these prices are executable after fees, slippage, legging, or venue constraints.

## 9. Missing Capabilities For A Credible Stage 1 Scanner

1. A deterministic `EventContractSpec` schema that rejects touch/path-dependent contracts unless a separate barrier-hedging charter exists.
2. A Polymarket adapter that stores question, full description, token IDs, CLOB book levels, source timestamps, accepting-order state, fees, and collateral facts.
3. A Deribit adapter path that stores bid/ask/depth for selected legs, not only `mark_price`.
4. A settlement compatibility engine for event source, calculation window, timezone, expiry timestamp, and index methodology.
5. A hedge compiler that returns `NOT_SAFELY_HEDGEABLE` for touch, conditional, or source-mismatched contracts.
6. A synthetic bid/ask calculator that uses correct buy/sell book sides and size constraints.
7. A conservative cost stack: fees, spread crossing, slippage, legging risk, stale-data reserve, duplicated collateral/margin burden, and settlement/basis reserve.
8. Frozen snapshot format and replay tests covering quote type labels and abstention reasons.

## 10. Continuation Recommendation

Recommendation: `NARROW_AND_REPEAT`.

Why not `GO`:

- Recurring BTC price-threshold contracts exist, but today's active sample is mostly touch/path-dependent, not terminal.
- Apparent option/event discrepancies do not survive payoff review because a static terminal spread is not the same instrument as a first-passage touch contract.
- Full executable synthetic bid/ask and collateral/cost stack are not yet captured in repository artifacts.

Why not `STOP`:

- Polymarket CLOB depth and Deribit option top-of-book are obtainable from public endpoints.
- Deribit has listed BTC strikes around many observed thresholds.
- A narrower terminal-contract scan could still pass if the market universe appears.

Recommended next repeat:

```text
Terminal-only repeat with a frozen Polymarket and Deribit bid/ask/depth witness.
Search only active binary BTC contracts whose resolution text says YES/NO based on BTC being above/below K at a single explicit timestamp.
Reject "hit", "reach", "dip", "any point", "before", conditional, and 50/50 fallback wording before hedge compilation.
Collect Polymarket CLOB books and Deribit ticker/books into one frozen JSON witness.
```

Touch/barrier replication remains out of scope for this continuation. It may be proposed later only as a separate charter decision with its own hedge grammar, cost stack, and residual-risk acceptance criteria.

## 11. Confidence And Evidence Gaps

Confidence: medium-high that the current active/recent BTC price-threshold universe is dominated by touch/path-dependent contracts; medium that a narrower future terminal-only universe may be sparse on Polymarket.

Evidence gaps:

- No live active terminal BTC above/below contract was found in this run.
- Fee and collateral facts were not collected.
- Deribit depth beyond ticker top-of-book was not normalized into hedge-size availability.
- No historical performance or fill simulation is available; local backtest has no resolved questions.
- Existing scan's "tradeable after costs" means "after spread proxy", not executable hedge tradeability.

## 12. Compact Contract Provenance

This appendix records enough source identity to reproduce the three static witness claims without committing local raw artifacts. Polymarket fields are from the public Gamma market objects observed during the Stage 0 revision pass. CLOB YES token IDs are the first entry in each market's `clobTokenIds`, matching `outcomes = ["Yes", "No"]`.

| Witness | Polymarket slug / source ID | Market / condition ID | YES token ID used for CLOB witness | Deadline and timezone | Resolution source and calculation pointer | Payout mapping |
| --- | --- | --- | --- | --- | --- | --- |
| A | `will-bitcoin-reach-70000-by-december-31-2026-from-june-8` | market `2467210`; condition `0x7b9072e6a9cdcf022c4f098564e8ee612d544e179e4a33dcc2790fbaa778daa8` | `95532524407959903145510583684979049735028502452973932716346555811355282494630` | `2027-01-01T05:00:00Z`, equivalent to Dec 31, 2026 23:59 ET market deadline | Binance BTC/USDT one-minute candle `High` at `https://www.binance.com/en/trade/BTC_USDT`; YES if any final one-minute high from market creation through deadline is greater than or equal to `$70,000`; other exchanges/pairs excluded | Polymarket binary YES pays `1` if condition resolves YES and `0` otherwise; NO is the complement; denomination is the market's dollar stablecoin payout convention |
| B | `will-bitcoin-reach-150000-by-december-31-2026-557-246-971` | market `701491`; condition `0xa7b594ae07d5c1590fa86028fcc2f8705990437237416556c05837a08b2e1cda` | `9408196828451163378822245032645030045707991112669125056198742225498158094445` | `2027-01-01T05:00:00Z`, equivalent to Dec 31, 2026 23:59 ET market deadline | Binance BTC/USDT one-minute candle `High`; YES if any final one-minute high between Nov 24, 2025 14:00 ET and Dec 31, 2026 23:59 ET is greater than or equal to `$150,000`; other exchanges/pairs excluded | Polymarket binary YES pays `1` if condition resolves YES and `0` otherwise; NO is the complement; denomination is the market's dollar stablecoin payout convention |
| C | `will-bitcoin-reach-200000-by-december-31-2026-752-232-389` | market `701486`; condition `0xac32e73aa9e0dae801d88d4f81efd2ef3fa0f04b815f3a0e74426f0762e668cd` | `61368943128255287414565270336856615453000675377332178800733742873558311943412` | `2027-01-01T05:00:00Z`, equivalent to Dec 31, 2026 23:59 ET market deadline | Binance BTC/USDT one-minute candle `High`; YES if any final one-minute high between Nov 24, 2025 14:00 ET and Dec 31, 2026 23:59 ET is greater than or equal to `$200,000`; other exchanges/pairs excluded | Polymarket binary YES pays `1` if condition resolves YES and `0` otherwise; NO is the complement; denomination is the market's dollar stablecoin payout convention |

Deribit normalization convention used in section 6:

- Instruments are BTC European call options expiring `2026-12-25 08:00 UTC`; Deribit instrument metadata for each witness leg reports `contract_size = 1.0`, `base_currency = BTC`, `quote_currency = BTC`, and `settlement_currency = BTC`.
- Ticker prices are BTC-denominated option premiums. The report's debit examples convert BTC premium to an approximate USD debit using sampled BTC spot, then divide by the USD strike width as a proxy cost per `$1` normalized terminal payoff.
- The terminal ramp formulas in section 6 are normalized dollar-payoff shape witnesses: `min(max((S_T - K_low) / (K_high - K_low), 0), 1)`. They are not a complete Deribit settlement, fee, collateral, or size model.
- The static witness uses top-of-book bid/ask only. It does not normalize Deribit book depth, legging risk, settlement reserve, or the BTC cash-settlement mechanics needed for an executable scanner.

## Coordination Status

```text
COORDINATION STATUS
Agreement: aligned
Compared: charter, packet, code paths, commands, evidence
Disagreement: none
Evidence gap: no active terminal BTC above/below contract found; no full executable synthetic bid/ask or full cost stack
Ownership overlap: intentional base from PR #5384 only; no charter edits; report path owned by this Stage 0 branch
Risk if unresolved: scanner could mistake touch-probability differences or mark-derived spread proxies for executable terminal hedge edge
Recommended default: NARROW_AND_REPEAT; terminal-only repeat with a frozen Polymarket and Deribit bid/ask/depth witness
Founder decision required: no
```

## Agent Continuity

```text
AGENT CONTINUITY
- Safe to switch agents? YES
- Exact reason: Work is docs-only, bounded to the Stage 0 feasibility report, with no product/frontier/UI/execution changes.
- If YES: exact handoff payload required: branch codex/hedge-backed-liquidity-stage0; report path docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md; evidence artifacts listed in section 2; recommendation NARROW_AND_REPEAT.
```
