# MVP1 Phase 5 review persistence hardening — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) · [`MVP1_PHASE1_3_SPRINT.md`](MVP1_PHASE1_3_SPRINT.md) (`MVP1-Phase5-Slice002`)  
**SELECTION:** [`POST_DEPLOY_WITNESS_PHASE5_SELECTION_OUTCOME.md`](POST_DEPLOY_WITNESS_PHASE5_SELECTION_OUTCOME.md)  
**Baseline:** **`main`**

---

## Sprint intent

Close remaining Phase 5 persistence gaps: SQLite foreign-key integrity for `snapshot_reviews` without execution/ticket scope.

## Acceptance

1. `python -m pytest -q tests/test_frozen_review_store.py tests/test_frozen_evaluation_store.py` green.
2. Full `python -m pytest -q` green before closeout.
3. Dual smoke optional (`PPE_SKIP_DUAL_SMOKE=1` allowed for local continuous runs).

## Touch set

- `src/viz/frozen_evaluation_store.py`
- `tests/test_frozen_review_store.py`
- `tests/test_frozen_evaluation_store.py`

## Not now

- Execution engine, ticket ledger, automated class verdicts (Phase 6 descriptive-only).
- Changes to `app_bitcoin_implied_lab.py` unless smoke requires.

---

## Slice map

### MVP1-Phase5Review-Control-Slice001 — charter

Align phase plan, queue, roadmap, evidence doc.

### MVP1-Phase5Review-Product-Slice002 — SQLite FK hardening (PRODUCT)

Implement PRAGMA + FK migration path; **`workerMode: local-agent`**.

### MVP1-Phase5Review-Smoke-Slice003 — pytest + optional dual smoke

### MVP1-Phase5Review-Closeout-Slice004 — chapter close
