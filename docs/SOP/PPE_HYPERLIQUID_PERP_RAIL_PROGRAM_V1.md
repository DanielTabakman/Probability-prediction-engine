# Hyperliquid perp rail program v1

**Chapter:** `ppe_hyperliquid_perp_rail_v1`  
**Parent program:** [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md)  
**Module:** `exposure_menu` — promotes `perp` rail from Planned → Live (read-only)  
**As-of:** 2026-06-30  
**Status:** **CHARTERED** — SELECTION complete; BUILD when relay READY

---

## North star

**Operator spends time with Hyperliquid perp traders → MSOS shows an honest HYPE exposure path** with live mark and funding from Hyperliquid public API — compare vs spot/options on other names — **without** faking options coverage or live execution.

Not Strategy Lab implied distribution. Not asset batch wave 1.

---

## Customer signal

Operator runs recurring conversations with traders who express **HYPE / Hyperliquid perp** interest. They use **perps, not options**. Demand is for legibility and path comparison (“how do I get long HYPE?”), not Breeden–Litzenberger curves.

Validation brief: [`briefs/HYPERLIQUID_PERP_VALIDATION_BRIEF.md`](briefs/HYPERLIQUID_PERP_VALIDATION_BRIEF.md)

---

## Product fit

| Surface | HYPE / Hyperliquid role |
|---------|-------------------------|
| **Exposure menu `/exposure`** | **Primary** — `perp_long` path Live for HYPE |
| **Strategy Lab** | Out of scope — no options chain |
| **Asset batch wave 1** | Out of scope — options witness pipeline |
| **Expression planner** | Honest copy only — HL remains non-options execution rail |
| **Forward consistency** | Phase 2+ — optional perp vs index basis |

---

## Registry model (exposure-only)

HYPE lands as an **enabled registry row** for picker + exposure menu — **not** a tier-1 options batch asset.

```yaml
# config/assets.yaml (merged in BUILD — disabled until witness)
HYPE:
  label: "HYPE (Hyperliquid perp)"
  asset_class: crypto
  tier: extended
  venue: hyperliquid
  hyperliquid_coin: HYPE
  exposure_only: true
  enabled: false
  price_unit: USD
  catalog:
    group: crypto
  trust_notes:
    - "Perp-only on Hyperliquid — no listed options in PPE v1."
    - "Funding and liquidation risk — research path only, no execution."
```

| Flag | Meaning |
|------|---------|
| `exposure_only: true` | Skip options discovery / `witness_asset_catalog` options fetch; use perp witness |
| `venue: hyperliquid` | Routes to `fetch_hyperliquid` — not Deribit/Bybit/equity |

**Do not** add HYPE to [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml) wave 1 chapters.

---

## Data source

| Field | Value |
|-------|--------|
| **Venue** | Hyperliquid public API (no API key for info endpoints) |
| **Fetch module** | `src/data/fetch_hyperliquid.py` (BUILD) |
| **Map** | [`config/asset_venue_source_map.yaml`](../../config/asset_venue_source_map.yaml) → `hyperliquid` |
| **Fields v1** | Mark/mid, 8h funding rate, open interest (when available) |
| **Enable gate** | Live mark + funding returned; no options count |

Reference endpoints (info API): `metaAndAssetCtxs`, `allMids` — document exact paths in sprint evidence.

---

## Exposure path behavior

Promote catalog template `perp_long` ([`config/exposure_path_catalog.yaml`](../../config/exposure_path_catalog.yaml)) for HYPE:

| Field | v0 (Planned) | v1 (this chapter) |
|-------|--------------|-------------------|
| `trust_badge` | Planned | **Live** when HL fetch ok |
| `liquidity` | planned | high / medium from OI heuristic |
| `cost_hint_usd` | empty | illustrative notional × mark |
| `headline` | “not connected yet” | mark + funding in headline or chips |
| `status` envelope | `insufficient_chain` (no options) | **`ok_perp_only`** when perp live |

**Semantic rule:** For `exposure_only` assets, `find_exposure_paths` must **not** require `options_live >= 2`. Perp-only success is valid.

---

## Chapter sequence

| Phase | Chapter | Delivers |
|-------|---------|----------|
| **v1 (this)** | `ppe_hyperliquid_perp_rail_v1` | HYPE registry row + HL fetch + Live perp card on `/exposure` |
| v2 (defer) | `ppe_hyperliquid_perp_rail_v2` | Funding history, basis vs Deribit index, short perp path |
| v3 (defer) | `ppe_hyperliquid_execution_v1` | **Separate SELECTION** — live orders; post-validation |

---

## Prerequisites

| Prerequisite | Status |
|--------------|--------|
| Exposure menu v0 LIVE | **COMPLETE** |
| Tradeable universe + catalog picker | **COMPLETE** |
| `perp_long` catalog template | **COMPLETE** (Planned) |

**Blocked by:** nothing hard.

**Does not block:** asset batch wave 1 batches 2–4, spine closeout, forward-consistency ch.2.

---

## Priority and scheduling

| Field | Value |
|-------|--------|
| **Priority** | **P2 side channel** |
| **Relay posture** | Parallel to wave 1 — run when IDE BUILD slot free |
| **Suggested start** | After wave 1 batch 2 retrospect **or** immediately if operator thread idle |
| **Slice budget** | ~4 product slices + closeout (small chapter) |

---

## Exclusions

| Excluded | Why |
|----------|-----|
| Live execution / wallet connect | Product focus drift guard |
| HYPE options on Derive/PowerTrade | No adapter; discovery blocked today |
| Strategy Lab implied distribution for HYPE | Options math N/A |
| Asset batch enablement ritual | Wrong pipeline |
| Port HL math to TypeScript | Repo layer rule |

---

## Evidence

[`PPE_HYPERLIQUID_PERP_RAIL_V1_EVIDENCE_STATUS.md`](PPE_HYPERLIQUID_PERP_RAIL_V1_EVIDENCE_STATUS.md)

---

## Related docs

| Doc | Role |
|-----|------|
| [`POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md`](POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md) | SELECTION |
| [`SPRINT_PPE_HYPERLIQUID_PERP_RAIL_V1.md`](SPRINT_PPE_HYPERLIQUID_PERP_RAIL_V1.md) | Sprint + acceptance |
| [`PHASE_PLANS/ppe_hyperliquid_perp_rail_v1_relay.json`](PHASE_PLANS/ppe_hyperliquid_perp_rail_v1_relay.json) | Relay plan |
| [`ASSET_BATCH_EXPANSION_POLICY_V1.md`](ASSET_BATCH_EXPANSION_POLICY_V1.md) | HYPE **not** wave 1 |
| [`ASSET_DATA_SOURCE_DISCOVERY_V1.md`](ASSET_DATA_SOURCE_DISCOVERY_V1.md) | Skip for `exposure_only` rows |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-30 | Program chartered — HYPE perp rail under exposure menu; P2 side channel |
