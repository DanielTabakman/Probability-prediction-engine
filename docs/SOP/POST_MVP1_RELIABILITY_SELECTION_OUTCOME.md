# Post–MVP1 Reliability — SELECTION outcome (2026-05-19)

**Status:** **SELECTION COMPLETE** — next BUILD chapter chartered on **`main`**.

**Inputs:** Reliability chapter **COMPLETE** (smoke green `20260519_133606` / `134906`; deploy compose on `main` @ `559f908`); paid-interest **N** (honest — steward outreach continues).

---

## Selected next BUILD chapter

| Field | Value |
|-------|--------|
| **Chapter** | **Phase 2 on `main`** (MVP1-framed relay) |
| **Sprint spec** | [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md) |
| **Phase plan** | [`PHASE_PLANS/mvp1_phase2_on_main_relay.json`](PHASE_PLANS/mvp1_phase2_on_main_relay.json) |
| **Parent charter** | [`PHASE_2_CHARTER.md`](PHASE_2_CHARTER.md) |
| **Baseline** | **`main`** @ `559f908`+ |
| **First slice** | `MVP1-Phase2-Control-Slice001` (CONTROL) — **CLOSED** 2026-05-19 (charter accept) |
| **Next slice** | `MVP1-Phase2-Reconcile-Slice002` — baseline vs `recovery/frontier-steward-v2_1-baseline` |

---

## Rationale

| Candidate | Decision |
|-----------|----------|
| **Phase 2 on `main`** | **Selected** — Reliability gates green; product desirability/playability is the bottleneck; reconcile Sprint 004-class work from recovery baseline before new PRODUCT slices. |
| **MVP1 hardening follow-on** | **Deferred** — only if smoke regresses post-reconcile. |
| **Sprint 003 evidence-plane** | **Deferred** — no fresh pilot evidence. |

Historical Sprint 004 spec [`SPRINT_004_PHASE_2.md`](SPRINT_004_PHASE_2.md) and [`phase2_next.json`](PHASE_PLANS/phase2_next.json) are **reference only** — re-validate on `main` before PRODUCT BUILD.

---

## Steward parallel (non-blocking)

1. VPS `.env` → **Research beta (v0)** CTA **PASS** in [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md)
2. Paid-interest live call → **Y/N** in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md)

---

## Next execution step

Run **`MVP1-Phase2-Reconcile-Slice002`** — document delta `main` vs `recovery/frontier-steward-v2_1-baseline`; steward approves first PRODUCT slice from [`SPRINT_004_PHASE_2.md`](SPRINT_004_PHASE_2.md) map.
