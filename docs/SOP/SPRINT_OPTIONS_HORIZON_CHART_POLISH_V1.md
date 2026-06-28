# Options Horizon chart polish v1 — relay sprint spec

**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**SELECTION:** [`POST_OPTIONS_HORIZON_CHART_POLISH_V1_SELECTION.md`](POST_OPTIONS_HORIZON_CHART_POLISH_V1_SELECTION.md)  
**Vision:** [`CHART_DISPLAY_CONTRACT_V1.md`](../VISION/OPTIONS_HORIZON/CHART_DISPLAY_CONTRACT_V1.md)  
**Prior chapter:** `horizon_expression_bridge_v1` (COMPLETE)  
**Baseline:** **`main`**

---

## Sprint intent

Upgrade `/options-horizon` from v1 SVG spike to **credible chart UX**: axis parity with Strategy Lab, visible options-implied distribution, expiry selector — **display only**, no TypeScript math.

**Priority:** LOW / P2 — side channel; promote to `READY` explicitly.

---

## Technical constraints (binding)

| Rule | Detail |
|------|--------|
| Layer | `msos-shell` only unless expiry list requires tiny payload extension in `ppe-ui` |
| No TS math | Render `prices_usd` / `pdf_pct` arrays from Python JSON |
| Reuse | `LabeledDistributionChart`, `chartAxisDisplay`, existing horizon APIs |
| Copy | Simulation-only; no execution language |

---

## Slice acceptance

### Horizon-ChartPolish-Control-Slice001 (CONTROL)

- SELECTION + sprint + evidence stub + relay plan committed

### Horizon-ChartPolish-Product-Slice002 (MSOS_UI)

- Time×price chart: grid, axis ticks, legend, improved volume/forward styling
- Expiry selector → refetch `chart.json?expiry_ts=`
- Responsive layout shell for chart + panel

### Horizon-ChartPolish-Product-Slice003 (MSOS_UI)

- Companion `LabeledDistributionChart` panel for `payload.implied`
- Optional implied-at-expiry contour on main chart (display mapping only)
- Region preview panel styling aligned with Strategy Lab panels

### Horizon-ChartPolish-Closeout-Slice004 (CONTROL)

- Evidence COMPLETE; update [`OPTIONS_HORIZON_V1_EVIDENCE_STATUS.md`](OPTIONS_HORIZON_V1_EVIDENCE_STATUS.md) follow-on section
- Milestone chart witness items checked

---

## Witness (chapter close)

- [ ] `/options-horizon` — grid, axes, legend, implied panel visible
- [ ] Expiry change updates chart + implied panel
- [ ] Region draw → implied mass → Strategy Lab link
- [ ] `python scripts/run_pushable_gate.py` green on touched paths
