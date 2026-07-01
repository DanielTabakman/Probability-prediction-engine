# PPE tradeable universe program v1

**Purpose:** Canonical map for expanding MSOS Strategy Lab from the BTC/ETH wedge to a **curated catalog of major tradables** — crypto, equity indices, mega caps, and commodity proxies — without boiling the ocean or porting math to TypeScript.

**As-of:** 2026-06-26 · **Controlling canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — Guide G-05 · [`PPE_TRADEABLE_UNIVERSE_ADR.md`](PPE_TRADEABLE_UNIVERSE_ADR.md)

**Tier-1 asset manifest (staging):** [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml)

---

## Agent load bundle

| Role | Path |
|------|------|
| Program (charter) | this file |
| Parent meta infra | [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md) |
| Batch operator policy | [`ASSET_BATCH_EXPANSION_POLICY_V1.md`](ASSET_BATCH_EXPANSION_POLICY_V1.md) |
| Asset discovery CLI | `python scripts/discover_asset_data_source.py --asset <ID> --json` |
| Resolve chapter | `python scripts/resolve_sop.py --chapter <chapter_id> --json` |

---

## North star

**Every major liquid options name a trader expects is one click away in Strategy Lab** — with honest trust labels when chains are thin — and adding the next name is **registry row + witness**, not a cross-layer rewrite.

Not a market-data terminal. Not a 500-ticker scanner. Not live execution.

---

## Prerequisites (must be COMPLETE before universe infra BUILD)

| Chapter | Status | Delivers |
|---------|--------|----------|
| `ppe_crypto_multi_asset_v1` | **COMPLETE** | BTC + ETH + asset registry v1 |
| `ppe_equity_options_v1` | **IN PROGRESS** | NVDA + equity venue adapter |

Universe infrastructure (`ppe_tradeable_universe_v1`) **blocked until** `ppe_equity_options_v1` COMPLETE — proves second venue before batch equity rollout.

---

## Chapter sequence (relay order)

| # | Chapter | Priority | Blocked until | Delivers |
|---|---------|----------|---------------|----------|
| 0 | `ppe_equity_options_v1` | P2 · **active** | — | NVDA equity wedge |
| 1 | **`ppe_tradeable_universe_v1`** | **HIGH** | equity v1 COMPLETE | Registry v2, `catalog.json`, dynamic MSOS picker, witness harness |
| 2 | `ppe_deribit_crypto_tier1_v1` | MEDIUM | universe v1 COMPLETE | SOL + Deribit tier-1 cryptos |
| 3 | `ppe_equity_universe_tier1a_v1` | MEDIUM | universe v1 COMPLETE | SPY, QQQ, IWM |
| 4 | `ppe_equity_universe_tier1b_v1` | MEDIUM | tier1a COMPLETE | AAPL, MSFT, AMZN, GOOGL, META |
| 5 | `ppe_equity_universe_tier1c_v1` | MEDIUM | tier1a COMPLETE | TSLA, AMD, COIN |
| 6 | `ppe_commodity_proxy_tier1_v1` | MEDIUM | universe v1 COMPLETE | GLD, SLV, USO (ETF options) |
| 7 | `ppe_cme_commodity_v1` | **LOW · DEFER** | validation pull + tier1 proxy use | True CME commodity options — SELECTION only after demand |

Mechanical order: finish **0**, then **1**, then **2–6** may interleave by steward SELECTION but default backlog order is crypto → indices → mega caps → commodity proxy.

**Operator override (2026-06-26):** After **1** completes, chapter **2** (`ppe_deribit_crypto_tier1_v1`, **SOL**) is **urgent/high** — do not promote equity index batches (3–5) ahead of SOL witness.

---

## Meta infrastructure (2026-06-27 — charter before bulk enable)

Before tier-1 **content** batches merge `enabled: true` at scale, complete meta chapters in [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md):

| # | Chapter | Gate |
|---|---------|------|
| 1 | `ppe_asset_display_parity_v1` | Live UX + WSGI cache + deploy warm |
| 2 | `ppe_asset_enablement_pipeline_v1` | `enable_asset_batch.py` + group witness |
| 3 | `ppe_cache_isolation_audit_v1` | No cross-asset cache bleed |
| 4 | `ppe_display_cache_ops_v1` | Scheduled warm + cache health |
| 5 | `msos_workflow_asset_parity_v1` | P4→P7 asset propagation |
| 6 | `ppe_trust_surface_v1` | Trust labels in MSOS |
| 7 | `msos_production_multi_asset_witness_v1` | Prod regression per enabled asset |

Content batches (crypto tier1, equity tier1a/b/c, commodity proxy) may **BUILD** registry rows in parallel; **`enabled: true`** requires meta **#1–#3** COMPLETE unless steward documents exception in evidence.

---

## Target catalog (~25–30 enabled assets)

| Group | IDs | Venue |
|-------|-----|-------|
| Crypto (live + tier1) | BTC, ETH, SOL, BNB, XRP | deribit |
| Equity index | SPY, QQQ, IWM | equity (yfinance) |
| Equity mega cap | NVDA, AAPL, MSFT, AMZN, GOOGL, META, TSLA, AMD, COIN | equity |
| Commodity proxy | GLD, SLV, USO | equity (`asset_class: commodity_proxy`) |

Full rows: [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml).

---

## Operator artifacts

| Artifact | Command / path |
|----------|----------------|
| Enabled catalog (after universe v1) | `GET /ppe-display-api/catalog.json` |
| Per-asset witness | `python scripts/witness_asset_catalog.py --asset SPY` |
| Batch witness | `python scripts/witness_asset_catalog.py --group equity_index` |
| All enabled | `python scripts/witness_asset_catalog.py --all-enabled` |

---

## Enablement gate (every asset)

Before `enabled: true` in `config/assets.yaml`:

1. Fetch smoke — chain loads, ≥1 usable expiry
2. BL witness — curve renders or `trust_state: thin_chain` surfaced
3. Display boundary — `display.json?asset=X` valid
4. MSOS witness — catalog picker + chart metadata
5. Cache isolation — `asset_id` in all option caches

---

## What the program excludes

| Excluded | Why |
|----------|-----|
| Multi-ticker scanner | Curated catalog only |
| PPE math in TypeScript | Layer rule |
| Dividend/discount modeling v1 | Trust notes only |
| Polymarket on same chart | Separate cross-venue program |
| CME until validation pull | High vendor cost; ETF proxies first |
| Auto-trade / execution | Deferred globally |

---

## Source docs (by chapter)

| Chapter | Sprint | SELECTION | Relay plan | Evidence |
|---------|--------|-----------|------------|----------|
| universe v1 | [`SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md`](SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md) | [`POST_PPE_TRADEABLE_UNIVERSE_V1_SELECTION.md`](POST_PPE_TRADEABLE_UNIVERSE_V1_SELECTION.md) | [`PHASE_PLANS/ppe_tradeable_universe_v1_relay.json`](PHASE_PLANS/ppe_tradeable_universe_v1_relay.json) | [`PPE_TRADEABLE_UNIVERSE_V1_EVIDENCE_STATUS.md`](PPE_TRADEABLE_UNIVERSE_V1_EVIDENCE_STATUS.md) |
| crypto tier1 | [`SPRINT_PPE_DERIBIT_CRYPTO_TIER1_V1.md`](SPRINT_PPE_DERIBIT_CRYPTO_TIER1_V1.md) | [`POST_PPE_DERIBIT_CRYPTO_TIER1_V1_SELECTION.md`](POST_PPE_DERIBIT_CRYPTO_TIER1_V1_SELECTION.md) | [`PHASE_PLANS/ppe_deribit_crypto_tier1_v1_relay.json`](PHASE_PLANS/ppe_deribit_crypto_tier1_v1_relay.json) | [`PPE_DERIBIT_CRYPTO_TIER1_V1_EVIDENCE_STATUS.md`](PPE_DERIBIT_CRYPTO_TIER1_V1_EVIDENCE_STATUS.md) |
| equity tier1a | [`SPRINT_PPE_EQUITY_UNIVERSE_TIER1A_V1.md`](SPRINT_PPE_EQUITY_UNIVERSE_TIER1A_V1.md) | [`POST_PPE_EQUITY_UNIVERSE_TIER1A_V1_SELECTION.md`](POST_PPE_EQUITY_UNIVERSE_TIER1A_V1_SELECTION.md) | [`PHASE_PLANS/ppe_equity_universe_tier1a_v1_relay.json`](PHASE_PLANS/ppe_equity_universe_tier1a_v1_relay.json) | [`PPE_EQUITY_UNIVERSE_TIER1A_V1_EVIDENCE_STATUS.md`](PPE_EQUITY_UNIVERSE_TIER1A_V1_EVIDENCE_STATUS.md) |
| equity tier1b | [`SPRINT_PPE_EQUITY_UNIVERSE_TIER1B_V1.md`](SPRINT_PPE_EQUITY_UNIVERSE_TIER1B_V1.md) | [`POST_PPE_EQUITY_UNIVERSE_TIER1B_V1_SELECTION.md`](POST_PPE_EQUITY_UNIVERSE_TIER1B_V1_SELECTION.md) | [`PHASE_PLANS/ppe_equity_universe_tier1b_v1_relay.json`](PHASE_PLANS/ppe_equity_universe_tier1b_v1_relay.json) | [`PPE_EQUITY_UNIVERSE_TIER1B_V1_EVIDENCE_STATUS.md`](PPE_EQUITY_UNIVERSE_TIER1B_V1_EVIDENCE_STATUS.md) |
| equity tier1c | [`SPRINT_PPE_EQUITY_UNIVERSE_TIER1C_V1.md`](SPRINT_PPE_EQUITY_UNIVERSE_TIER1C_V1.md) | [`POST_PPE_EQUITY_UNIVERSE_TIER1C_V1_SELECTION.md`](POST_PPE_EQUITY_UNIVERSE_TIER1C_V1_SELECTION.md) | [`PHASE_PLANS/ppe_equity_universe_tier1c_v1_relay.json`](PHASE_PLANS/ppe_equity_universe_tier1c_v1_relay.json) | [`PPE_EQUITY_UNIVERSE_TIER1C_V1_EVIDENCE_STATUS.md`](PPE_EQUITY_UNIVERSE_TIER1C_V1_EVIDENCE_STATUS.md) |
| commodity proxy | [`SPRINT_PPE_COMMODITY_PROXY_TIER1_V1.md`](SPRINT_PPE_COMMODITY_PROXY_TIER1_V1.md) | [`POST_PPE_COMMODITY_PROXY_TIER1_V1_SELECTION.md`](POST_PPE_COMMODITY_PROXY_TIER1_V1_SELECTION.md) | [`PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json`](PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json) | [`PPE_COMMODITY_PROXY_TIER1_V1_EVIDENCE_STATUS.md`](PPE_COMMODITY_PROXY_TIER1_V1_EVIDENCE_STATUS.md) |
| CME commodity | [`SPRINT_PPE_CME_COMMODITY_V1.md`](SPRINT_PPE_CME_COMMODITY_V1.md) | [`POST_PPE_CME_COMMODITY_V1_SELECTION.md`](POST_PPE_CME_COMMODITY_V1_SELECTION.md) | [`PHASE_PLANS/ppe_cme_commodity_v1_relay.json`](PHASE_PLANS/ppe_cme_commodity_v1_relay.json) | [`PPE_CME_COMMODITY_V1_EVIDENCE_STATUS.md`](PPE_CME_COMMODITY_V1_EVIDENCE_STATUS.md) |

---

## Success criteria (program-level)

1. **Infrastructure:** MSOS asset picker reads `catalog.json` — no hardcoded `SUPPORTED_LAB_ASSET_IDS` gate for new names.
2. **Coverage:** ≥20 tier-1 assets `enabled: true` with green batch witness.
3. **Trust:** Thin chains show warnings; commodity proxies labeled honestly (ETF exposure, not COMEX).
4. **Velocity:** Adding asset #21 is registry row + witness script only (no MSOS code change).

---

## Steward SELECTION ritual

1. Confirm prior chapter COMPLETE + evidence doc signed.
2. Merge manifest rows from [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml) into `config/assets.yaml` (`enabled: false` until witness).
3. Promote chapter in [`PHASE_QUEUE.json`](PHASE_QUEUE.json) or run `python scripts/ppe_auto_select.py --apply`.
4. Operator: `run_ppe.cmd` or IDE BUILD starter.
