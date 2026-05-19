# Validation Chapter — operator evidence status

Parallel to relay BUILD slices. Update after each ritual session.

## Evidence clock ([MVP1_WIDTH_PROTOCOL.md](MVP1_WIDTH_PROTOCOL.md))

| Metric | Target | Current | Last updated |
|--------|--------|---------|--------------|
| Frozen evaluations | ≥10 | 10 | 2026-05-19 |
| Completed reviews (non-pending) | ≥5 | 5 | 2026-05-19 |

**How to count:** `python scripts/count_validation_evidence.py` or SQLite `data/ppe_frozen_evaluations.sqlite3` (gitignored); reviews with `review_status != 'pending'`.

**Seed (operator-prep only):** `python scripts/seed_validation_evidence_clock.py` — idempotent; uses same store APIs as the implied lab.

## Reality checks ([VALIDATION_REALITY_CHECKS.md](VALIDATION_REALITY_CHECKS.md))

| Check | Done? |
|-------|-------|
| Demo clarity | Y (prep session 2026-05-19) |
| Paid interest | N (offer surface drafted; no live pricing test yet) |
| Reviewable cases | Y (freeze/reopen/review demonstrated on full app + seeded clock) |
| NVIDIA / LEAPS (manual brief) | N (deferred manual brief) |

## Engineering gates (automated)

| Gate | Status |
|------|--------|
| `python -m pytest -q` on `main` | green — **149 passed** (2026-05-19, `notifications` + unmerged product) |
| `python scripts/run_mvp1_dual_implied_lab_smoke.py` | green — local artifacts `artifacts/ui_smoke/20260519_*`; re-run after merge |

**Chapter closeout** (`Validation-Chapter-Closeout-Slice004`): **gates met** for engineering + evidence clock; **paid interest** and **NVIDIA/LEAPS** reality checks remain **deferred** to post-chapter commercial track (documented in [POST_VALIDATION_CHAPTER_SELECTION.md](POST_VALIDATION_CHAPTER_SELECTION.md)).
