# Options Horizon chart polish v1 — SELECTION

**Chapter:** `horizon_chart_polish_v1`  
**Display name:** Options Horizon chart polish (implied overlay + axis parity)  
**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**Milestone:** [`MILESTONE_OPTIONS_HORIZON_V1.md`](MILESTONE_OPTIONS_HORIZON_V1.md)  
**Relay plan:** [`PHASE_PLANS/horizon_chart_polish_v1_relay.json`](PHASE_PLANS/horizon_chart_polish_v1_relay.json)  
**Sprint:** [`SPRINT_OPTIONS_HORIZON_CHART_POLISH_V1.md`](SPRINT_OPTIONS_HORIZON_CHART_POLISH_V1.md)  
**Vision:** [`CHART_DISPLAY_CONTRACT_V1.md`](../VISION/OPTIONS_HORIZON/CHART_DISPLAY_CONTRACT_V1.md)

---

## Status

**CHARTERED** 2026-06-27 — closes the v1 spike vs milestone visual gap; **LOW / P2** side channel.

**First slice:** `Horizon-ChartPolish-Control-Slice001`

**Promote to `READY` when:** operator prioritizes Options Horizon over active meta-infra / tier-1 asset batches (not auto-selected).

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Operator feedback | Current `/options-horizon` chart is functional but not credible — minimal SVG, no implied overlay |
| Data already shipped | `payload.implied.prices_usd` + `pdf_pct` exist; MSOS never renders them |
| Pattern reuse | Strategy Lab `LabeledDistributionChart` + `chartAxisDisplay` — no new math |
| Priority | LOW — after `ppe_asset_display_parity_v1` and enablement pipeline; does not preempt trader-workflow relay |

**Blocked until:** ~~`horizon_expression_bridge_v1` **COMPLETE**~~ **satisfied** 2026-06-26.

---

## Acceptance (chapter)

1. Time×price chart uses axis grid, tick labels, and legend per [`CHART_DISPLAY_CONTRACT_V1.md`](../VISION/OPTIONS_HORIZON/CHART_DISPLAY_CONTRACT_V1.md).
2. Options-implied distribution visible at selected expiry (companion panel via `LabeledDistributionChart`; optional contour on main chart).
3. Expiry selector wired to `chart.json?expiry_ts=` without TypeScript math.
4. Region draw → implied mass preview → Strategy Lab deep-link preserved.
5. Evidence doc COMPLETE; milestone witness items for chart/implied overlay checked.

---

## Non-goals

- Replay scrubber, liquidation overlay, outcome ghosts (remain deferred H5)
- MSOS workflow persistence for RegionIntent (`horizon_region_workflow_v1` — separate chapter)
- Multi-asset Horizon
- PPE engine changes unless required for expiry list in payload

---

## Next chapter (same program)

[`POST_OPTIONS_HORIZON_REGION_WORKFLOW_V1_SELECTION.md`](POST_OPTIONS_HORIZON_REGION_WORKFLOW_V1_SELECTION.md) — persist RegionIntent to MSOS theses/workflow store.
