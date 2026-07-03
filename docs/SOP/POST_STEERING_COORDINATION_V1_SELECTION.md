# Steering coordination program v1 — SELECTION

**Chapter / program:** `steering_coordination_program_v1`  
**Priority:** **HIGH** (charter candidate)  
**Program:** [`STEERING_COORDINATION_PROGRAM_V1.md`](STEERING_COORDINATION_PROGRAM_V1.md)  
**Plane:** CONTROL-PLANE

---

## Status

**DRAFT** — plan hardened 2026-07-02; awaiting founder charter (high priority).

---

## Why now

- Steering drift caused wrong "next BUILD" narrative while relay executed correctly.
- `ppe_milestone_gate.py` Phase 0 shipped but hooks and operator UX incomplete.
- Layer audits pass while humans waste cycles — high leverage, low product risk.

---

## Scope (in)

- Phase 1–3 per program doc (reconcile hooks, docHints refresh, operator ACTIVE/NEXT, drift codes, lifecycle consolidation).
- CONTROL-plane relay slices only.

---

## Non-goals

- Merging relay queue and UX backlog into one list.
- Blocking factory on informational steering warns.
- VM mirror / SSH hygiene (separate track).

---

## Acceptance (program complete)

1. Stale `nextBuildCandidateId` auto-repairs within one closeout tick.
2. `OPERATOR_STATUS` shows distinct **Active relay** and **Next UX BUILD** lines.
3. Gate warns on `STEERING_HINTS_DRIFT` / `UX_BACKLOG_QUEUE_MISMATCH`.
4. `relay_decision_reconcile` steward item closed with decision table canon.
5. Success metrics in program doc met at Phase 1 + Phase 2 minimum.

---

## Charter sign-off

| Field | Value |
|-------|-------|
| SELECTED date | _(pending)_ |
| Operator | _(pending)_ |
| First slice | `PPE-SteerCoord-Phase1-Control-Slice001` |
