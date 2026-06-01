## MSOS_FRONTIER

Purpose: live steering document for the **MSOS Website Program** (platform UI / customer-facing shell).

### Control rule (hard)

- **Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (waterfall queue, top section) + [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md)
- **This file** is the only live frontier for MSOS website/platform BUILD.
- **MVP1 engine relay** (Streamlit implied lab, freeze/review loop): [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) — idle unless a new MVP1 chapter is SELECTION'd.
- **On conflict (MSOS UI vs PPE math):** non-widening rule wins; MVP1 contracts unchanged.

### Current execution focus (MSOS framing)

- **Integrated status:** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
- **Active BUILD chapter:** **MSOS P1 stack routing ADR** — ADR committed; relay witness/closeout via `run_ppe_local.cmd`
- **ADR:** [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md) — phased Next.js shell + Streamlit PPE (proxy at P4)
- **Sprint:** [`SPRINT_MSOS_P1_STACK_ROUTING.md`](SPRINT_MSOS_P1_STACK_ROUTING.md)
- **Phase plan:** [`PHASE_PLANS/msos_p1_stack_routing_relay.json`](PHASE_PLANS/msos_p1_stack_routing_relay.json)

### MSOS Website Program — relay queue

### MSOS Website Program P0 — relay queue — **COMPLETE** (2026-06-01)

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P0-Control-Slice001` — charter + queue install | EVIDENCE |
| **CLOSED** | `MSOS-P0-Witness-Slice002` — charter witness + queue health | EVIDENCE |
| **CLOSED** | `MSOS-P0-Closeout-Slice003` — chapter close | EVIDENCE |

**Evidence:** [`MSOS_WEBSITE_PROGRAM_P0_EVIDENCE_STATUS.md`](MSOS_WEBSITE_PROGRAM_P0_EVIDENCE_STATUS.md)

### MSOS P1 stack routing — relay queue — **IN PROGRESS**

| Status | Slice | Plane |
|--------|--------|-------|
| **OPEN** | `MSOS-P1-Control-Slice001` — charter | EVIDENCE |
| **DONE (IDE)** | `MSOS-P1-Product-Slice002` — stack/routing ADR | CONTROL |
| **OPEN** | `MSOS-P1-Witness-Slice003` — witness | EVIDENCE |
| **OPEN** | `MSOS-P1-Closeout-Slice004` — chapter close | EVIDENCE |

**Deliverable:** [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)

### Waterfall backlog (P1–P8)

| Priority | chapterId | Backlog status | Blocker |
|----------|-----------|----------------|---------|
| P1 | `msos_p1_stack_routing` | **chartered** | Relay closeout pending |
| P2 | `msos_p2_homepage` | **blocked** | Storyboard v0.6 not in-repo |
| P3 | `msos_p3_command_center` | **blocked** | After P2 |
| P4 | `msos_p4_strategy_lab` | **blocked** | After P3; PPE via Caddy proxy (ADR) |
| P5 | `msos_p5_thesis_confirm` | **blocked** | After P4 |
| P6 | `msos_p6_expression_sim` | **blocked** | After P5 |
| P7 | `msos_p7_monitoring` | **blocked** | After P6 |
| P8 | `msos_p8_tester_release` | **blocked** | After P7 |

See [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) for propagation state.

### Non-goals (MSOS track)

- Rewriting PPE math in frontend code
- Live execution / order routing (deferred per master)
- Starting P2+ without [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) satisfied
