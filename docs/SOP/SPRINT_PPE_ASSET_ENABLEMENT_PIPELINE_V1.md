# PPE asset enablement pipeline v1 — relay sprint spec

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**SELECTION:** [`POST_PPE_ASSET_ENABLEMENT_PIPELINE_V1_SELECTION.md`](POST_PPE_ASSET_ENABLEMENT_PIPELINE_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

One scripted path: **manifest slice → group witness → enable** — no ad-hoc YAML edits per batch.

---

## Slice acceptance

### PPE-EnablePipe-Control-Slice001 (CONTROL)

- Runbook stub + evidence + relay plan witness green

### PPE-EnablePipe-Core-Slice002 (PPE_CORE)

- `witness_asset_catalog.py --group` / `--manifest-slice`
- `scripts/enable_asset_batch.py` (dry-run + apply)

### PPE-EnablePipe-Platform-Slice003 (PLATFORM)

- CI gate on `enabled: true` diffs
- [`ASSET_ENABLEMENT_RUNBOOK_V1.md`](ASSET_ENABLEMENT_RUNBOOK_V1.md) complete

### PPE-EnablePipe-Closeout-Slice004 (CONTROL)

- Evidence COMPLETE; demo `--group crypto` dry-run green
