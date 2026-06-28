# Asset data source discovery v1

**Purpose:** Agents **automatically** find live options sources and hook up assets — **no operator vendor lookup, no multi-prompt back-and-forth.**

**As-of:** 2026-06-28 · **Related:** [`PPE_TRADEABLE_UNIVERSE_ADR.md`](PPE_TRADEABLE_UNIVERSE_ADR.md) · [`ASSET_ENABLEMENT_RUNBOOK_V1.md`](ASSET_ENABLEMENT_RUNBOOK_V1.md)

---

## Operator says "add / enable / hook up asset X" (or a batch)

**Agent runs first (same turn, before replying):**

```bash
# one asset
python scripts/discover_asset_data_source.py --asset X --json

# catalog group (crypto, equity_index, equity_mega, commodity_proxy)
python scripts/discover_asset_data_source.py --group crypto --json

# tier-1 manifest chapter
python scripts/discover_asset_data_source.py --manifest-slice ppe_deribit_crypto_tier1_v1 --json

# entire config/assets.yaml registry
python scripts/discover_asset_data_source.py --all-registry --json
```

Then **execute** `next_action` for each report (batch JSON has `reports[]` + `next_action_rollup`). Do not ask which exchange.

| Command | When |
|---------|------|
| `discover_asset_data_source.py` | **New asset**, wrong venue, or "get X down" |
| `probe_asset_data_source.py` | Verify **current** registry row only (post-change / CI) |

---

## Wired venues (scan order)

Configured in [`config/asset_venue_source_map.yaml`](../../config/asset_venue_source_map.yaml):

| Kind | Scan order | Fetch module |
|------|------------|--------------|
| **crypto** | Deribit → Bybit | `fetch_deribit.py` → `fetch_bybit_options.py` |
| **equity** | Yahoo (yfinance) | `fetch_equity_options.py` |

Discovery picks the **live** venue with the most instruments. **Prefers wired adapters** when multiple venues are live.

---

## `next_action` values (agent executes)

| Value | Meaning |
|-------|---------|
| `enable_existing_row` | Registry + venue correct; flip `enabled: true` after witness |
| `merge_registry_and_enable` | Not in registry; merge from tier1 manifest + enable |
| `switch_venue_and_enable` | Registry points at dead venue (e.g. Deribit SOL); switch to live venue (e.g. Bybit) |
| `build_adapter` | Live vendor found but fetch module not in repo — implement adapter, then enable |
| `already_enabled` | Nothing to do |
| `blocked_no_live_options` | No chain anywhere — document skip, do not enable |

---

## Agent ritual (hard — see [`asset-auto-discovery.mdc`](../../.cursor/rules/asset-auto-discovery.mdc))

### Triggers

- "Get SOL down" / "add SPY" / "enable BNB" / "hook up X"
- Tier-1 batch BUILD Core slice
- Registry row exists but probe fails

### Steps

1. `discover_asset_data_source.py --asset X --json`
2. Implement `agent_steps` from JSON (registry, adapter, routing, witness, enable)
3. `probe_asset_data_source.py --asset X` to confirm registry routing
4. Gate → commit → PR (PPE auto-commit policy)

### Do not

- Ask the operator which exchange has options
- Stop after reporting Deribit is empty without scanning Bybit
- Enable without witness when `options_count > 0`

---

## Adding a new venue to the scan list

1. Implement `src/data/fetch_<venue>_options.py` (Deribit-shaped normalization)
2. Add venue to `asset_venue_source_map.yaml` + `discovery.crypto_scan_order` or `equity_scan_order`
3. Register in `scripts/asset_source_discovery_core.py` (`FETCH_MODULE_BY_VENUE`, `scan_*`)
4. Wire `app_cache` + `distribution_export` venue branches
5. Extend ADR venue table

---

## Examples

```bash
# SOL — Deribit empty, Bybit live → switch_venue_and_enable (or build_adapter if Bybit not merged)
python scripts/discover_asset_data_source.py --asset SOL

# SPY — equity scan
python scripts/discover_asset_data_source.py --asset SPY --kind equity

# Verify after change
python scripts/probe_asset_data_source.py --asset SOL --json
```
