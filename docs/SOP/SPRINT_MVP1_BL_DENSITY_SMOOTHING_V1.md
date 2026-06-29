# MVP1 B–L density smoothing v1 — relay sprint spec

**SELECTION:** [`POST_MVP1_BL_DENSITY_SMOOTHING_V1.md`](POST_MVP1_BL_DENSITY_SMOOTHING_V1_SELECTION.md)  
**Baseline:** **`main`**

## Sprint intent

Apply a **smoothing pass** to Breeden–Litzenberger market-implied density before chart/export normalization — reducing spiky second-derivative artifacts on thin strike grids.

## Slices

| Slice | Plane | Delivers |
|-------|-------|----------|
| MVP1-BLDensitySmooth-Control-Slice001 | EVIDENCE | Charter + evidence stub |
| MVP1-BLDensitySmooth-Product-Slice002 | PRODUCT (`PPE_CORE`) | `smooth_bl_density()` + wire into `market_implied_density_breeden_litzenberger` |
| MVP1-BLDensitySmooth-Product-Slice003 | PRODUCT (`PPE_UI`) | Chart + export use smoothed BL when enabled |
| MVP1-BLDensitySmooth-Closeout-Slice004 | EVIDENCE | Evidence COMPLETE |

## Witness

- [ ] Smoothed BL integrates to ~1 on fixture marks  
- [ ] Raw vs smoothed toggle or label in implied lab trust strip  
- [ ] Export CSV reflects smoothed BL row when computed  
