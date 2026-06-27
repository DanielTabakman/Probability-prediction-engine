# Options Horizon program v1

**Purpose:** Canonical map for **Options Horizon** — chart-first region thesis workspace in MSOS, separate from Strategy Lab / PPE.

**As-of:** 2026-06-26 · **Milestone:** [`MILESTONE_OPTIONS_HORIZON_V1.md`](MILESTONE_OPTIONS_HORIZON_V1.md)

**Vision contracts:** [`docs/VISION/OPTIONS_HORIZON/`](../VISION/OPTIONS_HORIZON/)

---

## North star

**See where price has been, where options imply it's going, and box the region you care about — then preview payoff and suggested expressions in simulation.**

Not a broker. Not TradingView clone. Not PPE distribution histogram.

---

## Prerequisites (before first BUILD slice SELECTED)

| Chapter | Status | Delivers |
|---------|--------|----------|
| `ppe_equity_options_v1` | **COMPLETE** | Second venue proof |
| `ppe_tradeable_universe_v1` | **IN PROGRESS** | Catalog + registry v2 |

---

## Chapter sequence (relay order)

| # | Chapter | Priority | Blocked until | Delivers |
|---|---------|----------|---------------|----------|
| 0 | `horizon_charter_v1` | LOW | — | Charter docs + backlog |
| 1 | **`horizon_surface_archive_v1`** | LOW | charter + universe v1 COMPLETE | Daily surface JSON archive + query module + API |
| 2 | `horizon_chart_payload_v1` | LOW | surface archive COMPLETE | Chart JSON contract + Streamlit spike |
| 3 | `horizon_readonly_chart_v1` | LOW | chart payload COMPLETE | MSOS `/options-horizon` read-only chart |
| 4a | `horizon_region_draw_v1` | LOW | readonly chart COMPLETE | Box tool + RegionIntent save |
| 4b | `horizon_expression_bridge_v1` | LOW | region draw COMPLETE | Implied mass, payoff preview, Strategy Lab link |
| 5a | `horizon_replay_scrubber_v1` | LOW · DEFER | ≥30d archive + H3 COMPLETE | Timeline scrub of past implied surfaces |
| 5b | `horizon_liquidation_overlay_v1` | LOW · DEFER | validation + vendor | Liquidation levels on historical pane |
| 5c | `horizon_outcome_ghosts_v1` | LOW · DEFER | replay scrubber | Post-expiry implied vs realized |

---

## Operator artifacts

| Artifact | Command / path |
|----------|----------------|
| Surface snapshot | `python scripts/collect_horizon_surface_snapshot.py` → `artifacts/horizon_surface_archive/` |
| Surface API | `GET /ppe-display-api/horizon/surface.json?asset=BTC&as_of=...` |
| Chart payload API | `GET /ppe-display-api/horizon/chart.json?asset=BTC&expiry_ts=...` |
| Region schema | [`REGION_INTENT_SCHEMA_V1.md`](../VISION/OPTIONS_HORIZON/REGION_INTENT_SCHEMA_V1.md) |

**Daily ritual (after H1 ships):** run surface collector on schedule (same pattern as [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md)).

---

## Historical options strategy

**Archive-first:** daily snapshots from deploy date forward. No third-party backfill in v1.

- Replay scrubber ships when ≥30 calendar days of archive exist.
- Archive also feeds PPE research and cross-venue backtest consumers.

Contract: [`SURFACE_ARCHIVE_CONTRACT_V1.md`](../VISION/OPTIONS_HORIZON/SURFACE_ARCHIVE_CONTRACT_V1.md).

---

## What the program excludes

| Excluded | Why |
|----------|-----|
| Live execution | Separate future milestone |
| PPE math in TypeScript | Layer rule |
| Merging into implied lab | Horizon owns time × price grammar |
| Liquidation v1 | New data vendor; deferred |
| Bulk Deribit history backfill | Cost; archive-first sufficient for v1 |

---

## Source docs (by chapter)

| Chapter | SELECTION | Evidence |
|---------|-----------|----------|
| charter | [`POST_OPTIONS_HORIZON_CHARTER_V1_SELECTION.md`](POST_OPTIONS_HORIZON_CHARTER_V1_SELECTION.md) | — |
| surface archive | TBD | TBD |
| chart payload | TBD | TBD |
| readonly chart | TBD | TBD |
| region + bridge | TBD | TBD |

---

## Success criteria (program-level)

1. **Archive:** Collector + query API green; dated folders under `artifacts/horizon_surface_archive/`.
2. **Chart:** MSOS route shows spot, volume, forward overlay for BTC.
3. **Region:** Box → implied mass + ≥1 suggested expression (simulation).
4. **Bridge:** Deep-link to Strategy Lab with asset/expiry context.
5. **Honesty:** No execution language in UI or API.
