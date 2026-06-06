# MVP1 distribution export — SELECTION outcome

**Status:** **SELECTION COMPLETE** 2026-06-05  
**Precondition:** MSOS P4 Strategy Lab chapter **COMPLETE** (or manifest idle) before relay **READY**  
**Prior parallel track:** MSOS Website Program P4 — [`POST_MSOS_P4_STRATEGY_LAB_SELECTION.md`](POST_MSOS_P4_STRATEGY_LAB_SELECTION.md)

## Selected BUILD chapter

| Field | Value |
|-------|--------|
| **Chapter** | MVP1 BTC implied distribution CSV export (Phase 1) |
| **Canon** | [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) — research partner deliverable |
| **Phase plan** | [`PHASE_PLANS/mvp1_distribution_export_relay.json`](PHASE_PLANS/mvp1_distribution_export_relay.json) |
| **Sprint** | [`SPRINT_MVP1_DISTRIBUTION_EXPORT.md`](SPRINT_MVP1_DISTRIBUTION_EXPORT.md) |
| **Evidence** | [`MVP1_DISTRIBUTION_EXPORT_EVIDENCE_STATUS.md`](MVP1_DISTRIBUTION_EXPORT_EVIDENCE_STATUS.md) |

## Why this chapter

External research contact requested **time-series-friendly** distribution statistics for backtesting. Phase 1 delivers an **instant cross-expiry CSV** from distributions the implied lab already computes — mean and quartiles for **lognormal reference** and **Breeden–Litzenberger market-implied** curves across all listed BTC option expiries at the current snapshot.

## Scope (Phase 1)

1. **Engine:** quantile + mean helpers on lognormal and discrete BL density grids.  
2. **Export:** canonical CSV schema (see sprint spec).  
3. **UI:** Streamlit **Download distribution stats (CSV)** on implied lab (private app).  
4. **Tests:** unit coverage for quantile math and serializer shape.

## Out of scope

- Daily historical collector / backfill  
- Multi-asset (ETH, SOL, Hyperliquid)  
- User-belief subjective overlay in export  
- MSOS Next.js download surface

## Relay

| Slice | Plane | Worker |
|-------|-------|--------|
| Control-Slice001 | EVIDENCE | deterministic |
| Product-Slice002 | PRODUCT | `local-agent` (`PPE_CORE`) |
| Product-Slice003 | PRODUCT | `local-agent` (`PPE_UI`) |
| Smoke-Slice004 | EVIDENCE | deterministic |
| Closeout-Slice005 | EVIDENCE | deterministic |

## Operator note

Product slices require **IDE BUILD** → commit → `mark_ide_product_ready.cmd` → `run_ppe_local.cmd` on the local profile. Share the CSV with the research contact from the **private** implied lab after deploy.

## Deferred (Phase 2+)

| Candidate | Notes |
|-----------|--------|
| Daily timeseries collector | SQLite/Parquet + history download |
| Disagreement / width signal columns | Separate research export charter |
| MSOS Strategy Lab download chrome | After PPE export proven on Streamlit |
