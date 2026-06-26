# PPE equity universe tier-1a v1 — SELECTION

**Chapter:** `ppe_equity_universe_tier1a_v1`  
**Display name:** Equity indices (SPY, QQQ, IWM)  
**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Relay plan:** [`PHASE_PLANS/ppe_equity_universe_tier1a_v1_relay.json`](PHASE_PLANS/ppe_equity_universe_tier1a_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_EQUITY_UNIVERSE_TIER1A_V1.md`](SPRINT_PPE_EQUITY_UNIVERSE_TIER1A_V1.md)

---

## Status

**SELECTED** 2026-06-26 — batch chapter #3 (equity indices).

**Blocked until:** `ppe_tradeable_universe_v1` **COMPLETE**.

**Assets:** SPY, QQQ, IWM

**First slice:** `PPE-EqT1a-Control-Slice001`

---

## Acceptance

1. Registry rows for SPY, QQQ, IWM merged and enabled after witness.
2. Equity fetch + implied distribution witness per ticker.
3. Trust notes for index ETF dividends not modeled.
4. Catalog `equity_index` group populated in MSOS.
5. Evidence COMPLETE.

---

## Next chapter

[`POST_PPE_EQUITY_UNIVERSE_TIER1B_V1_SELECTION.md`](POST_PPE_EQUITY_UNIVERSE_TIER1B_V1_SELECTION.md)
