# Post–MVP1 belief-input UX — SELECTION outcome (2026-05-20)

**Status:** **SELECTION COMPLETE** — next BUILD chapter chartered on **`main`**.

**Inputs:** MVP1 belief-input UX **COMPLETE** (dual smoke `20260520_024407` + `20260520_024438`; sprint closed 2026-05-20); paid-interest **N**.

---

## Selected next BUILD chapter

| Field | Value |
|-------|--------|
| **Chapter** | **MVP1 onboarding / How it works (v0)** |
| **Sprint spec** | [`SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md`](SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md) |
| **Phase plan** | [`PHASE_PLANS/mvp1_onboarding_how_it_works_relay.json`](PHASE_PLANS/mvp1_onboarding_how_it_works_relay.json) |
| **Canon** | [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 5 |
| **Baseline** | **`main`** @ `47816a6`+ |
| **First slice** | `MVP1-OnboardingHowItWorks-Control-Slice001` (CONTROL) — charter |
| **Next slice** | `MVP1-OnboardingHowItWorks-Product-Slice002` — bounded “How it works” copy/UI in MVP1 lab context (may extend [`src/viz/tutorial.py`](../../src/viz/tutorial.py) / `render_tutorial_section`); no math/classification changes |

---

## Rationale

| Candidate | Decision |
|-----------|----------|
| **Onboarding / How it works** | **Selected** — §15B slice 5; explain market-implied distribution, belief overlay, disagreement, strategy families, and no-advice boundary before wider outreach. |
| **Sprint 003 evidence-plane** | **Deferred** — control-plane hardening; not the current product priority. |
| **Phase 3 commercial wrapper** | **Deferred** — new charter. |
| **Steward VPS CTA + outreach** | **Deferred** — steward parallel ([`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md)); not agent BUILD. |

---

## Steward parallel (non-blocking)

VPS CTA + §15F spot-check remain steward-owned ([`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md)).

---

## Next execution step

PREFLIGHT, then run **`MVP1-OnboardingHowItWorks-Control-Slice001`** per relay runbook.
