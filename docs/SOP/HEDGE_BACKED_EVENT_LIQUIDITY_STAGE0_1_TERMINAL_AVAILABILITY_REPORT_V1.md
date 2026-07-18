# Hedge-backed event liquidity Stage 0.1 terminal availability report v1

**Status:** Stage 0.1 witness complete  
**As-of:** 2026-07-18 20:54-20:59 UTC  
**Thread role:** `codex_build`  
**Repository:** `DanielTabakman/Probability-prediction-engine`  
**Base commit:** `1fd8dc45011398e9f67ec2b19b9bc2014be4ba75`  
**Branch:** `codex/stage0-1-terminal-availability`  
**Parent charter:** [`../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md`](../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md)  
**Accepted Stage 0 report:** [`HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md`](HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md)  
**Recommendation:** `WATCH_SPARSE_MARKET`

## 1. Executive Answer

Polymarket does not currently show a recurring, usable active universe of BTC binary contracts that resolve only by BTC being above or below a threshold at one explicit timestamp.

The Stage 0.1 terminal-only witness found:

| Count | Result |
| ---: | --- |
| 1,100 | Polymarket market objects discovered across active pagination plus targeted BTC searches |
| 8 | BTC price-threshold markets frozen as candidates |
| 2 | Current active BTC price-threshold markets in the frozen candidate set |
| 0 | Qualifying terminal `above` / `below` BTC markets |
| 8 | Rejected before hedge compilation |
| 0 | Synthetic bid/ask witnesses constructed |

The active candidates were both rejected before hedge compilation:

1. `540844`, "Will bitcoin hit $1m before GTA VI?" - rejected as touch/path-dependent, conditional, and not terminal `above` / `below`.
2. `573656`, "Will Bitcoin hit $150k by December 31, 2026?" - rejected as touch/path-dependent and not terminal `above` / `below`.

Deribit public option metadata and order-book depth are obtainable. The final witness saw 870 listed BTC option instruments and froze displayed Deribit depth for the only current active BTC threshold candidate with comparable listed strikes, `BTC-25DEC26-140000-C` and `BTC-25DEC26-150000-C`. That evidence supports later executable data collection, but it does not authorize a Stage 1 hedge scanner because the Polymarket semantic gate did not pass.

## 2. Evidence Date And Commands

Commands run from `C:\Users\USER\Desktop\Probability-prediction-engine`:

```powershell
git fetch origin main --prune
git checkout -B codex/stage0-1-terminal-availability origin/main
Test-Path docs/VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md
Test-Path docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md
python scripts/collect_cross_venue_snapshot.py --max-questions 20 --polymarket-limit 300
python scripts/run_cross_venue_scan.py --latest-snapshot --top 20
python scripts/run_cross_venue_tradeability.py --latest-snapshot
python -m pytest -q tests/test_cross_venue_tradeability.py tests/test_cross_venue_export.py
python scripts/hedge_backed_event_stage0_1_terminal_witness.py --include-closed --limit 200 --max-candidates 20 --clob-depth 10 --deribit-depth 5
```

Generated artifacts:

| Artifact | Path | Result |
| --- | --- | --- |
| Cross-venue snapshot | `artifacts/cross_venue_snapshots/2026-07-18/ppe_cross_venue_prob_panel_205443Z.csv` | 1 matched row, the active $150k hit market |
| Cross-venue scan | `artifacts/cross_venue_reports/latest.md`, `artifacts/cross_venue_reports/latest.json` | 1 ranked row |
| Tradeability report | `artifacts/cross_venue_tradeability/latest_report.md`, `artifacts/cross_venue_tradeability/latest_summary.json` | 1 row flagged by spread proxy |
| Stage 0.1 witness | `artifacts/hedge_backed_event_liquidity/stage0_1_terminal_availability_witness_20260718T205907Z.json` | 8 BTC price-threshold candidates, 0 terminal qualifiers |

Validation:

```text
python -m pytest -q tests/test_cross_venue_tradeability.py tests/test_cross_venue_export.py
11 passed in 1.43s

python -m pytest -q tests/test_cross_venue_tradeability.py
8 passed
```

## 3. Data-Quality And Quote-Type Audit

The existing cross-venue pipeline still uses Polymarket probability fields and Deribit probability/mark-derived estimates for scan and tradeability research. The Stage 0.1 witness added a narrow public-data freeze for the terminal-only question:

| Source | Frozen field | Quote label |
| --- | --- | --- |
| Polymarket Gamma `outcomePrices` | YES/NO probability array | market estimate, not executable by itself |
| Polymarket Gamma `bestBid` / `bestAsk` | top-of-book market fields | top-of-book indicator |
| Polymarket CLOB `/book` | displayed token-level bids and asks | displayed depth |
| Deribit `get_instruments` | expiry, strike, option type, multiplier metadata | instrument metadata |
| Deribit `get_order_book` | best bid/ask and displayed depth | top-of-book and displayed depth |
| Deribit `mark_price` | order-book response field | mark only, not executable |
| Existing tradeability `spread_proxy` | probability spread-cost proxy | proxy, not executable hedge price |

No marks, mids, modeled probabilities, or spread proxies are called executable in this report.

## 4. Contract Taxonomy

| Taxon | Found in Stage 0.1 witness? | Handling |
| --- | ---: | --- |
| Terminal `YES if BTC above K at explicit timestamp` | 0 | No hedge compilation |
| Terminal `YES if BTC below K at explicit timestamp` | 0 | No hedge compilation |
| Touch / hit / break by deadline | 6 | Rejected before hedge compilation |
| Conditional touch with fallback or non-BTC timing | 1 | Rejected before hedge compilation |
| Scalar / range BTC price market | 1 | Rejected before hedge compilation |

## 5. Candidate Compatibility Matrix

| # | Polymarket ID | Current? | Candidate | Event bid/ask | Semantic outcome | Deribit evidence | Result |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `540844` | yes | Will bitcoin hit $1m before GTA VI? | `0.498 / 0.499` | Touch/path-dependent, conditional, not terminal `above`/`below` | No comparable listed strike around $1m in selected Deribit chain | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 2 | `573656` | yes | Will Bitcoin hit $150k by December 31, 2026? | `0.035 / 0.036` | Touch/path-dependent, not terminal `above`/`below`; Binance 1m high semantics | `BTC-25DEC26-140000-C` `0.0008 / 0.0011`; `BTC-25DEC26-150000-C` `0.0006 / 0.0011`; 5 displayed levels captured per side | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 3 | `76` | no | Will $BTC break $20k before 2021? | closed `0 / 1` | Historical break/touch before deadline | Expired event; no hedge witness | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 4 | `25367` | no | Will $BTC break $50k before April 1st, 2021? | closed `0 / 1` | Historical break/touch before deadline | Expired event; no hedge witness | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 5 | `8939` | no | Will $BTC break $25k before March 1st? | closed `0 / 1` | Historical break/touch before deadline | Expired event; no hedge witness | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 6 | `36` | no | What will the price of Bitcoin be on November 4th, 2020? | closed `0 / 1` | Scalar/range-style market, not binary YES/NO terminal | Expired event; no hedge witness | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 7 | `63` | no | Will BTC break $15k before 2021? | closed `0 / 1` | Historical break/touch before deadline | Expired event; no hedge witness | `REJECT_NOT_SAFELY_HEDGEABLE` |
| 8 | `103` | no | Will $BTC break $20k before Thanksgiving? | closed `0 / 1` | Historical break/touch before deadline | Expired event; no hedge witness | `REJECT_NOT_SAFELY_HEDGEABLE` |

Cost and compatibility status:

| Item | Stage 0.1 status |
| --- | --- |
| Option bid/ask crossing cost | Known only as displayed Deribit top-of-book for `573656`; not assembled into synthetic quote because semantic gate failed |
| Event-market bid/ask and depth | Known for active candidates through Gamma and CLOB books |
| Event fees | Gamma fee fields and fee schedule frozen when present; full account-specific fee/collateral treatment not proven |
| Expected slippage and displayed depth | Displayed depth frozen; slippage model unavailable |
| Hedge legging reserve | Unavailable |
| Expiry mismatch | Known for `573656`: Polymarket deadline `2027-01-01T05:00:00Z`; Deribit matched option expiry `2026-12-25 08:00 UTC` |
| Timestamp mismatch | Known for active hit markets: any earlier qualifying candle versus terminal expiry instant |
| Settlement-index mismatch | Known for `573656`: Binance BTC/USDT 1m high versus Deribit BTC index option settlement |
| Strike approximation error | Not applicable after semantic rejection; no terminal digital spread witness accepted |
| Duplicated collateral or margin burden | Unavailable |
| Stale-data risk | Present; frozen timestamps differ by venue |
| Maximum residual terminal loss | Not computed because no candidate passed semantic compatibility |

## 6. Hedge Witnesses

No synthetic bid/ask witness was constructed.

This is intentional. The Stage 0.1 gate requires terminal `above` or `below` semantics before hedge compilation. Every frozen BTC price-threshold candidate failed that semantic gate. Constructing a normalized call-spread or put-spread synthetic quote for these markets would risk presenting a terminal hedge as evidence against a touch, conditional, historical, or scalar payoff.

For `573656`, the witness froze Deribit displayed depth for `BTC-25DEC26-140000-C` and `BTC-25DEC26-150000-C`. Those books prove that executable-looking option-side data is obtainable, not that the touch payoff is hedgeable by a static terminal spread.

## 7. Recurring Rejection Reasons

1. Active BTC threshold contracts use "hit" or "break" language, not terminal `above` / `below` language.
2. The active $150k market resolves on any Binance BTC/USDT one-minute candle high before the deadline, making it path-dependent.
3. The active $1m market is conditional on GTA VI timing and includes non-BTC event semantics.
4. Older archived BTC threshold markets are also break/touch markets and have no live executable event books.
5. Scalar/range-style BTC price markets do not provide binary YES/NO terminal payoff mapping.
6. The existing scan/tradeability path can flag a probability gap or spread proxy for a rejected market; that must not be treated as executable hedge evidence.

## 8. Qualifying-Market Frequency And Observed Depth

Qualifying terminal-market frequency in this run: `0 / 8` frozen BTC price-threshold candidates, and `0 / 2` current active BTC price-threshold candidates.

Observed active event-side quote evidence:

| Market | Gamma bid/ask | CLOB depth status |
| --- | --- | --- |
| `540844` $1m before GTA VI | `0.498 / 0.499` | YES and NO token books returned 10 bid and 10 ask levels |
| `573656` $150k by Dec 31 2026 | `0.035 / 0.036` | YES and NO token books returned displayed depth; frozen artifact stores 10 levels per side where available |

Observed active hedge-side evidence:

| Market | Deribit instrument | Top of book | Displayed depth |
| --- | --- | --- | --- |
| `573656` | `BTC-25DEC26-140000-C` | `0.0008 / 0.0011` BTC | 5 bid and 5 ask levels frozen |
| `573656` | `BTC-25DEC26-150000-C` | `0.0006 / 0.0011` BTC | 5 bid and 5 ask levels frozen |

These are displayed public books, not guaranteed fills after fees, slippage, legging, stale-data reserve, settlement basis reserve, or collateral cost.

## 9. Missing Capabilities Before Stage 1

1. Evidence of a recurring active Polymarket universe of terminal BTC `above` / `below` contracts.
2. A deterministic event-contract schema and parser that rejects touch, hit, break, dip, scalar, conditional, and fallback markets before any hedge compilation.
3. Full Polymarket contract semantics, fee, collateral, accepting-order, and CLOB depth snapshots in a replayable format.
4. Deribit option metadata and order-book depth snapshots matched only after semantic and settlement compatibility pass.
5. Settlement compatibility checks for event source, timestamp, timezone, calculation window, expiry, and index.
6. Synthetic bid/ask construction using correct executable book sides and displayed depth, with no mark/mid/proxy substitution.
7. Fee, slippage, legging, duplicated-collateral, stale-data, and settlement-basis reserves.

## 10. Recommendation

Recommendation: `WATCH_SPARSE_MARKET`.

Do not proceed to Stage 1 now. The active Polymarket BTC threshold universe remains observable and liquid enough to monitor, and synchronized public Polymarket/Deribit book evidence appears obtainable. But the terminal `above` / `below` universe was empty in the fresh witness, so a hedge compiler or executable synthetic scanner would have no qualifying market set to operate on.

Do not stop the Polymarket branch entirely. The data path is useful, and a terminal strip may appear later. The correct next state is a watcher/repeat posture: rerun this Stage 0.1 witness periodically or before any future Stage 1 selection, and proceed only if multiple active terminal BTC `above` / `below` markets pass semantic and settlement compatibility.

Touch/barrier replication remains outside scope.

## 11. Coordination Status

```text
COORDINATION STATUS
Agreement: aligned
Compared: charter, accepted Stage 0 report, Stage 0 packet, code paths, commands, evidence
Disagreement: none
Evidence gap: no active terminal BTC above/below contracts found; no synthetic executable bid/ask could be constructed because semantic compatibility never passed
Ownership overlap: none detected; docs-only report plus research-only witness script/test, no frontier/queue/UI/product path touched
Risk if unresolved: Stage 1 could mistake touch/path-dependent probability gaps or spread proxies for executable terminal hedge edge
Recommended default: WATCH_SPARSE_MARKET
Founder decision required: no
```

## 12. Agent Continuity

```text
AGENT CONTINUITY
- Safe to switch agents? YES
- Exact reason: Work is research-only and bounded to Stage 0.1 terminal availability evidence. No UI, frontier, queue, manifest, order, wallet, custody, treasury, or customer-funds paths were changed.
- If YES: exact handoff payload required: branch codex/stage0-1-terminal-availability; report path docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_1_TERMINAL_AVAILABILITY_REPORT_V1.md; witness script scripts/hedge_backed_event_stage0_1_terminal_witness.py; focused parser tests in tests/test_cross_venue_tradeability.py; final artifact artifacts/hedge_backed_event_liquidity/stage0_1_terminal_availability_witness_20260718T205907Z.json; recommendation WATCH_SPARSE_MARKET.
```
