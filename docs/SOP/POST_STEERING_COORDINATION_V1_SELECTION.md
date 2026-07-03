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

Steering drift caused wrong "next BUILD" narrative while relay executed correctly. `ppe_milestone_gate.py` Phase 0 shipped but hooks and operator UX incomplete. High leverage, low product risk.

---

## Scope (in)

Phase 1–3 per program doc. CONTROL-plane relay slices only.

---

## Non-goals

Merging relay and UX queues; blocking factory on informational warns; VM mirror hygiene.

---

## Acceptance (program complete)

1. Stale `nextBuildCandidateId` auto-repairs within one closeout tick.
2. `OPERATOR_STATUS` shows **Active relay** and **Next UX BUILD** separately.
3. Gate warns on hints/backlog drift.
4. `relay_decision_reconcile` closed.
5. Phase 1 + 2 success metrics met.

---

## Charter sign-off

| Field | Value |
|-------|-------|
| SELECTED date | _(pending)_ |
| First slice | `PPE-SteerCoord-Phase1-Control-Slice001` |
