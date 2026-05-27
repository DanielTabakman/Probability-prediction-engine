# MVP1 decision-ready review polish — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B (BTC implied lab hierarchy — decision-ready review).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_SPRINT003_SELECTION_OUTCOME.md`](POST_MVP1_SPRINT003_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Polish the **Decision-ready review** block for **friends-first MVP1**: clearer structure/payoff read, trust/fit-not-recommendation language aligned with disagreement + candidate strip chapters, and accurate linkage to **Belief vs market — at a glance** when `mvp1_exclude_execution_ui=True` — **display copy only** (no strategy math, classification, or ticket automation).

---

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** with run IDs recorded in [`MVP1_DECISION_READY_REVIEW_POLISH_EVIDENCE_STATUS.md`](MVP1_DECISION_READY_REVIEW_POLISH_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on chapter closeout.

---

## Not now

- Billing, paywall, or Phase 3 commercial wrapper.
- Execution engine, live trading, or trade-ticket export in MVP1 mode.
- Multi-asset scope beyond current MVP1 lab.
- Changes to strategy selection, overlay math, or `strategy_summary` applicability rules.
- Recovery merge of blind `app.py` / `mvp1_benchmark_substrate.py`.

---

## Slice map

### MVP1-DecisionReview-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Closed** 2026-05-27 — charter witness: sprint spec, [`PHASE_PLANS/mvp1_decision_ready_review_polish_relay.json`](PHASE_PLANS/mvp1_decision_ready_review_polish_relay.json), and [`MVP1_DECISION_READY_REVIEW_POLISH_EVIDENCE_STATUS.md`](MVP1_DECISION_READY_REVIEW_POLISH_EVIDENCE_STATUS.md) aligned; baseline `main` @ `3d4b311`+.

### MVP1-DecisionReview-Product-Slice002 — review polish (PRODUCT) — **CLOSED**

**Closed** 2026-05-27 — product **`61c2571`**; hypothesis framing + MVP1 glance linkage copy.

**Touch:** `src/viz/decision_ready_review.py`, `src/viz/app_panels.py`, `tests/test_decision_ready_review.py`.  
**Forbidden:** `src/viz/app.py`, `src/viz/app_bitcoin_implied_lab.py` unless steward packet widens TOUCH_SET.

### MVP1-DecisionReview-Smoke-Slice003 — dual smoke (CONTROL) — **CLOSED**

**Closed** 2026-05-27 — harness `decision_review_mvp1_found` witness; dual smoke `20260527_190000` + `20260527_191207`.

### MVP1-DecisionReview-Closeout-Slice004 — chapter close (CONTROL) — **CLOSED**

**Closed** 2026-05-27 — evidence witness in [`MVP1_DECISION_READY_REVIEW_POLISH_EVIDENCE_STATUS.md`](MVP1_DECISION_READY_REVIEW_POLISH_EVIDENCE_STATUS.md); steward CONTROL-CLOSEOUT pending (frontier, handoff, integrated status, continuity brief, SELECTION prep).

---

## Sprint status

**COMPLETE** 2026-05-27 — relay BUILD slices closed; steward CONTROL-CLOSEOUT pending.
