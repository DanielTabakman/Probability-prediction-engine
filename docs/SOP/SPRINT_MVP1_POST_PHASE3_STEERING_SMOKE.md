# MVP1 post-Phase3 steering + smoke witness refresh — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION_OUTCOME.md`](POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

After Phase 3 commercial wrapper and Sprint 003 evidence-plane closeout: align steering docs with repo truth and capture a fresh dual implied-lab smoke witness on current `main`.

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after smoke slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** PASS with run IDs in [`MVP1_POST_PHASE3_STEERING_SMOKE_EVIDENCE_STATUS.md`](MVP1_POST_PHASE3_STEERING_SMOKE_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER`, `HANDOFF`, [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md), and continuity brief updated on closeout.

## Not now

- New product surfaces, billing, or classification math changes.
- Re-opening closed relay chapters (disagreement, feedback-beta, Sprint 003, Phase 3).

---

## Slice map

### MVP1-PostPhase3-Control-Slice001 — charter (EVIDENCE-PLANE) — **CLOSED**

**Closed** 2026-05-28 — charter witness: sprint spec, [`PHASE_PLANS/mvp1_post_phase3_steering_smoke_relay.json`](PHASE_PLANS/mvp1_post_phase3_steering_smoke_relay.json), [`PHASE_QUEUE.json`](PHASE_QUEUE.json), queue health audit, and [`MVP1_POST_PHASE3_STEERING_SMOKE_EVIDENCE_STATUS.md`](MVP1_POST_PHASE3_STEERING_SMOKE_EVIDENCE_STATUS.md) aligned; baseline `main` @ `db7ca53`+.

### MVP1-PostPhase3-Smoke-Slice002 — dual smoke (EVIDENCE)

**Goal:** Run dual implied-lab smoke; record run IDs and pytest count in evidence doc.

### MVP1-PostPhase3-Closeout-Slice003 — chapter close (CONTROL)

**Goal:** Control closeout — steering alignment, manifest **COMPLETE**, queue **DONE**.
