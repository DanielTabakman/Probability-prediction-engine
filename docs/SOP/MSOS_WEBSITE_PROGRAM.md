# MSOS Website Program — Selected Waterfall Queue

**Canon source:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (top section, imported 2026-06-01)  
**Strategic umbrella:** [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md) · **MCD gate:** [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md)  
**Live steering:** [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)  
**Live product sequence:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md)  
**Acceleration checklist:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md)  
**Storyboard gate (P2+):** [`docs/VISION/MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md)  
**UX design philosophy (user-facing modules):** [`MSOS_UX_DESIGN_PHILOSOPHY_V1.md`](MSOS_UX_DESIGN_PHILOSOPHY_V1.md)

Portable agent canon for the MSOS customer-facing website/platform program. PPE engine math and MVP1 evidence contracts remain unchanged unless a dedicated SELECTION chapter says otherwise.

---

## Product hierarchy (preserve)

- **Market Structure OS / MSOS** = company and software platform.
- **Command Center** = authenticated home and ongoing work surface.
- **Strategy Lab** = workspace for forming/testing theses and designing expressions.
- **Options Horizon** = chart-first workspace (price × time + options-implied forward + region thesis); **v1 route live** at `/options-horizon`; **chart polish chartered** ([`POST_OPTIONS_HORIZON_CHART_POLISH_V1_SELECTION.md`](POST_OPTIONS_HORIZON_CHART_POLISH_V1_SELECTION.md)) — peer to Strategy Lab, not PPE.
- **PPE** = first tool inside Strategy Lab (not the whole platform).
- **BTC options** = first enabled PPE surface, not permanent product identity.
- **Existing PPE engine/math truth** remains controlling for calculations.

## Non-widening rule

MSOS UI work must wrap or expose PPE truth honestly. It must not silently alter PPE mathematical contracts, resolved MVP1 evidence, or existing engine validation requirements. Not-yet-shipped surfaces stay **Planned**, **Pending**, or **Simulation only**.

## Visual reference rule

Approved direction: **Market Structure OS Website Storyboard v0.6**. P0 and P1 do not require storyboard assets in-repo. **Before P2** (any user-facing visual implementation), storyboard PDF/montage or equivalent must land under [`docs/VISION/MSOS/`](../VISION/MSOS_STORYBOARD_GATE.md). Major finished surfaces include screenshot witness; report deviations via normal queue closeout.

---

## Priority stack

### P0 — Install program into repo canon and automated queue

**Outcome:** Future implementation no longer confuses MSOS, Strategy Lab, PPE, and BTC.  
**Work:** Product hierarchy + non-widening rule in repo frontier/continuity; P1–P8 in backlog/queue; storyboard gate documented.  
**Done when:** Native repo queue contains the ordered program; agents read hierarchy before UI work.

### P1 — Stack / routing decision without rewriting PPE

**Outcome:** Smallest stable path for the real product surface.  
**Work:** Inspect repo frontend roots, auth/login, deployment, Streamlit PPE app, testing/hosting. Extend existing frontend or select customer-facing shell + PPE adapter/API. Next.js + TypeScript is a candidate, not forced.  
**Done when:** Committed ADR ([`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)) unblocks P2.

### P2 — Design system + public MSOS homepage

**Reference:** Storyboard homepage ([`storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md)). **Ready for SELECTION** (gate OPEN, relay plan installed 2026-06-02).  
**Outcome:** Investor/customer-facing public entry (Read → State → Fit → Learn; honest BTC/PPE preview).

### P3 — Authenticated shell + Command Center

**Reference:** Storyboard Command Center. Fixture data where backend not real; honest Live/Soon/Planned.

### P4 — Strategy Lab / PPE integration

**Reference:** Storyboard Strategy Lab/PPE. PPE via lowest-risk boundary; no PPE math in frontend.

### P5 — Thesis confirmation + durable state

Exploring → Draft thesis → Confirmed thesis; persistence; CTA = expression planning, not execute.

### P6 — Expression planning + simulation only

Best-fit expression under constraints; Hyperliquid Pending unless implemented; no live orders.

### P7 — Monitoring, history, calibration loop

Distinct observed/saved/simulated/executed/reviewed states; no undefined thesis-health metrics.

### P8 — Tester release and evidence-based next selection

Friends-first/trader-tester conventions; validation report drives next queue selection.

### Post-P8 — Storyboard visual parity v1 (follow-on, chartered)

**Outcome:** `apps/msos-web/` matches storyboard v0.6 **pictures** (layout, tokens, panel chrome), not narrative-only parity.  
**Work:** Screen-by-screen witness vs `prototype/html/*.html`; VPS deploy; closes deferred pixel checks from P2–P8 evidence.  
**Priority:** MEDIUM — runs after current LOW dist-quant chapter unless a higher tier is SELECTION'd.  
**Charter:** [`SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md`](SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md) · [`POST_MSOS_STORYBOARD_VISUAL_PARITY_V1_SELECTION.md`](POST_MSOS_STORYBOARD_VISUAL_PARITY_V1_SELECTION.md)

### Post-launch — Production wiring v1 (follow-on, chartered)

**Outcome:** Apex MSOS shell **behaves** like a real product walkthrough — sign-in to `app.*`, live PPE embed, env-driven CTAs, wired navigation. Command Center may still use fixtures until phase 2.  
**Work:** Product slice (nav, sign-in, CTA) + platform slice (compose/Caddy/env) + operator witness.  
**Priority:** HIGH — [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) **phase 1**.  
**Charter:** [`SPRINT_MSOS_PRODUCTION_WIRING_V1.md`](SPRINT_MSOS_PRODUCTION_WIRING_V1.md) · [`POST_MSOS_PRODUCTION_WIRING_V1_SELECTION.md`](POST_MSOS_PRODUCTION_WIRING_V1_SELECTION.md)

### Post-wiring — User state v1 / Command Center bridge (chartered)

**Outcome:** Command Center reads **real PPE snapshots** (read-only) with honest labeling — not fixture KPIs.  
**Priority:** HIGH — sequence **phase 2**.  
**Charter:** [`SPRINT_MSOS_USER_STATE_V1.md`](SPRINT_MSOS_USER_STATE_V1.md) · [`POST_MSOS_USER_STATE_V1_SELECTION.md`](POST_MSOS_USER_STATE_V1_SELECTION.md)

### Post-bridge — Workflow persistence v1 (chartered)

**Outcome:** MSOS theses/expressions **server-side**; Command Center draft/confirmed from MSOS store; optional link to PPE snapshots.  
**Priority:** HIGH — sequence **phase 3** (long-term workflow canon).  
**Charter:** [`SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md`](SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md) · [`POST_MSOS_WORKFLOW_PERSISTENCE_V1_SELECTION.md`](POST_MSOS_WORKFLOW_PERSISTENCE_V1_SELECTION.md)

### Post-bridge — Strategy Lab embed shell v1 (chartered)

**Outcome:** `/strategy-lab` chart region matches storyboard **`03_ppe_lab`** — one cohesive MSOS surface, not full Streamlit app chrome inside an iframe box. PPE math stays in Python via read-only display API and/or chromeless embed-only view.  
**Priority:** MEDIUM — runs after phase 3 closeout; does not block phases 4a–7.  
**Charter:** [`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md) · [`POST_MSOS_STRATEGY_LAB_EMBED_SHELL_V1_SELECTION.md`](POST_MSOS_STRATEGY_LAB_EMBED_SHELL_V1_SELECTION.md)

### Later — Access identity + Monitor/History live (chartered)

Phases **4a–5** in [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md).

### Later — E2E witness (chartered)

Phase **6:** [`SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md`](SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md) — full production journey checklist.

### Commercial — Entitlements + Stripe (chartered)

| Phase | Chapter | When |
|-------|---------|------|
| **7a** | [`msos_entitlements_v1`](SPRINT_MSOS_ENTITLEMENTS_V1.md) | Free accounts; manual paid upgrade; ADR [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md) |
| **7b** | [`msos_billing_stripe_v1`](SPRINT_MSOS_BILLING_STRIPE_V1.md) | Stripe Checkout — **chartered, BUILD deferred** until operator configures Stripe |

**Intent:** Test willingness to pay via manual/invoice path first (7a); self-serve Stripe when ready (7b) without rework.

---

## Deferred until selected after validation

- Live execution or order routing
- Hyperliquid integration beyond honest Pending representation
- Prediction-market or perps lenses as live tools
- Broad asset rollout
- Claims of measured edge, profitability, formal TAM, or traction without evidence

**Commercial note:** Paywall and Stripe are **not deferred indefinitely** — see live sequence phases **7a–7b**. Generic “paywall automation” in backlog is superseded by [`msos_entitlements_v1`](SPRINT_MSOS_ENTITLEMENTS_V1.md) + [`msos_billing_stripe_v1`](SPRINT_MSOS_BILLING_STRIPE_V1.md).

---

## Relay mapping (repo)

| Priority | chapterId | planPath (when chartered) |
|----------|-----------|---------------------------|
| P0 | `msos_website_program_p0` | `PHASE_PLANS/msos_website_program_p0_relay.json` |
| P1 | `msos_p1_stack_routing` | `PHASE_PLANS/msos_p1_stack_routing_relay.json` |
| P2 | `msos_p2_homepage` | `PHASE_PLANS/msos_p2_homepage_relay.json` |
| P3 | `msos_p3_command_center` | `PHASE_PLANS/msos_p3_command_center_relay.json` |
| P4 | `msos_p4_strategy_lab` | `PHASE_PLANS/msos_p4_strategy_lab_relay.json` |
| P5 | `msos_p5_thesis_confirm` | `PHASE_PLANS/msos_p5_thesis_confirm_relay.json` |
| P6 | `msos_p6_expression_sim` | `PHASE_PLANS/msos_p6_expression_sim_relay.json` |
| P7 | `msos_p7_monitoring` | `PHASE_PLANS/msos_p7_monitoring_relay.json` |
| P8 | `msos_p8_tester_release` | `PHASE_PLANS/msos_p8_tester_release_relay.json` |
| Post-P8 | `msos_storyboard_visual_parity_v1` | `PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json` |
| Post-launch | `msos_public_demo_launch_v1` | `PHASE_PLANS/msos_public_demo_launch_v1_relay.json` |
| Post-launch | `msos_production_wiring_v1` | `PHASE_PLANS/msos_production_wiring_v1_relay.json` |
| Live seq P3 | `msos_workflow_persistence_v1` | `PHASE_PLANS/msos_workflow_persistence_v1_relay.json` |
| Post-P3 UX | `msos_strategy_lab_embed_shell_v1` | `PHASE_PLANS/msos_strategy_lab_embed_shell_v1_relay.json` |
| Live seq 4a | `mvp1_snapshot_owner_v1` | `PHASE_PLANS/mvp1_snapshot_owner_v1_relay.json` |
| Live seq 4b | `msos_access_identity_v1` | `PHASE_PLANS/msos_access_identity_v1_relay.json` |
| Live seq 5 | `msos_monitor_history_live_v1` | `PHASE_PLANS/msos_monitor_history_live_v1_relay.json` |
| Live seq 6 | `msos_e2e_product_witness_v1` | `PHASE_PLANS/msos_e2e_product_witness_v1_relay.json` |
| Live seq 7a | `msos_entitlements_v1` | `PHASE_PLANS/msos_entitlements_v1_relay.json` |
| Live seq 7b | `msos_billing_stripe_v1` | `PHASE_PLANS/msos_billing_stripe_v1_relay.json` |

**Live product sequence:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) · **Commercial ADR:** [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md)

Backlog rows stay **blocked** until the prior chapter is **done**; closeout then **auto-promotes** the next row to `queued` ([`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)).
