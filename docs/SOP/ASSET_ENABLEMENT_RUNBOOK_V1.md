# Asset enablement runbook v1

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**Chapter:** `ppe_asset_enablement_pipeline_v1` (BUILD fills commands)

---

## When to use

Enabling a **batch** of tier-1 assets (e.g. SPY/QQQ/IWM) after meta infra chapters #1–#3 are COMPLETE.

---

## Standard path (target — implemented by enablement pipeline chapter)

```bash
# 1. Dry-run: show registry diffs + witness plan
python scripts/enable_asset_batch.py --group equity_index --dry-run

# 2. Witness (CI: mocked; steward: --live for spot-check)
python scripts/witness_asset_catalog.py --group equity_index --live

# 3. Apply enabled flags (after witness green)
python scripts/enable_asset_batch.py --group equity_index --apply

# 4. Gate + merge + deploy

# 5. Warm display cache
python scripts/warm_display_payload_cache.py --base-url http://127.0.0.1:8765

# 6. Production multi-asset witness
python scripts/msos_production_multi_asset_witness.py
```

---

## Gates (do not skip)

1. Display parity — MSOS Live for each asset in batch  
2. Cache isolation pytest green for batch group  
3. Production witness includes new assets  

---

## Rollback

Set `enabled: false` for batch ids in `config/assets.yaml`, redeploy `ppe_display_api`, re-run catalog witness.
