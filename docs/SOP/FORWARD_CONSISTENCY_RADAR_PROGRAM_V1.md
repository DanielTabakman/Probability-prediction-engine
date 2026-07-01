# Forward consistency radar — program v1

**Module ID:** `forward_consistency`  
**Registry:** [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md)  
**Class:** `CONSISTENCY`  
**Pillars:** EDGE + LEGIBILITY  
**First ship-to:** OPERATOR → Monitor hook at T4  
**As-of:** 2026-06-29  
**Status:** **SELECTION COMPLETE** (relay ch.1–2) — chapters queued **PLANNED** after trader-workflow supply refresh

---

## Agent load bundle

| Role | Path |
|------|------|
| Program (charter) | this file |
| SELECTION ch.1 | [`POST_PPE_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md`](POST_PPE_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md) |
| SELECTION ch.2 | [`POST_MSOS_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md`](POST_MSOS_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md) |
| Resolve | `python scripts/resolve_sop.py --module forward_consistency --json` |

---

## North star

**Show which enabled asset/expiry pairs have internally consistent executable forwards, which look wrong, and whether wrongness is bad data or a persistent dislocation — without execution language.**

Not an arbitrage detector. A **data-trust and internal-consistency** surface for testing edge hypotheses.

---

## Integration tier charter

| Field | Value |
|-------|--------|
| **Current tier** | T1 (single-cell API + Strategy Lab panel) |
| **Target tier (this program)** | T3 |
| **T2 intent** | Internal MSOS heatmap + detail + debug drawer |
| **T3 intent** | Daily snapshots for persistence questions only |
| **T4 intent** | Optional Monitor trust signal — **defer** until trader validation |

---

## Prerequisites

| Prerequisite | Status |
|--------------|--------|
| Engine + status enum | **SHIPPED** — `src/engine/forward_consistency.py` |
| Single-cell boundary | **SHIPPED** — `/ppe-display-api/forward-consistency.json` |
| Strategy Lab panel | **SHIPPED** — `ForwardConsistencyPanel` |
| Trust surface v1 | **COMPLETE** |
| Multi-asset catalog | In progress |

---

## Exclusions

| Excluded | Why |
|----------|-----|
| Live execution / order routing | Separate future milestone |
| New venue adapters in v1 | Deribit path only |
| PPE math in TypeScript | Layer rule |
| Merge into distribution histogram | Sibling module; deep-link only |
| “Arbitrage opportunity” primary branding | Semantic / trust rule |
| Full order-book archival | Archive charter — see below |

---

## Copy (canonical)

- **Module name:** Forward consistency  
- **Badges:** No arb · Watch · Possible dislocation · Bad data · Not comparable  
- **Footer:** Research only — executable synthetic forward vs future/perp after spreads and estimated costs. Not price. Not a trade signal.

---

## Chapter sequence (relay)

| # | Chapter | Priority | Blocked until | Tier | Delivers |
|---|---------|----------|---------------|------|----------|
| 1 | `ppe_forward_consistency_radar_v1` | MEDIUM | trust surface COMPLETE | T1 | Quality flags, dashboard payload, fixture, `dashboard.json` |
| 2 | `msos_forward_consistency_radar_v1` | MEDIUM | ch.1 merged | T2 | `/forward-consistency` — summary, heatmap, detail, debug |
| 3 | `ppe_forward_consistency_collector_v1` | LOW · sideChannel | ch.2 + archive charter approved | T3 | Daily snapshot + read-latest |
| 4 | `msos_forward_consistency_history_v1` | LOW | ≥7d snapshots | T3–T4 | Event tape + timeline |

**Minimum working radar = chapters 1–2.**

---

## T3 archive charter (proposed — approve before collector slice)

| Field | Proposal |
|-------|----------|
| **Hypothesis** | Distinguish **persistent** consistency dislocations from **one-off bad quotes**; support operator trust in Strategy Lab data |
| **Consumer** | Operator first; optional Monitor summary at T4 |
| **Granularity** | One row per **enabled asset × expiry** per run; status, quality flags, net/gross edge USD, as_of — **not** full option chain |
| **Frequency** | Daily on VM loop host (after cross-venue window) |
| **Retention** | 90 days raw daily; optional weekly rollup later |
| **Trigger** | Scheduled task; diff engine emits events only on **status change** or WATCH persist ≥N runs |
| **Non-goals** | No tick data; no all-strike storage; no auto-trade signals |

---

## Data contracts (extend existing)

Build on `ForwardConsistencyCheck`; do not fork parallel types.

```text
ForwardConsistencyQualityFlag:
  STALE_QUOTES | WIDE_SPREAD | INSUFFICIENT_DEPTH | MISSING_LEG | EXPIRY_MISMATCH

ForwardConsistencyHeatmapCell:
  asset_id, expiry_date, status, net_edge_usd, quality_flags[], as_of_utc

ForwardConsistencyDashboardPayload:
  kind: forward_consistency_dashboard
  schema_version: 1
  summary: { assets_checked, expiries_checked, watch_count, possible_count, bad_data_count }
  cells: ForwardConsistencyHeatmapCell[]

ForwardConsistencyEvent:   # chapter 4
  asset_id, expiry_date, from_status, to_status, net_edge_usd, duration_s, reason, quality_flags[]
```

USD edges in v1 (engine native). Defer `confidence_score` until rule is defined.

### API paths

| Path | Status |
|------|--------|
| `GET /ppe-display-api/forward-consistency.json?asset=&expiry=` | **Live** |
| `GET /ppe-display-api/forward-consistency/dashboard.json` | **Planned** ch.1 |

Fixture: `fixtures/forward_consistency_dashboard_v1.json` (planned)

---

## MSOS surface (chapter 2)

**Route:** `/forward-consistency`  
**Nav:** Internal / ops first  
**v0 views:** summary cards, heatmap, selected detail, raw JSON drawer  
**Deferred:** dislocation tape, timeline (chapter 4)

---

## Operator artifacts (chapter 3+)

| Artifact | Path |
|----------|------|
| Snapshot | `artifacts/forward_consistency_snapshots/` |
| Collector | `scripts/collect_forward_consistency_snapshot.py` (planned) |
| Ops | `FORWARD_CONSISTENCY_COLLECTOR_OPS_V1.md` (planned) |

Pattern: [`CROSS_VENUE_COLLECTOR_OPS_V1.md`](CROSS_VENUE_COLLECTOR_OPS_V1.md)

---

## Relay slice sketch (chapter 1)

| Slice | Layer | Delivers |
|-------|-------|----------|
| `PPE-FCR-Control-Slice001` | CONTROL | SELECTION, evidence stub |
| `PPE-FCR-Core-Slice002` | `ppe-core` | Quality flags, matrix builder |
| `PPE-FCR-UI-Slice003` | `ppe-ui` | `dashboard.json` + fixture + tests |
| `PPE-FCR-Closeout-Slice004` | CONTROL | Evidence COMPLETE |

---

## Success criteria

**Chapters 1–2:**

1. Fixture dashboard validates in pytest  
2. Heatmap from one API fetch (enabled assets × expiries)  
3. Cell click → synthetic/future/edge/flags/reason  
4. Operator distinguishes BAD_DATA vs WATCH without opening Strategy Lab  

**Chapters 3–4:**

5. Daily snapshots on VM; dashboard reads latest  
6. Event tape shows transitions including WATCH persisted  

---

## Sibling links

| Module | Link |
|--------|------|
| `implied_distribution` | Deep-link → Strategy Lab `?asset=&expiry=` |
| `options_horizon` | Forward context only — no merge |
| `expression_planner` | No v1 link |
| Trust surface | Reuse trust copy where thin-chain applies |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-29 | v1 draft program + archive charter proposal |
| 2026-06-29 | Operator SELECTION — relay ch.1–2 approved; queued after horizon nav |
