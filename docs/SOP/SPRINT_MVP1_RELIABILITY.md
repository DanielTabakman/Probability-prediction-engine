# MVP1 Reliability — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md).  
**Live steering:** [`docs/SOP/MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION record:** [`POST_COMMERCIAL_OPS_SELECTION_OUTCOME.md`](POST_COMMERCIAL_OPS_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

**Authority:** CONTROL acceptance steward-driven. PRODUCT slices per [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md).

---

## Sprint intent

Harden MVP1 demo/smoke reliability after Commercial Validation ops: deterministic dual-smoke witness, harness kill-class prevention, and deploy env documentation — without Phase 2 reconcile or new product surfaces.

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after each PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** PASS with steward-recorded run IDs in frontier/evidence doc.
3. Implied-lab runbook §6 classification documented for any live-data degraded run.
4. `MVP1_FRONTIER` + `HANDOFF` updated on each slice closeout.

## Not now

- Phase 2 reconcile from recovery baseline.
- Billing, multi-asset automation, execution engine.
- New commercial offer surfaces beyond env/deploy docs.

---

## Slice map

### MVP1-Reliability-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Goal:** Accept sprint spec, phase plan, frontier sync.

**Deliverables:** this file, [`PHASE_PLANS/mvp1_reliability_relay.json`](PHASE_PLANS/mvp1_reliability_relay.json), `MVP1_FRONTIER.md`, `HANDOFF.md`, [`POST_COMMERCIAL_OPS_SELECTION_OUTCOME.md`](POST_COMMERCIAL_OPS_SELECTION_OUTCOME.md).

**Acceptance:** doc-only; pytest unchanged green. **Closed** 2026-05-19 (post-ops SELECTION).

---

### MVP1-Reliability-Smoke-Slice002 — harness discipline (PRODUCT) — **OPEN**

**Goal:** Reduce smoke kill/hang class: scenario progress logging, documented per-scenario timeouts, runbook alignment.

**Acceptance:** dual smoke exit **0** on `main`; witness run IDs logged.

---

### MVP1-Reliability-Deploy-Slice003 — deploy witness (CONTROL) — **OPEN**

**Goal:** `PPE_RESEARCH_OFFER_*` on demo service documented and verified in [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) after VPS `.env` + compose.

**Acceptance:** steward or agent fetch confirms offer CTA when env set; witness SHA matches deployed tip.

---

### MVP1-Reliability-Closeout-Slice004 — chapter close (CONTROL) — **OPEN**

**Goal:** Reliability chapter **COMPLETE** in `MVP1_FRONTIER`; handoff to next SELECTION (likely Phase 2 reconcile).

**Acceptance:** slices 001–003 **CLOSED**; evidence row in reliability status doc (frontier table).
