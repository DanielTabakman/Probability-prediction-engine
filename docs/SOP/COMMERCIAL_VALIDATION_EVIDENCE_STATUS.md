# Commercial Validation — evidence status

## Engineering gates

| Gate | Status |
|------|--------|
| `python -m pytest -q` | green — **153 passed** (2026-05-19 ops cleanup) |
| `python scripts/run_mvp1_dual_implied_lab_smoke.py` | green — `20260519_131035` (compact) + `20260519_131251` (full lab); exit 0; classification **deterministic** |

## Slice status

| Slice | Status |
|-------|--------|
| Commercial-Validation-Control-Slice001 | CLOSED |
| Commercial-Validation-Offer-Slice002 | CLOSED |
| Commercial-Validation-Reality-Slice003 | CLOSED (playbook + log; live buyer outreach via ops) |
| Commercial-Validation-Nvidia-Brief-Slice004 | CLOSED |

## Reality checks

See [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

## Deploy

Ops tracker: [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md). Re-verify VPS SHA after `git pull` on production.
