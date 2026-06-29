# Asset batch expansion policy v1

**Purpose:** One operator phrase → agent executes a **wave** of asset enablement without re-negotiating ritual each time.

**As-of:** 2026-06-29 · **Related:** [`ASSET_DATA_SOURCE_DISCOVERY_V1.md`](ASSET_DATA_SOURCE_DISCOVERY_V1.md) · [`ASSET_ENABLEMENT_RUNBOOK_V1.md`](ASSET_ENABLEMENT_RUNBOOK_V1.md) · [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)

---

## Operator triggers (say any of these)

| Phrase | Wave | Agent does |
|--------|------|------------|
| `asset batch wave 1` / `finish tier-1` / `next tier-1 chapter` | **Wave 1 (~10–30)** | Run next **uncomplete** manifest chapter; one relay slice per session |
| `asset batch wave 2` / `tier-2 batch` / `add 100 assets` | **Wave 2 (~100)** | Next tier-2 chunk (10 ids); repeat until wave target |
| `asset batch wave 3` / `tier-3 batch` / `add 1000 assets` | **Wave 3 (~1000)** | **Blocked** until tier-3 program SELECTION — see §Wave 3 |

**Burst:** `asset batch wave N until blocked` — agent runs consecutive chunks until witness fail, gate fail, or prerequisite missing; then reports stop reason.

---

## Wave map

| Wave | Target enabled | Manifest | Chunk size | PRs per wave |
|------|----------------|----------|------------|--------------|
| **1 — tier-1** | ~25–30 curated | [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml) | 1 relay chapter (3–5 ids) | ~6–8 |
| **2 — tier-2** | ~100 liquid | [`config/assets_tier2_manifest.yaml`](../../config/assets_tier2_manifest.yaml) | 10 ids | ~10 |
| **3 — tier-3** | ~1000 searchable | [`config/assets_tier3_manifest.yaml`](../../config/assets_tier3_manifest.yaml) (future) | 50 ids | ~20 |

**Current live count:** check `python scripts/witness_asset_catalog.py --all-enabled --json` → `enabled_count`.

---

## Prerequisites (hard gates)

### Wave 1 (tier-1)

| Gate | Status check |
|------|--------------|
| Meta infra #1–#3 COMPLETE | [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md) evidence docs |
| `ppe_tradeable_universe_v1` COMPLETE | Dynamic catalog + registry v2 |
| Per-chapter | Prior manifest chapter witness green |

### Wave 2 (tier-2)

All Wave 1 gates **plus:**

| Gate | Delivers |
|------|----------|
| Tier-1 program closeout | ≥20 assets enabled, prod multi-asset witness green |
| Meta infra #4–#7 COMPLETE | Cache ops, trust surface, prod witness at scale |
| MSOS catalog search | Required when enabled count > 50 |
| Tier-2 manifest steward-approved | Rows in `assets_tier2_manifest.yaml` |

### Wave 3 (tier-3)

**Not auto-started.** Requires steward SELECTION for `ppe_tradeable_universe_tier3_v1` (scanner UX, pagination, async warm, rate-limit budget). Wave 3 is a **different product surface** — not “more of the same registry rows.”

---

## Agent ritual (every chunk — no shortcuts)

### 1. Pick work

```bash
# Wave 1: next chapter with status != complete
python scripts/enable_asset_batch.py --manifest-slice <chapter_id> --dry-run

# Wave 2+: next chunk id from manifest waves.tier2.chunks[]
python scripts/enable_asset_batch.py --manifest-slice <chunk_id> --dry-run
```

If dry-run shows `unknown asset_id` → merge manifest templates into `config/assets.yaml` first (`enabled: false`).

### 2. Discover (mandatory per asset)

For each id in chunk:

```bash
python scripts/discover_asset_data_source.py --asset <ID> --json
```

Execute `next_action` from JSON ([`asset-auto-discovery.mdc`](../../.cursor/rules/asset-auto-discovery.mdc)). **Never** ask operator which exchange.

| `next_action` | Agent |
|---------------|-------|
| `enable_existing_row` | Continue to witness |
| `merge_registry_and_enable` | Merge row + venue from discovery |
| `switch_venue_and_enable` | Fix venue (e.g. deribit → bybit) |
| `build_adapter` | Implement adapter slice first; stop chunk if blocking |
| `blocked_no_live_options` | Log skip in evidence; **do not enable** |
| `already_enabled` | Skip |

### 3. Witness + enable

```bash
python scripts/probe_asset_data_source.py --manifest-slice <slice_id> --json
python scripts/enable_asset_batch.py --manifest-slice <slice_id> --dry-run
python scripts/witness_asset_catalog.py --manifest-slice <slice_id> --live
python scripts/enable_asset_batch.py --manifest-slice <slice_id> --apply --live-witness
python scripts/run_pushable_gate.py
```

### 4. Post-enable ops

```bash
python scripts/warm_display_payload_cache.py
python scripts/msos_production_multi_asset_witness.py   # when meta #7 COMPLETE
```

### 5. Close chunk

- Update manifest chapter `status: complete` + evidence doc row
- Commit → push → PR (PPE auto-commit)
- **One chunk per thread** unless operator said `until blocked`

---

## Wave 1 chapter order (default)

Mechanical order from [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md):

1. `ppe_deribit_crypto_tier1_v1` — SOL, BNB, XRP (SOL done; finish BNB/XRP when live)
2. `ppe_equity_universe_tier1a_v1` — SPY, QQQ, IWM
3. `ppe_equity_universe_tier1b_v1` — AAPL, MSFT, AMZN, GOOGL, META
4. `ppe_equity_universe_tier1c_v1` — TSLA, AMD, COIN
5. `ppe_commodity_proxy_tier1_v1` — GLD, SLV, USO

Skip ids with `blocked_no_live_options`; document in chapter evidence.

---

## Wave 2 — tier-2 (~100)

**Scope:** Liquid US equity options (yfinance) + live crypto on wired venues. **Not** full Russell 3000 — curated liquidity floor.

**Liquidity gate (registry merge):**

- Equity: ≥1 monthly expiry, total OI ≥ 100 (matches `fetch_equity_options.py`)
- Crypto: ≥10 live instruments on recommended venue

**Chunk schedule:** 10 ids per PR, grouped by `catalog_group`. Order: indices → mega → sector ETFs → liquid midcaps → crypto extensions.

**Manifest:** [`config/assets_tier2_manifest.yaml`](../../config/assets_tier2_manifest.yaml) — steward fills `chunks[]`; agent does not invent tickers.

**Infra before bulk apply:**

- Catalog search in MSOS Strategy Lab
- Staggered cache warm (`warm_display_payload_cache.py --asset` batch mode when added)
- Prod witness samples N assets per deploy (not full 100 live fetch in CI)

---

## Wave 3 — tier-3 (~1000)

**Out of scope for this policy’s auto-execute path** until:

1. `ppe_tradeable_universe_tier3_v1` SELECTION merged
2. Bulk discovery script (`discover_asset_batch.py`) ships
3. Catalog pagination + lazy display payload
4. Operator rate-limit budget signed

Operator phrase `asset batch wave 3` → agent reads prerequisites, reports blockers, **does not** start ad-hoc registry spam.

---

## Failure handling

| Failure | Action |
|---------|--------|
| Discovery blocked | Skip asset; continue chunk if ≥1 green; else stop chunk |
| Witness fail on apply | Do not `--apply`; fix registry/venue; re-witness |
| Cache isolation fail | Stop; fix isolation before any enable |
| Gate fail | Fix in same session; no commit |
| >50% chunk blocked | Pause wave; steward reviews manifest liquidity gates |

**Rollback:** `enabled: false` in `config/assets.yaml` for chunk ids → redeploy display API → re-run catalog witness.

---

## Evidence (per chunk)

Append to chapter evidence doc:

- Chunk id, date, enabled ids, skipped ids + reason
- Witness stdout summary
- `enabled_count` before/after

---

## Tooling gaps (build before Wave 2 scale)

| Tool | Wave | Status |
|------|------|--------|
| `discover_asset_data_source.py --asset` | 1 | **Live** |
| `enable_asset_batch.py --manifest-slice` | 1–2 | **Live** |
| `probe_asset_data_source.py --group` | 1–2 | **Live** |
| `discover_asset_batch.py --chunk` | 2+ | **TODO** — bulk discovery JSON |
| `merge_manifest_chunk.py --apply` | 2+ | **TODO** — registry merge from tier2 manifest |
| MSOS catalog search | 2 | **TODO** — required >50 enabled |

Wave 1 runs with existing tools (loop per asset for discovery). Wave 2+ should add bulk scripts in a control-plane slice before operator says `wave 2`.

---

## Quick reference

```bash
# Where are we?
python scripts/witness_asset_catalog.py --all-enabled --json

# Wave 1 — next chapter dry-run
python scripts/enable_asset_batch.py --manifest-slice ppe_equity_universe_tier1a_v1 --dry-run

# Single asset (always works)
python scripts/discover_asset_data_source.py --asset SPY --json
```
