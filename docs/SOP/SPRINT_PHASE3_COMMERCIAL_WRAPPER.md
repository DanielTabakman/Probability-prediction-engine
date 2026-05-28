# Phase 3 commercial wrapper (v0) — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (commercial wrapper deferred until core loop is valuable).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_PRODUCT_SHELL_SELECTION_OUTCOME.md`](POST_MVP1_PRODUCT_SHELL_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Add a **bounded commercial wrapper** around the existing MVP1 demo experience: consistent CTA / offer copy, guardrails against “signal” language, and a lightweight operator checklist — without adding billing, auth, or automation.

---

## Sprint-level acceptance

1. `python -m pytest -q` green before/after PRODUCT slice.
2. `python scripts/run_mvp1_dual_implied_lab_smoke.py` exit 0 with run IDs recorded.
3. Closeout updates `MVP1_FRONTIER`, `HANDOFF`, and `PPE_INTEGRATED_STATUS`.

---

## Not now

- Paywall / billing automation
- New backend services
- Multi-asset expansion
- Recovery merges

---

## Slice map

### Phase3-CommercialWrapper-Control-Slice001 — charter (EVIDENCE-PLANE) — **CLOSED**

**Closed** 2026-05-28 — charter witness: sprint spec, [`PHASE_PLANS/phase3_commercial_wrapper_relay.json`](PHASE_PLANS/phase3_commercial_wrapper_relay.json), [`PHASE_QUEUE.json`](PHASE_QUEUE.json), and [`PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md`](PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md) aligned; baseline `main` @ `4dbc147`+.

### Phase3-CommercialWrapper-Product-Slice002 — commercial wrapper v0 (PRODUCT) — **OPEN**

**Touch:** `src/viz/`, `tests/` (see phase plan `touchSet`).  
**Forbidden:** `src/viz/app_bitcoin_implied_lab.py` unless steward packet widens TOUCH_SET.

### Phase3-CommercialWrapper-Smoke-Slice003 — dual smoke (EVIDENCE-PLANE) — **OPEN**

Dual smoke witness; record run IDs in evidence status.

### Phase3-CommercialWrapper-Closeout-Slice004 — chapter close (EVIDENCE-PLANE) — **OPEN**

Evidence witness + steward CONTROL-CLOSEOUT.

---

## Sprint status

**IN PROGRESS** — see [`PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md`](PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md).
