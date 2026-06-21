# PPE integrated status — canonical one-pager

**As-of:** 2026-06-21 · **Baseline `main`:** verify `git rev-parse origin/main` after push  
**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) · **MVP1 steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) · **MSOS steering:** [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) · **MSOS acceleration:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md) · **Strategic focus:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md)

This file merges archived chapters, steward parallel work, engineering gates, and the doc map. On drift, **`MVP1_FRONTIER.md`** wins for MVP1 slice queue; **`MSOS_FRONTIER.md`** wins for MSOS website slice queue; this file wins for cross-chapter summary.

---

## Active BUILD — MCD track (phase 2 in flight)

| Field | Value |
|-------|--------|
| **MCD gate** | [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) — **PASSED** 2026-06-21 |
| **Sequence canon** | [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) — MCD track 1→3 + embed shell |
| **Active chapter** | `msos_user_state_v1` — Witness-Slice004 next |
| **Relay plan** | [`msos_user_state_v1_relay.json`](PHASE_PLANS/msos_user_state_v1_relay.json) |
| **Last closed slice** | `MSOS-UserStateV1-Platform-Slice003` (`main` #212) |
| **Next (blocked)** | `msos_workflow_persistence_v1` → `msos_strategy_lab_embed_shell_v1` (MCD-required) |
| **Post-MCD phases 4a–7b** | Built pre-pivot; **deferred** for product focus until MCD PASSED |
| **MSOS steering** | [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) |

**P1 decision:** Phased hybrid — **`apps/msos-web/`** (Next.js) MSOS shell; **Streamlit** PPE unchanged; **Cloudflare Access** on `app.*`; long-term MSOS workflow store server-side (phase 3) with PPE snapshot read feed (phase 2).

**MVP1 relay:** see [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md). **Operator:** `run_ppe_local.cmd` / `run_ppe.cmd`.

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

| MVP1 distribution quant research v2 | **COMPLETE** 2026-06-13 | [`SPRINT_MVP1_DISTRIBUTION_QUANT_RESEARCH_V2.md`](docs/SOP/SPRINT_MVP1_DISTRIBUTION_QUANT_RESEARCH_V2.md), [`MVP1_DISTRIBUTION_QUANT_RESEARCH_V2_EVIDENCE_STATUS.md`](docs/SOP/MVP1_DISTRIBUTION_QUANT_RESEARCH_V2_EVIDENCE_STATUS.md) |

| MSOS public demo launch v1 | **COMPLETE** 2026-06-14 | [`SPRINT_MSOS_PUBLIC_DEMO_LAUNCH_V1.md`](docs/SOP/SPRINT_MSOS_PUBLIC_DEMO_LAUNCH_V1.md), [`MSOS_PUBLIC_DEMO_LAUNCH_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_PUBLIC_DEMO_LAUNCH_V1_EVIDENCE_STATUS.md) |

| MSOS live product sequence P1–7b | **CHARTERED** 2026-06-14 | [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) — full product + commercial path |

| MSOS production wiring v1 | **COMPLETE** 2026-06-15 | [`SPRINT_MSOS_PRODUCTION_WIRING_V1.md`](docs/SOP/SPRINT_MSOS_PRODUCTION_WIRING_V1.md), [`MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md) |

| MSOS production wiring v1 | **COMPLETE** 2026-06-17 | [`SPRINT_MSOS_PRODUCTION_WIRING_V1.md`](docs/SOP/SPRINT_MSOS_PRODUCTION_WIRING_V1.md), [`MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md) |

| MSOS user state v1 — Command Center bridge | **IN PROGRESS** 2026-06-20 | [`SPRINT_MSOS_USER_STATE_V1.md`](docs/SOP/SPRINT_MSOS_USER_STATE_V1.md), [`MSOS_USER_STATE_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_USER_STATE_V1_EVIDENCE_STATUS.md) |

| MSOS workflow persistence v1 | **BLOCKED** (MCD phase 3) | [`SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md`](docs/SOP/SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md), [`MSOS_WORKFLOW_PERSISTENCE_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_WORKFLOW_PERSISTENCE_V1_EVIDENCE_STATUS.md) |

| MVP1 snapshot owner v1 | **COMPLETE** 2026-06-18 | [`SPRINT_MVP1_SNAPSHOT_OWNER_V1.md`](docs/SOP/SPRINT_MVP1_SNAPSHOT_OWNER_V1.md), [`MVP1_SNAPSHOT_OWNER_V1_EVIDENCE_STATUS.md`](docs/SOP/MVP1_SNAPSHOT_OWNER_V1_EVIDENCE_STATUS.md) |

| MSOS access identity v1 | **COMPLETE** 2026-06-18 | [`SPRINT_MSOS_ACCESS_IDENTITY_V1.md`](docs/SOP/SPRINT_MSOS_ACCESS_IDENTITY_V1.md), [`MSOS_ACCESS_IDENTITY_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_ACCESS_IDENTITY_V1_EVIDENCE_STATUS.md) |

| MSOS monitor & history live v1 | **COMPLETE** 2026-06-18 | [`SPRINT_MSOS_MONITOR_HISTORY_LIVE_V1.md`](docs/SOP/SPRINT_MSOS_MONITOR_HISTORY_LIVE_V1.md), [`MSOS_MONITOR_HISTORY_LIVE_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_MONITOR_HISTORY_LIVE_V1_EVIDENCE_STATUS.md) |

| MSOS entitlements & commercial beta v1 | **COMPLETE** 2026-06-19 | [`SPRINT_MSOS_ENTITLEMENTS_V1.md`](docs/SOP/SPRINT_MSOS_ENTITLEMENTS_V1.md), [`MSOS_ENTITLEMENTS_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_ENTITLEMENTS_V1_EVIDENCE_STATUS.md) |

| MSOS Strategy Lab embed shell v1 | **BLOCKED** (MCD-required, HIGH) | [`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](docs/SOP/SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md), [`MSOS_STRATEGY_LAB_EMBED_SHELL_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_STRATEGY_LAB_EMBED_SHELL_V1_EVIDENCE_STATUS.md) |

| MSOS end-to-end product witness v1 | **COMPLETE** 2026-06-19 | [`SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md`](docs/SOP/SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md), [`MSOS_E2E_PRODUCT_WITNESS_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_E2E_PRODUCT_WITNESS_V1_EVIDENCE_STATUS.md) |

| MSOS user state v1 — Command Center bridge | **COMPLETE** 2026-06-20 | [`SPRINT_MSOS_USER_STATE_V1.md`](docs/SOP/SPRINT_MSOS_USER_STATE_V1.md), [`MSOS_USER_STATE_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_USER_STATE_V1_EVIDENCE_STATUS.md) |

| MSOS Strategy Lab embed shell v1 | **COMPLETE** 2026-06-21 | [`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](docs/SOP/SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md), [`MSOS_STRATEGY_LAB_EMBED_SHELL_V1_EVIDENCE_STATUS.md`](docs/SOP/MSOS_STRATEGY_LAB_EMBED_SHELL_V1_EVIDENCE_STATUS.md) |

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
| **Active relay chapter** | **`msos_mcd_production_witness_v1`** — MCD sign-off witness | [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) · [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md) |
| VPS repo-root `.env` → **Research beta (v0)** CTA | **pending** | [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md) |
| Paid-interest live call | **N** (honest) | [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) |
| **Product focus playbook** | v1 installed | [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) — wedge proof before platform drift |
| **Live product sequence** | MCD track active; post-MCD **deferred** | [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) |
| **Commercial ADR** | PROPOSED | [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md) |

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

**Await steward SELECTION** — [`MSOS_FRONTIER.md`](docs/SOP/MSOS_FRONTIER.md). **Worry audit:** [`PPE_RISK_REGISTER.md`](PPE_RISK_REGISTER.md).
