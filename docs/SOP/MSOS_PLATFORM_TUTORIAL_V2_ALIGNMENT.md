# MSOS platform tutorial v2 — alignment

**Status:** **ACTIVE** (product implementation on `main`)  
**Supersedes:** v1 passive walkthrough only — chapter `msos_self_serve_onboarding_v1` remains **COMPLETE**; v2 extends the same tour system.  
**As-of:** 2026-06-30

**Canon links:**

| Doc | Role |
|-----|------|
| [`CLIENT_SELF_SERVE_DEMO_V1.md`](CLIENT_SELF_SERVE_DEMO_V1.md) | Workstream A — self-serve demo + **tutorial contract** |
| [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md) | Success = process fit, not “finished the tour” |
| [`MSOS_UX_DESIGN_PHILOSOPHY_V1.md`](MSOS_UX_DESIGN_PHILOSOPHY_V1.md) | Tutorial through play; zero-friction first action |
| [`TRADER_LEARNING_SPINE_PROGRAM_V1.md`](TRADER_LEARNING_SPINE_PROGRAM_V1.md) | Save → review → track — spine steps in **full** tour |

**Implementation SSOT:** [`apps/msos-web/src/lib/platformTutorial.ts`](../../apps/msos-web/src/lib/platformTutorial.ts)

---

## Problem (v1 gap)

v1 delivered self-serve onboarding (spotlight tour, first visit, restart, beginner track). Gaps for **Trader Workflow Integration**:

1. **Passive** — users could click Next through belief without touching controls.
2. **Lab-only** — no pointer to Horizon, export, or review loop.
3. **One length** — same tour for first visit and return visitors who need the 15-second wedge only.

Milestone criterion #1 distinguishes **using MSOS in process** from **completing the tour**.

---

## Three upgrade directions (v2)

### 1. Tutorial through play

Gate **Next** on a micro-action where it matters:

- **Belief step:** user must tap Higher/Lower (or More/Less vol) once; card copy updates after the nudge (“Teal moved — that’s your disagreement”).
- Aligns with philosophy § *Tutorial through play* and Phase 2 non-goal guard (not text walls — **interaction**, not more copy).

### 2. Extend tour along the trader spine

Optional steps after core lab flow (**full** mode only):

| Step | Anchor | Intent |
|------|--------|--------|
| Options Horizon | `lab-horizon-nav` | Region thesis — price × time before expression |
| Distribution export | `lab-distribution-export` | Research / journal CSV |
| Review loop | `lab-workflow-review` | Confirm → Monitor / History for post-mortem |

Bundle spine copy updates with workflow slices per [`POST_MSOS_TRADER_WORKFLOW_HORIZON_NAV_V1_SELECTION.md`](POST_MSOS_TRADER_WORKFLOW_HORIZON_NAV_V1_SELECTION.md).

### 3. Multiple tour modes (not one longer default)

| Mode | Entry | Steps | Audience |
|------|-------|-------|----------|
| **standard** | First visit, `?tutorial=1` | Asset → expiry → belief (play) → chart → tuning → confirm | Default self-serve |
| **beginner** | `?beginner=1`, features CTA | Shorter copy; belief (play); no tuning step | Options newcomers |
| **quick** | `?tutorial=quick` | Expiry → belief (play) → chart → confirm | Return visitors; 15s wedge |
| **full** | `?tutorial=full` | Standard + spine (horizon, export, review) | First serious session |

**Default first visit:** `standard` (with play gates). **Not** full — spine is opt-in depth.

---

## Tutorial contract (unchanged + v2 rules)

1. Any visitor-visible workflow change → update `platformTutorial.ts` in the **same PR**.
2. New tour anchors → `data-tour` on the target element + step row in the appropriate mode array.
3. Play-gated steps → use `playAction` in step definition; emit from the control surface (belief nudge).
4. No advisory copy — descriptive only ([`SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md)).
5. No text-heavy onboarding walls — prefer one gated interaction over extra steps.

---

## Acceptance (v2)

Observable in demo or witness:

1. Belief step **cannot** advance until one nudge (standard, beginner, quick).
2. **Quick** tour ≤ 4 steps; **full** tour includes horizon + export + workflow review anchors.
3. Homepage / features / restart CTAs resolve to correct mode hrefs.
4. pytest witnesses for mode resolution + wiring green.
5. Playwright witness still dismisses tour via existing storage key (automation unchanged).

**Not** acceptance: tour completion rate alone — validate with steward comprehension Q (*“Would you open this before your next trade?”*) per [`STEWARD_VALIDATION_GUIDE_V1.md`](STEWARD_VALIDATION_GUIDE_V1.md).

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-30 | v2 alignment — play gates, spine steps, four tour modes |
