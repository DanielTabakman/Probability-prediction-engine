# MVP1 disagreement / candidate strip polish — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 4.  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_ONBOARDING_DISAGREEMENT_SELECTION_OUTCOME.md`](POST_MVP1_ONBOARDING_DISAGREEMENT_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Polish **disagreement** and **candidate strip** copy so width/directional candidates read as **hypotheses to inspect**: clearer labels, confidence/trust language, falsification conditions, and **fit-not-recommendation** framing — without changing disagreement **classification** rules, belief math, or data paths.

---

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** with run IDs in [`MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md`](MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on chapter closeout.

---

## Not now

- Billing, paywall, or Phase 3 commercial wrapper.
- Execution engine, live trading, or ticket automation.
- Multi-asset scope beyond current MVP1 lab.
- Changes to `classify_disagreement` thresholds or core derivation math.
- Recovery merge of blind `app.py` / `mvp1_benchmark_substrate.py`.

---

## Slice map

### MVP1-DisagreementStrip-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Closed** 2026-05-26 — charter witness: sprint spec, [`PHASE_PLANS/mvp1_disagreement_candidate_strip_polish_relay.json`](PHASE_PLANS/mvp1_disagreement_candidate_strip_polish_relay.json), [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md), and [`MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md`](MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md) aligned; baseline `main` @ `ef7a0f8`+.

### MVP1-DisagreementStrip-Product-Slice002 — strip polish (PRODUCT) — **CLOSED**

**Closed** 2026-05-26 — product **`630e93a`** (PR **#23**); hypothesis copy polish without classification/math changes.

**Touch:** `src/viz/` (belief/disagreement hints, candidate strip panels, provenance copy), `tests/`.  
**Forbidden:** `src/viz/app.py`, `src/viz/app_bitcoin_implied_lab.py` unless steward packet widens TOUCH_SET.

### MVP1-DisagreementStrip-Smoke-Slice003 — dual smoke (CONTROL) — **CLOSED**

**Closed** 2026-05-27 — dual smoke witness recorded (PR **#24**).

### MVP1-DisagreementStrip-Closeout-Slice004 — chapter close (CONTROL) — **CLOSED**

**Closed** 2026-05-27 — evidence witness in [`MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md`](MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md); steward CONTROL-CLOSEOUT pending (frontier, handoff, integrated status, continuity brief, SELECTION prep).

---

## Sprint status

**COMPLETE** 2026-05-27 — relay BUILD slices closed; steward CONTROL-CLOSEOUT pending.
