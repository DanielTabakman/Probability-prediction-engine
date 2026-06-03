# MSOS Website Program — Selected Waterfall Queue

**Canon source:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (top section, imported 2026-06-01)  
**Live steering:** [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)  
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
| P4 | `msos_p4_strategy_lab` | `PHASE_PLANS/msos_p4_strategy_lab_relay.json` (pre-chartered; **blocked** until P3 done) |
| P5–P8 | `msos_p5_thesis_confirm` … `msos_p8_tester_release` | Charter at SELECTION; **blocked** in backlog |
