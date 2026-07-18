# Hedge-backed event liquidity Stage 0.1 terminal availability report v1

**Status:** Stage 0.1 witness revised after independent review  
**As-of:** 2026-07-18 21:20-21:21 UTC  
**Thread role:** `codex_build`  
**Repository:** `DanielTabakman/Probability-prediction-engine`  
**Base commit:** `1fd8dc45011398e9f67ec2b19b9bc2014be4ba75`  
**Branch:** `codex/stage0-1-terminal-availability`  
**Parent charter:** [`../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md`](../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md)  
**Accepted Stage 0 report:** [`HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md`](HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md)  
**Recommendation:** `STOP_POLYMARKET_BRANCH`

## 1. Executive Answer

The revised Stage 0.1 witness found zero qualifying BTC terminal contracts in active markets and zero qualifying BTC terminal contracts in the closed/resolved coverage that the public Gamma search returned. `WATCH_SPARSE_MARKET` is therefore not supported by this evidence: a sparse valid market requires at least one genuine terminal contract, and this run found none.

`STOP_POLYMARKET_BRANCH` means:

- stop investing in a Polymarket-specific hedge scanner or implementation branch;
- preserve the reusable public-data collection and parser code;
- allow an inexpensive future availability check to see whether genuine terminal BTC contracts later appear;
- do not authorize Stage 1.

The possibility that a terminal contract may appear someday is not evidence that a sparse valid market currently exists. Touch, barrier, path-dependent, conditional, scalar, fallback, or ambiguous contracts remain outside scope and must not be replicated as terminal hedges.

## 2. Coverage And Counts

The witness used active Gamma pagination plus targeted public Gamma searches for BTC-related terms, with `--include-closed --limit 200 --max-candidates 20`. The large JSON artifact was regenerated under the required path:

`artifacts/hedge_backed_event_liquidity/terminal_availability/stage0_1_terminal_availability_witness_20260718T212113Z.json`

This raw artifact is not committed because it is large live-market evidence. The compact reproducibility record is in Appendix A below.

| Coverage item | Count / range |
| --- | ---: |
| Active general Polymarket market objects paginated | 1,000 |
| Closed/resolved general market objects returned by targeted searches | 100 |
| General Polymarket market objects discovered | 1,100 |
| BTC price-threshold candidates frozen | 7 |
| Active BTC price-threshold candidates frozen | 2 |
| Closed/resolved BTC price-threshold candidates frozen | 5 |
| Closed/resolved candidate date span observed | 2020-11-26 to 2021-04-01 deadlines |
| Recent-history lookback definition | closed/resolved targeted Gamma search, max 200 per search term, inspected for the current run |
| Terminal qualifiers, active category | 0 |
| Terminal qualifiers, closed/resolved category | 0 |
| Canonical `ELIGIBLE` outcomes | 0 |
| Canonical `WATCH` outcomes | 0 |
| Canonical `REJECT` outcomes | 7 |
| Synthetic hedge witnesses constructed | 0 |

The 1,100 general market objects were not 1,100 semantically inspected BTC contracts. They were the public coverage envelope used to find the seven BTC threshold candidates that were then parsed and frozen.

## 3. Structured Contract Gate

The revised witness no longer uses loose keywords as the final eligibility gate. `classify_market` now builds a deterministic `EventContractSpec`-style parse with these fields:

| Field | Required for `ELIGIBLE` |
| --- | --- |
| underlying | exactly one BTC underlying |
| comparator | exactly one of `above` or `below` |
| threshold | exactly one BTC price threshold |
| resolution timestamp | one explicit date and time |
| timezone | explicit timezone |
| resolution source/index | explicit source or index |
| calculation method | explicit terminal calculation method |
| YES payout | explicit `$1` payout |
| NO payout | explicit `$0` payout |
| ambiguity/fallback flags | none |

Keywords still provide rejection hints for touch, barrier, scalar, conditional, or fallback language, but final eligibility comes only from validated structured fields. Missing, conflicting, or ambiguous fields produce `WATCH` or `REJECT`; the witness never infers eligibility.

Canonical outcomes:

- `ELIGIBLE`: all structured fields pass and no ambiguity flags are present.
- `WATCH`: BTC threshold-shaped market, but required structured evidence is missing rather than contradicting the gate.
- `REJECT`: contradictory, path-dependent, conditional, scalar, non-BTC-secondary, fallback, nonstandard-payout, or otherwise unsafe semantics.

## 4. Execution Order

Semantic contract parsing now runs before Deribit leg selection or order-book collection. The regenerated witness did not call Deribit order-book matching for the seven rejected candidates, and every candidate records:

`synthetic_not_constructed_semantic_gate_failed`

Deribit public metadata remains a separately labelled data-availability probe only:

| Probe | Result |
| --- | ---: |
| Deribit BTC option instruments observed | 872 |
| Probe label | `data_availability_only_not_hedge_compilation` |

This is not hedge compilation, candidate matching, or Stage 1 authorization.

## 5. Candidate Compatibility Matrix

| # | Market ID | Current? | Candidate | Semantic outcome | Canonical result |
| ---: | --- | --- | --- | --- | --- |
| 1 | `573656` | yes | Will Bitcoin hit $150k by December 31, 2026? | Touch/path-dependent Binance 1m candle high; missing explicit `$1/$0` payout text | `REJECT` |
| 2 | `540844` | yes | Will bitcoin hit $1m before GTA VI? | Touch/path-dependent; secondary GTA condition; fallback 50-50 condition; missing `above`/`below`; missing explicit payout | `REJECT` |
| 3 | `76` | no | Will $BTC break $20k before 2021? | Break/touch before deadline; missing source/index and explicit payout | `REJECT` |
| 4 | `25367` | no | Will $BTC break $50k before April 1st, 2021? | Break/touch before deadline; missing source/index and explicit payout | `REJECT` |
| 5 | `8939` | no | Will $BTC break $25k before March 1st? | Break/touch before deadline; missing source/index and explicit payout | `REJECT` |
| 6 | `63` | no | Will BTC break $15k before 2021? | Break/touch before deadline; missing source/index, calculation method, and explicit payout | `REJECT` |
| 7 | `103` | no | Will $BTC break $20k before Thanksgiving? | Break/touch before deadline; missing source/index and explicit payout | `REJECT` |

## 6. Validation

Focused parser and witness tests:

```text
python -m pytest -q tests/test_cross_venue_tradeability.py tests/test_cross_venue_export.py
24 focused tradeability/parser tests passed in 1.62s for tests/test_cross_venue_tradeability.py; cross-venue export remains covered by the pushable gate.
```

Focused lint:

```text
python -m ruff check scripts/hedge_backed_event_stage0_1_terminal_witness.py tests/test_cross_venue_tradeability.py
All checks passed.
```

The focused tests include negative coverage for two thresholds, both `above` and `below`, date without time/timezone, two observation times, two observation dates, conflicting timezones, missing source/index, alternative venues, fallback source language, conflicting named indexes, secondary non-BTC condition, nonstandard payout, fallback or ambiguous resolution, and source wording containing `by`, `high`, or `low` that is not path-dependent. They also preserve coherent terminal timestamp and `Coinbase BTC/USD spot price index` source phrases.

## 7. Recommendation

Recommendation: `STOP_POLYMARKET_BRANCH`.

Do not proceed to Stage 1. Stop the Polymarket-specific hedge scanner or implementation branch because active and closed/resolved evidence found no qualifying terminal BTC contract universe. Preserve the reusable public-data code and the narrow structured parser so a cheap future availability check can be run before any new selection.

Touch/barrier replication remains prohibited.

## Appendix A. Compact Provenance For Frozen Candidates

Fetch timestamp for the regenerated witness: `2026-07-18T21:20:21.577137+00:00`; per-candidate Gamma/CLOB fetch timestamps are recorded in the regenerated artifact. Exact questions are listed below. Exact resolution text is the Gamma `description` field at the stable source pointer when present; active candidates also have the precise source/index and calculation rule extracted below.

| Market | Condition | Question ID | YES token | NO token | Slug / pointer | Created | Deadline / timezone | Source / rule | Payout | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `573656` | `0x02deb9538f5c123373adaa4ee6217b01745f1662bc902e46ac92f3fe6f8741e8` | `0x5ffb6001758f989dc5a6a9ce6dd78554784e022036e2e7dab37038add592f2a8` | `93694900555669388759405753550770573998169287228984912881955464376232163096213` | `55119388124180116303253993098894090042427725500010038140578121972388485050538` | `will-bitcoin-hit-150k-by-december-31-2026` | `2025-08-07T14:34:08.095389Z` | `December 31, 2026 11:59PM ET` | Binance BTC/USDT 1m candle final high; path-dependent | missing explicit `$1/$0` | `REJECT` |
| `540844` | `0xbb57ccf5853a85487bc3d83d04d669310d28c6c810758953b9d9b91d1aee89d2` | `0x7e4ff7b7fdfe7d1fbc6c0e2a7626ae4fc8d62f3848a5e601d511a51bdfa51f09` | `105267568073659068217311993901927962476298440625043565106676088842803600775810` | `91863162118308663069733924043159186005106558783397508844234610341221325526200` | `will-bitcoin-hit-1m-before-gta-vi-872-424` | `2025-05-02T15:24:45.04244Z` | `July 31, 2026 11:59 PM ET` | Binance BTCUSDT 1m candle final high plus GTA release condition/fallback | fallback 50-50; missing explicit `$1/$0` | `REJECT` |
| `76` | `0xa670159e0a8868ed1ca0013cf026805c1c5ffbf778a1d5030218471620211222` | not returned | `24680891386899004239422217017747530833228850388439331073974543214962789676595` | `83973309932681465959484168662520374150245867260821232128773724666573303624136` | `will-btc-break-20k-before-2021` | `2020-11-06T21:50:06.493Z` | `January 1st, 2021 12:00am EST` | stable Gamma description pointer; break/touch wording | missing explicit `$1/$0` | `REJECT` |
| `25367` | `0xe97a28fbd11bc755d4dff8a710d64b1a9ffd10324adbdcf391da64da60a96e2e` | not returned | `6691484561624346413649341413488271135999574859299388605100127341090504781015` | `70580131683183266462078834111066430299653156454501725753019074800892827343672` | `will-btc-break-50k-before-april-1st-2021` | `2021-01-04T17:20:08.085Z` | `April 1st, 2021 12:00am EST` | stable Gamma description pointer; break/touch wording | missing explicit `$1/$0` | `REJECT` |
| `8939` | `0x9cff735d7e2d1c7ed06cdc30f206e66dbf8331c493f0d260f6f777b6a7f72908` | not returned | `111442005067379510832855695143617202880785476284619910510703686643727966998475` | `9192758429981042942584759348647002322418162537159342549043196464861358439245` | `will-btc-break-25k-before-march-1st` | `2020-12-16T17:05:22.378Z` | `March 1st, 2021 12:00am EST` | stable Gamma description pointer; break/touch wording | missing explicit `$1/$0` | `REJECT` |
| `63` | `0x7b02c10a310f38be83ae0dbbb5caa96722a69ae1488b1ac5c2003bccd70ac021` | not returned | `81489679527234870363655397325586438057198526422665424757123802116412728199295` | `49766556628062086013472587707046514950870842420956058689393245878472316276945` | `will-btc-break-15k-before-2021-1` | `2020-10-22T16:50:03.826Z` | `Dec 31, 2020 11:59 PM ET` | stable Gamma description pointer; break/touch wording | missing explicit `$1/$0` | `REJECT` |
| `103` | `0xb787f500a7b6e105eb6eddcb47df6a6de87ea4f26059e917daea1bbf54c8accb` | not returned | `86454146934806610986347752380863288016151372034608409853443136263523534610246` | `96454313312833889175528293976423410488772363048009139816268524349544941728710` | `will-btc-break-20k-before-thanksgiving` | `2020-11-18T17:50:08.3Z` | `November 26th, 2020 12:00am EST` | stable Gamma description pointer; break/touch wording | missing explicit `$1/$0` | `REJECT` |

Question text:

| Market | Exact question |
| --- | --- |
| `573656` | Will Bitcoin hit $150k by December 31, 2026? |
| `540844` | Will bitcoin hit $1m before GTA VI? |
| `76` | Will $BTC break $20k before 2021? |
| `25367` | Will $BTC break $50k before April 1st, 2021? |
| `8939` | Will $BTC break $25k before March 1st? |
| `63` | Will BTC break $15k before 2021? |
| `103` | Will $BTC break $20k before Thanksgiving? |

## Coordination Status

```text
COORDINATION STATUS
Agreement: aligned after revision
Compared: charter, accepted Stage 0 report, Stage 0 packet, PR review, code paths, commands, evidence
Disagreement: none
Evidence gap: no active or closed/resolved qualifying terminal BTC above/below contracts found; no synthetic executable bid/ask could be constructed because semantic compatibility never passed
Ownership overlap: none detected; docs-only report plus research-only witness script/test, no frontier/queue/UI/product path touched
Risk if unresolved: Stage 1 could mistake touch/path-dependent probability gaps or spread proxies for executable terminal hedge edge
Recommended default: STOP_POLYMARKET_BRANCH
Founder decision required: no
```

## Agent Continuity

```text
AGENT CONTINUITY
- Safe to switch agents? YES
- Exact reason: Work is research-only and bounded to Stage 0.1 terminal availability evidence. No UI, frontier, queue, manifest, order, wallet, custody, treasury, or customer-funds paths were changed.
- If YES: exact handoff payload required: branch codex/stage0-1-terminal-availability; report path docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_1_TERMINAL_AVAILABILITY_REPORT_V1.md; witness script scripts/hedge_backed_event_stage0_1_terminal_witness.py; focused parser tests in tests/test_cross_venue_tradeability.py; regenerated artifact path artifacts/hedge_backed_event_liquidity/terminal_availability/stage0_1_terminal_availability_witness_20260718T212113Z.json; recommendation STOP_POLYMARKET_BRANCH.
```
