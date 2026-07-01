# Exposure path save v1 (preview)

**Parent:** [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md) · [`EXPOSURE_MENU_SCAN_COMPARE_V1.md`](EXPOSURE_MENU_SCAN_COMPARE_V1.md)  
**Module:** `exposure_menu`  
**Tier:** T4 preview (browser localStorage — same pattern as thesis/expression preview)  
**As-of:** 2026-07-01  
**Status:** LIVE (preview)

---

## Intent

Let a trader **bookmark one exposure path** from `/exposure` for later review — without claiming execution or recommendation.

One saved path per browser (`msos.exposure_path.preview.v1`). Not server workflow store yet.

---

## UX

| Element | Behavior |
|---------|----------|
| **Save for later** | On each path card; marks active when same path/asset/direction/horizon |
| **Banner** | Shows saved path label + Reopen / Clear |
| **Copy** | “Path saved to your workspace for later — comparison only, not a trade.” |

---

## Witness

Index ETF exposure bindings: `python -m scripts.witness_exposure_menu --group equity_index` (mocked CI) or `--live` for vendor fetch.

---

## Not now

- Server-side workflow store sync
- Multiple saved paths / compare bookmarks
- Command Center card (defer until server persistence)
