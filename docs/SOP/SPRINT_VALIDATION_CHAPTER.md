# Validation Chapter — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §1A (Validation Chapter).  
**Live steering:** [`docs/SOP/MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**Relay baseline:** **`main`** (see [`run_slice.cmd`](../../run_slice.cmd)).

**Pre-relay bulk BUILD:** commit **`9cc536b`** landed decision surface, demo UX, and operator docs outside the relay runtime. Relay-shaped work starts with **`Validation-Chapter-Control-Slice001`**.

**Authority:** SELECTION and CONTROL-CLOSEOUT are steward-driven. Relay-assisted BUILD runs only inside bounded loops per [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md).

---

## Sprint intent

Close the Validation Chapter on **`main`**: green dual smoke, demo hierarchy, deploy witness, and operator evidence targets — without reopening Phase 4–6 scope or execution/ticket automation.

## Sprint-level acceptance

1. **`python -m pytest -q`** green on baseline before/after each PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** PASS (or steward-classified live-data degraded with written classification in relay result).
3. Steering docs (`MVP1_FRONTIER`, `HANDOFF`) updated on each slice **CONTINUE** closeout.
4. Operator evidence (freezes/reviews/reality checks) tracked outside relay; chapter closeout when targets met.

## Not now

- Multi-asset expansion, execution engine, auto-trade language.
- Silent semantic contract rewrites.
- Broad UI redesign beyond Validation Chapter demo clarity.

---

## Slice map

### Validation-Chapter-Control-Slice001 — SELECTION + infra (CONTROL-PLANE) — **CLOSED**

**Goal:** Relay baseline **`main`**, sprint spec, phase plan, frontier/handoff alignment.

**Deliverables:** this file, [`PHASE_PLANS/validation_chapter_relay.json`](PHASE_PLANS/validation_chapter_relay.json), `run_slice.cmd` / `run_phase.cmd` baseline, [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md), [`HANDOFF.md`](HANDOFF.md).

**Acceptance:** doc-only; pytest unchanged green.

---

### Validation-Chapter-Smoke-Slice001 — dual smoke (PRODUCT-PLANE) — **CLOSED**

**Goal:** `scripts/run_mvp1_dual_implied_lab_smoke.py` exits 0; `MVP1_compact_verification` has `page_loaded: true`, `verification_found: true`, `trade_ticket_found: false`.

**Shipped:** harness waits on `Probability Engine` + `MVP1 output:`; MVP1 pass criteria relaxed for compact chrome.

---

### Validation-Chapter-UX-Slice002 — demo hierarchy (PRODUCT-PLANE) — **CLOSED**

**Goal:** chart → **MVP1 primary output** banner → digest → freeze.

**Shipped:** `render_mvp1_primary_output_compact` in [`app_panels.py`](../../src/viz/app_panels.py), wired in [`app.py`](../../src/viz/app.py).

---

### Validation-Chapter-Deploy-Slice003 — deploy witness (CONTROL-PLANE) — **CLOSED**

**Goal:** Record VPS post-deploy smoke per [`DEMO_UI_RELEASE_CHECKLIST.md`](DEMO_UI_RELEASE_CHECKLIST.md) §5.

**Deliverables:** steward fills [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md); frontier row updated on closeout.

**Acceptance:** witness table complete with hostname, date, PASS/FAIL per checklist row.

---

### Validation-Chapter-Closeout-Slice004 — chapter closeout (CONTROL-PLANE) — **CLOSED**

**Goal:** Mark Validation Chapter complete when **all** hold:

- Relay slices 001–003 **CLOSED** with §15 **CONTINUE**
- Dual smoke green (or classified degraded with sign-off)
- Operator evidence: ≥10 freezes, ≥5 completed reviews ([`MVP1_WIDTH_PROTOCOL.md`](MVP1_WIDTH_PROTOCOL.md)); reality-check rows in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md)

**Closed 2026-05-19:** engineering gates green; evidence clock met; deploy witness PASS. Paid-interest and NVIDIA/LEAPS reality checks **deferred** to post-chapter Commercial Validation track (see [`POST_VALIDATION_CHAPTER_SELECTION.md`](POST_VALIDATION_CHAPTER_SELECTION.md)).

---

## Phase plan

Sequential queue: [`PHASE_PLANS/validation_chapter_relay.json`](PHASE_PLANS/validation_chapter_relay.json)

```bat
run_phase.cmd docs/SOP/PHASE_PLANS/validation_chapter_relay.json
```
