# Phase 2 on `main` — relay sprint spec (MVP1)

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md).  
**Phase charter:** [`PHASE_2_CHARTER.md`](PHASE_2_CHARTER.md).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_RELIABILITY_SELECTION_OUTCOME.md`](POST_MVP1_RELIABILITY_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

**Authority:** CONTROL acceptance steward-driven. PRODUCT slices only after Reconcile-Slice002 steward sign-off.

---

## Sprint intent

Reconcile **Phase 2 desirability / playability** product work onto **`main`** under MVP1 canon: baseline diff vs `recovery/frontier-steward-v2_1-baseline`, then bounded PRODUCT slices (Sprint 004-class candidate-edge strips) without reopening Phase 1 trust spine or commercial/billing scope.

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after each PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** PASS when `src/viz/**` changes.
3. Reconcile artifact documents what is safe to port vs defer.
4. `MVP1_FRONTIER` + `HANDOFF` updated on each slice closeout.

## Not now

- Billing / Stripe / Phase 3 commercial wrapper.
- Multi-asset automation, execution engine.
- Silent semantic contract rewrites (`docs/SEMANTIC_CONTRACTS.md`).
- Blind merge of recovery branch without reconcile doc.

---

## Slice map

### MVP1-Phase2-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Goal:** Accept sprint spec, phase plan, frontier sync, SELECTION record.

**Deliverables:** this file, [`PHASE_PLANS/mvp1_phase2_on_main_relay.json`](PHASE_PLANS/mvp1_phase2_on_main_relay.json), [`POST_MVP1_RELIABILITY_SELECTION_OUTCOME.md`](POST_MVP1_RELIABILITY_SELECTION_OUTCOME.md), `MVP1_FRONTIER.md`, `HANDOFF.md`.

**Closed** 2026-05-19 (integrated finish-line pass).

---

### MVP1-Phase2-Reconcile-Slice002 — baseline reconcile (CONTROL) — **OPEN**

**Goal:** Steward-reviewed diff: `main` vs `recovery/frontier-steward-v2_1-baseline` for Sprint 004-class viz/product paths.

**Deliverables:** reconcile notes in [`MVP1_PHASE2_EVIDENCE_STATUS.md`](MVP1_PHASE2_EVIDENCE_STATUS.md) (file list + port/defer decision per path).

**Acceptance:** steward signs first PRODUCT slice target (likely `Sprint004-Slice004` class directional strip — see historical [`SPRINT_004_PHASE_2.md`](SPRINT_004_PHASE_2.md)).

---

### MVP1-Phase2-Product-Slice003 — first PRODUCT port (PRODUCT) — **OPEN**

**Goal:** First steward-selected PRODUCT slice from reconcile plan (not started until Slice002 **CLOSED**).

**Acceptance:** pytest + dual smoke green; frontier updated.

---

### MVP1-Phase2-Closeout-Slice004 — chapter checkpoint (CONTROL) — **OPEN**

**Goal:** Document first PRODUCT slice closeout or defer with honest evidence.

**Acceptance:** evidence doc + HANDOFF next step.
