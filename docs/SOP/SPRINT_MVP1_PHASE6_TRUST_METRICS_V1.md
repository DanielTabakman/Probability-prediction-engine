# MVP1 Phase 6 trust metrics v1 — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) · [`MVP1_PHASE1_3_SPRINT.md`](MVP1_PHASE1_3_SPRINT.md) (Phase 6 v0 + beyond v0)  
**SELECTION:** [`POST_PHASE5_PHASE6_TRUST_METRICS_SELECTION_OUTCOME.md`](POST_PHASE5_PHASE6_TRUST_METRICS_SELECTION_OUTCOME.md)  
**Baseline:** **`main`**

---

## Sprint intent

Promote MVP1 **trust enums** (`data_quality`, `primary_output_state`) from frozen snapshots into Phase 6 **class summary** rollups and implied-lab UI. Replace Breeden-only trust proxy as the primary operator-facing trust breakdown.

## Trust enum contracts (frozen record)

| Field | Allowed values | Source precedence |
|-------|----------------|-------------------|
| `data_quality` | `usable`, `degraded`, `invalid` | `record["data_quality"]` → `verification.verification_summary.data_quality` → legacy fallback |
| `primary_output_state` | `candidate`, `watch_only`, `no_trade` | `record["primary_output_state"]` → `verification.verification_summary.primary_output_state` → `unknown` |

### Legacy fallback (`data_quality` only)

When no explicit enum on a frozen row (pre–Phase 3 snapshots):

1. Read `density.market_implied.breeden_litzenberger` (existing proxy path).
2. If value is `computed` → bucket **`unknown`** (do not infer `usable`).
3. Else → bucket **`degraded`**.

`primary_output_state` without explicit value → **`unknown`** (no breeden inference).

## Acceptance

1. `python -m pytest -q tests/test_reviewed_class_summary.py` green.
2. Full `python -m pytest -q` green before closeout.
3. Rollup JSON includes **`by_data_quality`** and **`by_primary_output_state`** with expected keys when test fixtures set enums.
4. CSV export includes new metrics in `serialize_rollup_csv`.
5. Dual smoke optional (`PPE_SKIP_DUAL_SMOKE=1`).

## Touch set

- `src/viz/reviewed_class_summary.py`
- `src/viz/frozen_evaluation_record.py` (only if a shared resolver helper reduces duplication)
- `src/viz/app.py` (Phase 6 expander caption + JSON subheaders only)
- `tests/test_reviewed_class_summary.py`

## Not now

- Changing `resolve_data_quality()` rules in `mvp1_decision_surface.py`.
- Execution engine, ticket ledger, automated class verdicts beyond descriptive counts.
- Broad `app.py` refactors outside the Phase 6 expander block.

---

## Slice map

### MVP1-Phase6Trust-Control-Slice001 — charter

Align phase plan, queue, roadmap, evidence doc; confirm SELECTION outcome on disk.

### MVP1-Phase6Trust-Product-Slice002 — trust enum rollups (PRODUCT)

Implement rollup + UI per contracts above; **`workerMode: local-agent`**.

### MVP1-Phase6Trust-Smoke-Slice003 — pytest witness

Run targeted + full pytest; bump pytest witness count if repo policy requires.

### MVP1-Phase6Trust-Closeout-Slice004 — chapter close

Control closeout; manifest COMPLETE; queue item DONE.
