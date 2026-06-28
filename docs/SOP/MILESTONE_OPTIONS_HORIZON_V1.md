# Milestone: Options Horizon v1

**Milestone ID:** `options_horizon_v1`  
**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**As-of:** 2026-06-26

---

## What this milestone is

**Goal:** A trader opens **Options Horizon** in MSOS — a chart-first workspace separate from Strategy Lab / PPE — to see where price has been, where options imply it is going, draw a **region** (price × time), and get implied mass + simulated expression preview **without execution**.

**Tagline:** *See where price has been, where options imply it's going, and box the region you care about.*

**Not** PPE implied lab. **Not** live order routing.

---

## Product placement

| Layer | Owner |
|-------|--------|
| **MSOS shell** | Options Horizon route, region draw UX, workflow save |
| **PPE core** | Implied distribution, forward curve, surface archive math |
| **Link** | Display API only — no TypeScript math port |

Hierarchy: **MSOS → Options Horizon** (peer to Strategy Lab) → consumes PPE display payloads.

---

## Workstreams (chapter sequence)

| # | Workstream | Chapter | Outcome |
|---|------------|---------|---------|
| **H0** | Charter | `horizon_charter_v1` | Canon docs + backlog |
| **H1** | Surface archive | `horizon_surface_archive_v1` | Daily options surface snapshots + query API |
| **H2** | Chart payload | `horizon_chart_payload_v1` | JSON contract + Streamlit spike |
| **H3** | Read-only chart | `horizon_readonly_chart_v1` | MSOS `/options-horizon` spot + volume + forward |
| **H4** | Region + bridge | `horizon_region_draw_v1`, `horizon_expression_bridge_v1` | Box draw, implied mass, Strategy Lab deep-link — **COMPLETE** (v1 spike) |
| **H4c** | Chart polish | `horizon_chart_polish_v1` | Implied overlay, axis/legend parity, expiry selector — **CHARTERED** |
| **H4d** | Region workflow | `horizon_region_workflow_v1` | MSOS persistence for RegionIntent — **CHARTERED** |
| **H5** | Deferred overlays | `horizon_replay_scrubber_v1`, etc. | Replay after ≥30d archive; liquidation TBD |

---

## Gating — when BUILD may be SELECTED

Do **not** promote Horizon chapters to `READY` until:

1. [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md) workstreams materially complete
2. [`ppe_tradeable_universe_v1`](POST_PPE_TRADEABLE_UNIVERSE_V1_SELECTION.md) **COMPLETE**
3. [`ppe_equity_options_v1`](POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md) **COMPLETE**
4. Ideal: ≥1 **strong+** validation signal on chart-first pre-trade research

**Priority:** `low` / `focusPlaybookTier: P2` — after active wedge and universe infra.

---

## Milestone complete when

1. User opens Options Horizon; sees ≥30d BTC price + volume + forward implied overlay.
2. Daily surface archive running; replay scrubber when ≥30 days of history exist.
3. User draws a region; sees implied mass % + simulation payoff + ≥1 suggested expression.
4. Region saves to workflow or exports; "Open in Strategy Lab" pre-fills asset/expiry.
5. Zero execution paths in UI, API, or copy ([`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md)).

---

## Explicitly not this milestone

- Live execution / broker keys / order routing
- Third-party historical options backfill (archive-first only)
- Liquidation heatmap (deferred chapter)
- Multi-asset beyond BTC wedge (until tradeable universe tier-1 crypto batch)
- Folding Horizon into PPE implied lab UI

---

## How BUILD agents use this

- **Scope test:** Does the slice advance Options Horizon per [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)?
- **Layer rule:** Math in `ppe-core`; chart UX in `msos-shell`; no TS distribution port.
- **Copy rule:** "Suggested expression," "simulation" — never "we placed your trade."
