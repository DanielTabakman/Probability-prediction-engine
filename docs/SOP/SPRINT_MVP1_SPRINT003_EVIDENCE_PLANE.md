# MVP1 Sprint 003 evidence-plane — relay sprint spec

**Controlling canon:** [`SPRINT_003_PHASE_2.md`](SPRINT_003_PHASE_2.md) (evidence-plane only).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_FEEDBACK_BETA_SELECTION_OUTCOME.md`](POST_MVP1_FEEDBACK_BETA_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Bounded **evidence-plane / control-plane** hardening on `main`: tiered pushable gate, chapter closeout → queue automation, and relay operator ergonomics — **no** `src/viz/**` product changes.

---

## Sprint-level acceptance

1. **`python -m pytest -q`** green after evidence slice.
2. **`python scripts/run_pushable_gate.py`** documents tier behavior (tier 0/1/2).
3. Steering docs updated on chapter closeout via relay closeout job.

---

## Not now

- Product UX, feedback panel, or implied-lab layout changes.
- Dual UI smoke as a hard gate (not required for evidence-plane chapter).
- `docs/SOP/**` edits during BUILD slices (closeout job only).

---

## Slice map

### MVP1-Sprint003-Control-Slice001 — charter (EVIDENCE-PLANE) — **CLOSED**

**Closed** 2026-05-27 — charter witness: sprint spec, [`PHASE_PLANS/mvp1_sprint003_evidence_plane_relay.json`](PHASE_PLANS/mvp1_sprint003_evidence_plane_relay.json), [`PHASE_QUEUE.json`](PHASE_QUEUE.json), and [`MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md`](MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md) aligned; baseline `main` @ `897e16c`+.

### MVP1-Sprint003-Evidence-Slice002 — gate + auto-select (EVIDENCE-PLANE) — **CLOSED**

**Closed** 2026-05-27 — tiered pushable gate + queue auto-select; product **`3d4b311`**.

Touch: `scripts/`, `tests/`, `.cursor/rules/` (control plane). No `src/**`.

### MVP1-Sprint003-Witness-Slice003 — pytest witness (EVIDENCE-PLANE) — **CLOSED**

**Closed** 2026-05-27 — pytest + ruff witness; **206** passed at closeout re-verify.

### MVP1-Sprint003-Closeout-Slice004 — chapter closeout (EVIDENCE-PLANE) — **CLOSED**

**Closed** 2026-05-27 — evidence witness in [`MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md`](MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md); steward CONTROL-CLOSEOUT pending (frontier, handoff, integrated status, continuity brief, SELECTION prep).

---

## Sprint status

**COMPLETE** 2026-05-27 — relay BUILD slices closed; steward CONTROL-CLOSEOUT pending.
