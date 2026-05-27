# MVP1 disagreement / candidate strip polish — evidence status

**Chapter:** MVP1 disagreement / candidate strip polish (v0)  
**Status:** **ACTIVE**  
**SELECTION:** [`POST_MVP1_ONBOARDING_DISAGREEMENT_SELECTION_OUTCOME.md`](POST_MVP1_ONBOARDING_DISAGREEMENT_SELECTION_OUTCOME.md)  
**Sprint spec:** [`SPRINT_MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH.md`](SPRINT_MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH.md)  
**Phase plan:** [`PHASE_PLANS/mvp1_disagreement_candidate_strip_polish_relay.json`](PHASE_PLANS/mvp1_disagreement_candidate_strip_polish_relay.json)

---

## Witness log

| Slice | Status | Notes |
|-------|--------|-------|
| MVP1-DisagreementStrip-Control-Slice001 | **CLOSED** 2026-05-26 | charter witness; baseline `main` @ `ef7a0f8`+ |
| MVP1-DisagreementStrip-Product-Slice002 | pending | |
| MVP1-DisagreementStrip-Smoke-Slice003 | **CLOSED** 2026-05-27 | dual smoke `20260526_202410` + `20260526_203629` (~937s) |
| MVP1-DisagreementStrip-Closeout-Slice004 | pending | |

---

## Engineering gates (charter baseline)

| Gate | Status | Notes |
|------|--------|-------|
| `python -m pytest -q` | **PASS** | **189** passed (2026-05-27) |
| Dual smoke | **PASS** | `20260526_202410` (MVP1_compact) + `20260526_203629` (A_width); exit 0 (~937s) |

---

## Dual smoke

| Run ID | Scenario | Exit | Notes |
|--------|----------|------|-------|
| 20260526_202410 | MVP1_compact_verification | 0 | verification + trust_strip_mvp1 true (~726s) |
| 20260526_203629 | A_width_target_payoff | 0 | verification true (~188s) |

**Prior flake (not recorded):** `20260526_201059` — MVP1_compact cold-start page load incomplete; superseded by pass-2 run above.

## Pytest

- Count at smoke witness: **189** passed (2026-05-27)
