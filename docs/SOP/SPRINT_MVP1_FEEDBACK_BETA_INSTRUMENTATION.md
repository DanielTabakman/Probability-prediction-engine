# MVP1 feedback + beta instrumentation — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 6.  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_DISAGREEMENT_FEEDBACK_SELECTION_OUTCOME.md`](POST_MVP1_DISAGREEMENT_FEEDBACK_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Ship a bounded **feedback** path in the MVP1 implied lab so early testers can submit structured signal: **confusion category**, **usefulness**, **repeat-use intent**, and **free-text objections** — aligned with master §15F tester rubric — without changing belief math, disagreement classification, or data paths.

---

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** with run IDs in [`MVP1_FEEDBACK_BETA_INSTRUMENTATION_EVIDENCE_STATUS.md`](MVP1_FEEDBACK_BETA_INSTRUMENTATION_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on chapter closeout.

---

## Not now

- Billing, paywall, or Phase 3 commercial wrapper.
- Execution engine, live trading, or ticket automation.
- External analytics SaaS or authenticated multi-user feedback backends.
- Changes to disagreement **classification** rules or core derivation math.
- Recovery merge of blind `app.py` / `mvp1_benchmark_substrate.py`.

---

## Slice map

### MVP1-FeedbackBeta-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Closed** 2026-05-27 — charter witness: sprint spec, [`PHASE_PLANS/mvp1_feedback_beta_instrumentation_relay.json`](PHASE_PLANS/mvp1_feedback_beta_instrumentation_relay.json), [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md), and [`MVP1_FEEDBACK_BETA_INSTRUMENTATION_EVIDENCE_STATUS.md`](MVP1_FEEDBACK_BETA_INSTRUMENTATION_EVIDENCE_STATUS.md) aligned; baseline `main` @ `9a4a04c`+.

### MVP1-FeedbackBeta-Product-Slice002 — feedback capture (PRODUCT) — **CLOSED**

**Closed** 2026-05-27 — product **`0937cef`**; Give feedback expander + local SQLite persistence (§15F rubric).

**Touch:** `src/viz/` (feedback UI + local persistence), `tests/`.  
**Forbidden:** `src/viz/app.py`, `src/viz/app_bitcoin_implied_lab.py` unless steward packet widens TOUCH_SET.

### MVP1-FeedbackBeta-Smoke-Slice003 — dual smoke (CONTROL) — **CLOSED**

**Closed** 2026-05-27 — harness `feedback_panel_found` witness; product **`b48b087`**.

### MVP1-FeedbackBeta-Closeout-Slice004 — chapter close (CONTROL) — **CLOSED**

**Closed** 2026-05-27 — evidence witness in [`MVP1_FEEDBACK_BETA_INSTRUMENTATION_EVIDENCE_STATUS.md`](MVP1_FEEDBACK_BETA_INSTRUMENTATION_EVIDENCE_STATUS.md); steward CONTROL-CLOSEOUT pending (frontier, handoff, integrated status, continuity brief, SELECTION prep).

---

## Sprint status

**COMPLETE** 2026-05-27 — relay BUILD slices closed; steward CONTROL-CLOSEOUT pending.
