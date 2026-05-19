# Phase 2 on `main` — evidence status

**Chapter:** [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md) · **Baseline:** `main` @ `559f908`+

---

## Engineering gates

| Gate | Status | Notes |
|------|--------|-------|
| `python -m pytest -q` | **PASS** | **156** passed (carry-forward from Reliability closeout) |
| Dual smoke | **PASS** (carry-forward) | `20260519_133606` + `20260519_134906` — re-run after PRODUCT slices |

---

## Slice status

| Slice | Status |
|-------|--------|
| Control-Slice001 | **CLOSED** 2026-05-19 |
| Reconcile-Slice002 | **OPEN** — `main` vs `recovery/frontier-steward-v2_1-baseline` |
| Product-Slice003 | **OPEN** — blocked on Slice002 |
| Closeout-Slice004 | **OPEN** |

---

## Reconcile-Slice002 (steward + agent)

**Command sketch (read-only):**

```bash
git fetch origin
git log --oneline main..origin/recovery/frontier-steward-v2_1-baseline -- src/viz/
git diff main...origin/recovery/frontier-steward-v2_1-baseline -- src/viz/
```

**Record here:** paths to port, paths to defer, first PRODUCT slice ID steward selects.

| Path / area | Port / defer | Notes |
|-------------|--------------|-------|
| `src/viz/app.py` | **review** | Large delta vs recovery (~951 lines touched in diff stat) — reconcile before blind port |
| `src/viz/app_panels.py` | **review** | +168 lines class — candidate strips / panels |
| `src/viz/mvp1_benchmark_substrate.py` | **review** | +495 lines on recovery — verify already on `main` under MVP1 |
| `src/viz/belief_disagreement_hints.py` | **review** | Small delta |
| `src/viz/decision_ready_review.py` | **review** | Small delta |
| `src/viz/implied_lab_provenance.py` | **review** | +32 lines |

**Diff command (2026-05-19):** `git diff --stat main...origin/recovery/frontier-steward-v2_1-baseline -- src/viz/` → 6 files, +1276 / -446.

**Steward:** mark port/defer per path; select first PRODUCT slice (historical target: Sprint004-Slice004 directional strip per [`SPRINT_004_PHASE_2.md`](SPRINT_004_PHASE_2.md)).

---

## References

- Historical product spec: [`SPRINT_004_PHASE_2.md`](SPRINT_004_PHASE_2.md)
- Reliability closed: [`MVP1_RELIABILITY_EVIDENCE_STATUS.md`](MVP1_RELIABILITY_EVIDENCE_STATUS.md)
