# PPE integrated status — canonical one-pager

**As-of:** 2026-06-13 · **Baseline `main`:** verify `git rev-parse origin/main` after push  
**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) · **MVP1 steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) · **MSOS steering:** [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) · **MSOS acceleration:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md) · **Strategic focus:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md)

This file merges archived chapters, steward parallel work, engineering gates, and the doc map. On drift, **`MVP1_FRONTIER.md`** wins for MVP1 slice queue; **`MSOS_FRONTIER.md`** wins for MSOS website slice queue; this file wins for cross-chapter summary.

---

## Active BUILD — MSOS P3 Command Center (manifest RUNNING)

| Field | Value |
|-------|--------|
| **Chapter** | `msos_p3_command_center` — [`msos_p3_command_center_relay.json`](PHASE_PLANS/msos_p3_command_center_relay.json) |
| **Sprint** | [`SPRINT_MSOS_P3_COMMAND_CENTER.md`](SPRINT_MSOS_P3_COMMAND_CENTER.md) |
| **Evidence** | [`MSOS_P3_COMMAND_CENTER_EVIDENCE_STATUS.md`](MSOS_P3_COMMAND_CENTER_EVIDENCE_STATUS.md) |
| **Last closed** | MSOS P2 homepage — **COMPLETE** 2026-06-03 |
| **Next queued (pre-chartered)** | P4 [`msos_p4_strategy_lab_relay.json`](PHASE_PLANS/msos_p4_strategy_lab_relay.json) — **blocked** until P3 closeout |

**P1 decision:** Phased hybrid — **`apps/msos-web/`** (Next.js 15 + TypeScript) for MSOS shell; **Streamlit** PPE unchanged; **Cloudflare Access** on `app.*`; PPE entry via **Caddy reverse proxy** at P4.

**MVP1 relay:** idle (P4 **READY** in queue). **Next MVP1 chapter (blocked until P4 COMPLETE):** probability method legibility — [`SPRINT_MVP1_PROBABILITY_METHOD_LEGIBILITY.md`](SPRINT_MVP1_PROBABILITY_METHOD_LEGIBILITY.md) (UI labels + pointwise Polymarket comparison shipped on branch). **Operator:** `run_ppe_local.cmd` / `run_ppe.cmd` — [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md).

---

## Flow (archived → steward → next BUILD)

```mermaid
flowchart LR
  subgraph closed [Closed chapters]
    V[Validation COMPLETE]
    C[Commercial Validation COMPLETE]
    R[MVP1 Reliability COMPLETE]
    P2[Phase 2 on main COMPLETE]
  end
  subgraph steward [Steward parallel]
    ENV[VPS .env CTA pending]
    PI[Paid interest N]
  end
  subgraph closed2 [Also closed]
    OH[MVP1 operator hardening COMPLETE]
    RE[MVP1 review enrichment COMPLETE]
    SR[MVP1 smoke regression COMPLETE]
  end
  closed --> closed2
  subgraph closed3 [Also closed]
    FF[MVP1 friends-first COMPLETE]
    BI[MVP1 belief-input COMPLETE]
    ON[MVP1 onboarding COMPLETE]
    P0[MSOS P0 COMPLETE]
  end
  closed2 --> closed3
  closed3 --> steward
  steward --> P1[MSOS P1 ADR in progress]
```

---

## Archived chapters (summary)

| Chapter | Status | Sprint / evidence |
|---------|--------|-------------------|
| Validation | **COMPLETE** 2026-05-19 | [`SPRINT_VALIDATION_CHAPTER.md`](SPRINT_VALIDATION_CHAPTER.md) |
| Commercial Validation | **COMPLETE** 2026-05-19 | [`SPRINT_POST_VALIDATION_COMMERCIAL.md`](SPRINT_POST_VALIDATION_COMMERCIAL.md) |
| MVP1 Reliability | **COMPLETE** 2026-05-19 | [`SPRINT_MVP1_RELIABILITY.md`](SPRINT_MVP1_RELIABILITY.md) |
| Phase 2 on `main` | **COMPLETE** 2026-05-19 | [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md) |
| MVP1 operator hardening | **COMPLETE** 2026-05-19 | [`SPRINT_MVP1_OPERATOR_HARDENING.md`](SPRINT_MVP1_OPERATOR_HARDENING.md) |
| MVP1 review enrichment | **COMPLETE** 2026-05-19 | [`SPRINT_MVP1_REVIEW_ENRICHMENT.md`](SPRINT_MVP1_REVIEW_ENRICHMENT.md) |
| MVP1 smoke regression | **COMPLETE** 2026-05-19 | [`SPRINT_MVP1_SMOKE_REGRESSION.md`](SPRINT_MVP1_SMOKE_REGRESSION.md) |
| MVP1 friends-first screen | **COMPLETE** 2026-05-20 | [`SPRINT_MVP1_FRIENDS_FIRST_SCREEN.md`](SPRINT_MVP1_FRIENDS_FIRST_SCREEN.md) |
| MVP1 belief-input UX | **COMPLETE** 2026-05-20 | [`SPRINT_MVP1_BELIEF_INPUT_UX.md`](SPRINT_MVP1_BELIEF_INPUT_UX.md) |
| MVP1 onboarding / How it works | **COMPLETE** 2026-05-20 | [`SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md`](SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md) |
| MVP1 disagreement strip polish | **COMPLETE** 2026-05-26 | [`SPRINT_MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH.md`](SPRINT_MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH.md) |
| Phase 3 commercial wrapper | **COMPLETE** 2026-05-28 | [`SPRINT_PHASE3_COMMERCIAL_WRAPPER.md`](SPRINT_PHASE3_COMMERCIAL_WRAPPER.md) |
| MVP1 Phase 6 trust metrics v1 | **COMPLETE** 2026-06-01 | [`SPRINT_MVP1_PHASE6_TRUST_METRICS_V1.md`](SPRINT_MVP1_PHASE6_TRUST_METRICS_V1.md) |
| MSOS Website Program P0 | **COMPLETE** 2026-06-01 | [`SPRINT_MSOS_WEBSITE_PROGRAM_P0.md`](SPRINT_MSOS_WEBSITE_PROGRAM_P0.md), [`MSOS_WEBSITE_PROGRAM_P0_EVIDENCE_STATUS.md`](MSOS_WEBSITE_PROGRAM_P0_EVIDENCE_STATUS.md) |
| MSOS P1 stack routing ADR | **COMPLETE** 2026-06-01 | [`SPRINT_MSOS_P1_STACK_ROUTING.md`](SPRINT_MSOS_P1_STACK_ROUTING.md), [`MSOS_P1_STACK_ROUTING_EVIDENCE_STATUS.md`](MSOS_P1_STACK_ROUTING_EVIDENCE_STATUS.md) |

| MSOS P2 design system + public homepage | **COMPLETE** 2026-06-02 | [`SPRINT_MSOS_P2_HOMEPAGE.md`](docs/SOP/SPRINT_MSOS_P2_HOMEPAGE.md), [`MSOS_P2_HOMEPAGE_EVIDENCE_STATUS.md`](docs/SOP/MSOS_P2_HOMEPAGE_EVIDENCE_STATUS.md) |

| MSOS P3 authenticated shell + Command Center | **COMPLETE** 2026-06-05 | [`SPRINT_MSOS_P3_COMMAND_CENTER.md`](docs/SOP/SPRINT_MSOS_P3_COMMAND_CENTER.md), [`MSOS_P3_COMMAND_CENTER_EVIDENCE_STATUS.md`](docs/SOP/MSOS_P3_COMMAND_CENTER_EVIDENCE_STATUS.md) |

| MVP1 BTC distribution export (Phase 1) | **COMPLETE** 2026-06-06 | [`SPRINT_MVP1_DISTRIBUTION_EXPORT.md`](docs/SOP/SPRINT_MVP1_DISTRIBUTION_EXPORT.md), [`MVP1_DISTRIBUTION_EXPORT_EVIDENCE_STATUS.md`](docs/SOP/MVP1_DISTRIBUTION_EXPORT_EVIDENCE_STATUS.md) |

| MSOS P4 Strategy Lab / PPE integration | **COMPLETE** 2026-06-09 | [`SPRINT_MSOS_P4_STRATEGY_LAB.md`](docs/SOP/SPRINT_MSOS_P4_STRATEGY_LAB.md), [`MSOS_P4_STRATEGY_LAB_EVIDENCE_STATUS.md`](docs/SOP/MSOS_P4_STRATEGY_LAB_EVIDENCE_STATUS.md) |

| Repo housekeeping v1 | **COMPLETE** 2026-06-10 | [`SPRINT_REPO_HOUSEKEEPING_V1.md`](docs/SOP/SPRINT_REPO_HOUSEKEEPING_V1.md), [`REPO_HOUSEKEEPING_V1_EVIDENCE_STATUS.md`](docs/SOP/REPO_HOUSEKEEPING_V1_EVIDENCE_STATUS.md) |

| MVP1 distribution stats legibility | **COMPLETE** 2026-06-11 | [`SPRINT_MVP1_DISTRIBUTION_STATS_LEGIBILITY.md`](docs/SOP/SPRINT_MVP1_DISTRIBUTION_STATS_LEGIBILITY.md), [`MVP1_DISTRIBUTION_STATS_LEGIBILITY_EVIDENCE_STATUS.md`](docs/SOP/MVP1_DISTRIBUTION_STATS_LEGIBILITY_EVIDENCE_STATUS.md) |

| MSOS Strategy Lab distribution demo | **COMPLETE** 2026-06-11 | [`SPRINT_MSOS_STRATEGY_LAB_DISTRIBUTION_DEMO.md`](docs/SOP/SPRINT_MSOS_STRATEGY_LAB_DISTRIBUTION_DEMO.md), [`MSOS_STRATEGY_LAB_DISTRIBUTION_DEMO_EVIDENCE_STATUS.md`](docs/SOP/MSOS_STRATEGY_LAB_DISTRIBUTION_DEMO_EVIDENCE_STATUS.md) |

| MSOS P5 thesis confirmation + durable state | **COMPLETE** 2026-06-11 | [`SPRINT_MSOS_P5_THESIS_CONFIRM.md`](docs/SOP/SPRINT_MSOS_P5_THESIS_CONFIRM.md), [`MSOS_P5_THESIS_CONFIRM_EVIDENCE_STATUS.md`](docs/SOP/MSOS_P5_THESIS_CONFIRM_EVIDENCE_STATUS.md) |

| MSOS P6 expression planning + simulation only | **COMPLETE** 2026-06-12 | [`SPRINT_MSOS_P6_EXPRESSION_SIM.md`](docs/SOP/SPRINT_MSOS_P6_EXPRESSION_SIM.md), [`MSOS_P6_EXPRESSION_SIM_EVIDENCE_STATUS.md`](docs/SOP/MSOS_P6_EXPRESSION_SIM_EVIDENCE_STATUS.md) |

| MSOS P7 monitoring, history, calibration loop | **COMPLETE** 2026-06-12 | [`SPRINT_MSOS_P7_MONITORING.md`](docs/SOP/SPRINT_MSOS_P7_MONITORING.md), [`MSOS_P7_MONITORING_EVIDENCE_STATUS.md`](docs/SOP/MSOS_P7_MONITORING_EVIDENCE_STATUS.md) |

| MSOS P8 tester release + evidence-based next selection | **COMPLETE** 2026-06-12 | [`SPRINT_MSOS_P8_TESTER_RELEASE.md`](docs/SOP/SPRINT_MSOS_P8_TESTER_RELEASE.md), [`MSOS_P8_TESTER_RELEASE_EVIDENCE_STATUS.md`](docs/SOP/MSOS_P8_TESTER_RELEASE_EVIDENCE_STATUS.md) |

| MVP1 cross-venue probability panel | **COMPLETE** 2026-06-13 | [`SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md`](docs/SOP/SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md), [`MVP1_CROSS_VENUE_PROB_PANEL_EVIDENCE_STATUS.md`](docs/SOP/MVP1_CROSS_VENUE_PROB_PANEL_EVIDENCE_STATUS.md) |

**Ops tail:** [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md) — VPS CTA + paid-interest remain steward.

---

## Engineering gates

See [`TESTING_TIERS_V1.md`](TESTING_TIERS_V1.md).

| Gate | When | Notes |
|------|------|-------|
| `python scripts/run_pushable_gate.py` | WIP commit | Scoped or fast pytest |
| `python scripts/run_pushable_gate.py --pre-push` | Before push | Full pytest (matches CI) |
| `python scripts/run_implied_lab_ui_smoke.py` | Viz PR merge | Scenario A default |
| Dual smoke | Harness-wide viz only | Optional; not every PR |
| CI `pytest` + `docker_entrypoint` | Merge to `main` | Required checks |

---

## Steward parallel checklist

| Item | Status | Action |
|------|--------|--------|
| **Active relay chapter** | **MSOS P3** | manifest `RUNNING`; P4 plan pre-chartered |
| VPS repo-root `.env` → **Research beta (v0)** CTA | **pending** | [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md) |
| Paid-interest live call | **N** (honest) | [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) |
| **Product focus playbook** | v1 installed | [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) — wedge proof before platform drift |
| **Storyboard v0.6** | **in-repo** | gate OPEN — MSOS P3 BUILD; P4 relay pre-chartered |

**After `run_ppe.cmd`:** read `artifacts/orchestrator/LAST_RUN_REPORT.md`; **new Cursor thread** with [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) only.

---

## Doc map

| Role | Path |
|------|------|
| **This one-pager** | [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) |
| MVP1 frontier | [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) |
| MSOS frontier | [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) |
| MSOS acceleration | [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md) |
| Product focus playbook | [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) |
| MSOS P1 ADR | [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md) |
| Session handoff | [`HANDOFF.md`](HANDOFF.md) |
| Deploy + CTA witness | [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) |

---

## Deferred (reconcile — do not BUILD without SELECTION)

| Path / topic | Decision |
|--------------|----------|
| [`src/viz/mvp1_benchmark_substrate.py`](../../src/viz/mvp1_benchmark_substrate.py) | **defer** — recovery-only |
| Blind [`src/viz/app.py`](../../src/viz/app.py) merge | **defer** |

---

## Next BUILD (agent lane)

**Await steward SELECTION** — [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](docs/SOP/MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md). **Worry audit:** [`PPE_RISK_REGISTER.md`](PPE_RISK_REGISTER.md).
