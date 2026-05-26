# MVP1 friends-first — first meaningful screen polish — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (§15B–15F).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_SMOKE_REGRESSION_SELECTION_OUTCOME.md`](POST_MVP1_SMOKE_REGRESSION_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Make the MVP1 implied lab above-fold read as **“what this run is saying”** in plain English: headline, compact primary-output banner, trust-at-a-glance **before** the chart — without new decision logic, execution surfaces, or scope creep.

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** with run IDs in [`MVP1_FRIENDS_FIRST_EVIDENCE_STATUS.md`](MVP1_FRIENDS_FIRST_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on closeout.

## Not now

- Landing page / auth shell, onboarding site, billing, multi-asset.
- Recovery merge, `mvp1_benchmark_substrate.py` port.
- Changes to `mvp1_decision_surface.py` classification rules.
- Belief-input UX overhaul (§15B slice 3) — defer to next chapter.

---

## Slice map

### MVP1-FriendsFirst-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Closed** 2026-05-20.

---

### MVP1-FriendsFirst-Product-Slice002 — above-fold polish (PRODUCT) — **CLOSED**

**Closed** 2026-05-20 — `render_mvp1_friends_first_above_fold`; trust-at-a-glance before chart; tests `test_mvp1_friends_first_panels.py`.

---

### MVP1-FriendsFirst-Smoke-Slice003 — dual smoke witness (CONTROL) — **CLOSED**

**Closed** 2026-05-20 — dual smoke `20260520_020945` + `20260520_021200`.

---

### MVP1-FriendsFirst-Closeout-Slice004 — chapter close (CONTROL) — **CLOSED**

**Closed** 2026-05-20 — this evidence file + [`POST_MVP1_FRIENDS_FIRST_SELECTION.md`](POST_MVP1_FRIENDS_FIRST_SELECTION.md).

---

## Sprint status

**MVP1 friends-first screen:** **COMPLETE** 2026-05-20.
