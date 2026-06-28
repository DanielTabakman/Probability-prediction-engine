# Asset enablement runbook v1

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**Chapter:** `ppe_asset_enablement_pipeline_v1`  
**Data sources:** [`ASSET_DATA_SOURCE_DISCOVERY_V1.md`](ASSET_DATA_SOURCE_DISCOVERY_V1.md)  
**Gate:** `python scripts/gate_asset_enablement_diff.py`

---

## When to use

Enabling a **batch** of tier-1 assets (e.g. SPY/QQQ/IWM, SOL/BNB/XRP) after meta infra chapters #1–#2 are COMPLETE.

Do **not** hand-edit `enabled: true` in `config/assets.yaml` without running the witness path below — CI rejects new enablements without proof.

---

## Standard path

```bash
# 0. Discover live source (agents — mandatory; see ASSET_DATA_SOURCE_DISCOVERY_V1.md)
python scripts/discover_asset_data_source.py --asset SOL --json
python scripts/probe_asset_data_source.py --group equity_index --json

# 1. Dry-run: show registry diffs + witness plan
python scripts/enable_asset_batch.py --group equity_index --dry-run

# 2. Witness (CI: mocked; steward: --live-witness for spot-check)
python scripts/witness_asset_catalog.py --group equity_index --json

# 3. Apply enabled flags (after witness green)
python scripts/enable_asset_batch.py --group equity_index --apply

# 4. Gate + merge + deploy
python scripts/run_pushable_gate.py

# 5. Warm display cache (after deploy)
python scripts/warm_display_payload_cache.py --base-url http://127.0.0.1:8765

# 6. Production multi-asset witness
python scripts/msos_production_multi_asset_witness.py
```

---

## CI gate (required on PRs touching `config/assets.yaml`)

`scripts/gate_asset_enablement_diff.py` runs in the pushable gate when `config/assets.yaml` is in the diff.

| Condition | Result |
|-----------|--------|
| Diff does not newly set `enabled: true` | Pass |
| Diff enables assets + `artifacts/enablement/*.json` covers batch with `witness_ok` | Pass |
| Diff enables assets + pre-enable witness passes for the batch (mocked) | Pass |
| Manual `enabled: true` without witness | **Fail** |

Reproduce locally:

```bash
python scripts/gate_asset_enablement_diff.py --base-ref origin/main --changed-file config/assets.yaml
```

---

## Preconditions

1. **Display parity** — MSOS Live UX for each asset in batch.  
2. **Registry row** — asset in `config/assets.yaml` with correct `venue` / symbols.  
3. **Live options** — discovery/probe green before enable.  
4. **Cache isolation** — pytest green when meta chapter #3 ships.

---

## Batch targets

| Target | Command |
|--------|---------|
| Crypto tier-1 | `--manifest-slice ppe_deribit_crypto_tier1_v1` |
| Equity index | `--manifest-slice ppe_equity_universe_tier1a_v1` |
| Mega caps batch 1/2 | `--manifest-slice ppe_equity_universe_tier1b_v1` / `tier1c_v1` |
| Commodity ETFs | `--manifest-slice ppe_commodity_proxy_tier1_v1` |

---

## Rollback

Set `enabled: false` for batch ids, redeploy `ppe_display_api`, re-run catalog witness.
