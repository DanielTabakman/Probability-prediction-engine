# MSOS Website Program — Selected Waterfall Queue

**Canon source:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (top section, imported 2026-06-01)  
**Live steering:** [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)  
**Live product sequence:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md)  
**Acceleration checklist:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md)  
**Storyboard gate (P2+):** [`docs/VISION/MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md)

Portable agent canon for the MSOS customer-facing website/platform program. PPE engine math and MVP1 evidence contracts remain unchanged unless a dedicated SELECTION chapter says otherwise.

---

## Product hierarchy (preserve)

- **Market Structure OS / MSOS** = company and software platform.
- **Command Center** = authenticated home and ongoing work surface.
- **Strategy Lab** = workspace for forming/testing theses and designing expressions.
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

### Later — Access identity + Monitor/History live (backlog stubs)

**Phases 4–5** in [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md): Cloudflare Access on MSOS routes + per-user scoping; then Monitor/History from combined state. Charter at SELECTION after phase 3.

---

## Deferred until selected after validation

- Live execution or order routing
- Hyperliquid integration beyond honest Pending representation
- Prediction-market or perps lenses as live tools
- Broad asset rollout
- Paywall beyond low-cost validation needs
- Claims of measured edge, profitability, formal TAM, or traction without evidence

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
| Live seq P2 | `msos_user_state_v1` | `PHASE_PLANS/msos_user_state_v1_relay.json` |
| Live seq P3 | `msos_workflow_persistence_v1` | `PHASE_PLANS/msos_workflow_persistence_v1_relay.json` |
| Live seq P4–5 | `msos_access_identity_v1`, `msos_monitor_history_live_v1` | _(SELECTION pending)_ |

**Live product sequence (phases 1–5):** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md)

Backlog rows stay **blocked** until the prior chapter is **done**; closeout then **auto-promotes** the next row to `queued` ([`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)).
