# Phase plan slice schema v1

**Plane:** CONTROL-PLANE  
**Validation:** `python -m scripts.validate_phase_plans`

---

## Slice fields

| Field | Required | Notes |
|-------|----------|-------|
| `sliceId` | yes | Stable id |
| `declaredPlane` | yes | `PRODUCT-PLANE` \| `EVIDENCE-PLANE` |
| `layerPreset` | recommended | From `REPO_LAYER_PATH_PREFIXES.json` |
| `touchSet` | **yes on PRODUCT-PLANE** (strict) | Explicit edit paths |
| `acceptance` | optional | `{ id, check, verify? }[]` |
| `closeout` | one per plan | Chapter closeout |

---

## CLI

```bash
python -m scripts.validate_phase_plans --manifest
python -m scripts.validate_phase_plans --phase-plan docs/SOP/PHASE_PLANS/foo_relay.json --strict
python -m scripts.validate_phase_plans --all --strict   # legacy plans may lack closeout
```

See [`ACCEPTANCE_TEST_NAMING_V1.md`](ACCEPTANCE_TEST_NAMING_V1.md) · [`AI_HUMAN_DIVISION_V1.md`](AI_HUMAN_DIVISION_V1.md).
