# Exposure menu program v1

**Module ID:** `exposure_menu`  
**Registry:** [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md)  
**Class:** `EXPOSURE_PATH` — “What ways exist to get exposure to this asset?”  
**Pillars:** WORKFLOW (primary) + LEGIBILITY (trust labels per path)  
**First ship-to:** TRADER  
**As-of:** 2026-06-30  
**Status:** v0 **LIVE** — scan/compare follow-on chartered in [`EXPOSURE_MENU_SCAN_COMPARE_V1.md`](EXPOSURE_MENU_SCAN_COMPARE_V1.md)

---

## North star

**User says “I want NVIDIA exposure” → MSOS shows a menu of paths** (own shares, LEAPS, spreads, …) with honest tradeoffs — not a single optimized trade, not a distribution chart.

Standalone lens at **`/exposure`**. Separate from Strategy Lab (thesis/disagreement) and Expression planner (structure fit under belief).

---

## User experience (v0)

| Element | Behavior |
|---------|----------|
| **Route** | `/exposure` — secondary nav (with Options Horizon) |
| **Intake** | Asset picker + direction (Long / Short / Neutral); optional horizon chip (`Any` \| `3m` \| `12m`) |
| **Output** | Card grid — each **ExposurePath** with rail badge, cost hint, leverage shape, pros/cons, trust pill |
| **Sort** | Simplest first (spot → defined-risk options → aggressive options) |
| **Copy** | “Paths for comparison only — not recommendations” |
| **Deep-link** | Options paths → Strategy Lab `?asset=` (expiry/strike params later) |

**Not on this screen:** belief sliders, disagreement readout, 4-leg universal strategy editor.

---

## Core entity: `ExposurePath`

Distinct from **Expression** (thesis-confirmed structure). Fields:

| Field | Meaning |
|-------|---------|
| `path_id` | Stable catalog id |
| `instrument_rail` | `spot_equity` \| `listed_options` \| `etf_proxy` \| `perp` |
| `label` | User-facing path name |
| `direction` | `long` \| `short` \| `neutral` |
| `headline` | One-line payoff shape |
| `capital_shape` | e.g. “100% at risk on spot move”, “Premium at risk only” |
| `cost_hint_usd` | Spot × illustrative size or option net premium |
| `leverage` | `none` \| `defined` \| `high` |
| `time_bound` | `none` \| `dated` |
| `liquidity` | `high` \| `medium` \| `low` \| `planned` |
| `trust_badge` | `Live` \| `Thin chain` \| `Planned` |
| `pros` / `cons` | Short bullets |
| `legs` | Options paths only |
| `deep_link` | Strategy Lab when rail is options |
| `recommendation_status` | Always `path_not_recommendation` |

---

## Integration tier charter

| Field | Value |
|-------|--------|
| **Current tier** | — (not built) |
| **Target tier (v0 program)** | **T2** |
| **T0** | Types, catalog YAML, fixture JSON, unit tests |
| **T1** | `GET /ppe-display-api/exposure-menu.json` + CLI |
| **T2** | MSOS `/exposure` page + nav link |
| **T3** | Archive — **N/A** until product asks for path cost history |
| **T4** | Save path to workflow store — **defer** v1 |

---

## Prerequisites

| Prerequisite | Status |
|--------------|--------|
| Tradeable universe + asset registry | **COMPLETE** |
| NVDA equity options + spot fetch | **COMPLETE** |
| BTC/ETH multi-asset cache | **COMPLETE** |
| MSOS standalone route pattern (`/options-horizon`) | **COMPLETE** |
| NVIDIA / LEAPS validation signal | Brief exists — [`briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md`](briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md) |

---

## Path catalog

Configured in [`config/exposure_path_catalog.yaml`](../../config/exposure_path_catalog.yaml).

Engine activates paths from catalog + live eligibility (chain depth, horizon, spot quote). Does not combinatorially scan full chain in v0.

### v0 proof assets

| Asset | Rails live in v0 |
|-------|------------------|
| **NVDA** | spot, LEAPS call, bull call spread, near-dated call, OTM call, cash-secured put (short exposure path) |
| **BTC** | spot/index, long call, bull call spread |
| **HYPE** | perp only (Hyperliquid) — [`PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md`](PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md) |

### Planned cards (honest labels, no fake math)

| Rail | v0 posture |
|------|------------|
| `etf_proxy` (e.g. SMH for NVDA) | **Planned** card |
| `perp` (BTC/ETH) | **Planned** until HL chapter ships |
| `perp` (HYPE) | **CHARTERED** → Live mark/funding in [`ppe_hyperliquid_perp_rail_v1`](POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md) |

---

## Code layout (BUILD slices)

| Layer | Path |
|-------|------|
| Catalog | `config/exposure_path_catalog.yaml` |
| Pure engine | `src/engine/exposure_paths.py` |
| Orchestration | `scripts/exposure_path_core.py` |
| CLI | `scripts/find_exposure_paths.py` |
| Boundary | `src/viz/exposure_menu_boundary.py` → `/ppe-display-api/exposure-menu.json` |
| MSOS | `apps/msos-web/src/app/exposure/` |

**Reuses:** `assets_registry`, `fetch_equity_spot`, `fetch_equity_options*`, `app_cache`, Deribit fetch, optional `implied_lab_presets` for leg/cost fill.

**Does not reuse as primary UX:** implied lab state, belief tuning, disagreement hints.

---

## Chapter sequence (relay)

| # | Chapter | Tier | Delivers |
|---|---------|------|----------|
| 1 | **`ppe_exposure_menu_v1`** | T0→T2 | Core + CLI + boundary + MSOS page (NVDA + BTC) |
| 2 | **`ppe_hyperliquid_perp_rail_v1`** | T1→T2 | HYPE Live perp path (Hyperliquid read-only) — [`POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md`](POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md) |

Future (post v0):

| Chapter | Delivers |
|---------|----------|
| **`ppe_exposure_menu_scan_v1`** | Sections, fit lenses, two-path compare — [`EXPOSURE_MENU_SCAN_COMPARE_V1.md`](EXPOSURE_MENU_SCAN_COMPARE_V1.md) **LIVE** |
| `ppe_exposure_menu_nl_v1` | Natural-language intake (“nvidia exposure”) |
| `msos_exposure_menu_save_v1` | Save chosen path — **preview LIVE** [`MSOS_EXPOSURE_PATH_SAVE_V1.md`](MSOS_EXPOSURE_PATH_SAVE_V1.md) |
| `ppe_exposure_menu_universe_v1` | Neutral/hedge catalog + remaining assets (SPY/QQQ/IWM index binding shipped in scan follow-up) |

---

## Exclusions

| Excluded | Why |
|----------|-----|
| Live execution / order routing | Separate milestone |
| “Best trade” / buy language | Semantic rule — paths for comparison |
| Merging into Strategy Lab or Expression planner | Own lens |
| Natural language intake | v1 |
| ETF proxy live pricing | v1 |
| Perp math without vendor | Planned cards only (except HYPE — chartered HL fetch) |
| T3 collector without archive charter | Registry rule |

---

## Copy (canonical)

- **Module name:** Exposure menu (nav: “Get exposure” acceptable)
- **Footer:** Paths for comparison only — simulation and research support, not trade recommendations.
- **Planned rail:** “Not connected yet — shown for context.”

---

## Sibling modules

| Module | Relationship |
|--------|--------------|
| `implied_distribution` | Deep-link target for options inspection — not entry point |
| `expression_planner` | Deeper structure fit after user picks an options path |
| `options_horizon` | Optional later link for time×price framing |
| `discover_asset_data_source` | Preflight when asset has no chain — CLI `next_action: run_discover_first` |

---

## Related docs

| Doc | Role |
|-----|------|
| [`POST_PPE_EXPOSURE_MENU_V1_SELECTION.md`](POST_PPE_EXPOSURE_MENU_V1_SELECTION.md) | SELECTION |
| [`SPRINT_PPE_EXPOSURE_MENU_V1.md`](SPRINT_PPE_EXPOSURE_MENU_V1.md) | Sprint |
| [`PHASE_PLANS/ppe_exposure_menu_v1_relay.json`](PHASE_PLANS/ppe_exposure_menu_v1_relay.json) | Relay plan |
| [`EXPOSURE_MENU_SCAN_COMPARE_V1.md`](EXPOSURE_MENU_SCAN_COMPARE_V1.md) | Scan sections, fit lenses, compare drawer (next UX chapter) |
| [`PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md`](PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md) | HYPE perp rail — exposure-only registry |
| [`MSOS_Market_Interaction_Modes_v0.1.md`](../VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md) | Exposure-first intent (adjacent to Expression Search / Hedging) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-29 | v1 charter — module `exposure_menu`, v0 scope NVDA+BTC, T2 target |
| 2026-06-30 | Link scan/compare follow-on charter; status v0 LIVE |
| 2026-06-30 | Charter `ppe_hyperliquid_perp_rail_v1` — HYPE perp under exposure menu (P2 side channel) |
