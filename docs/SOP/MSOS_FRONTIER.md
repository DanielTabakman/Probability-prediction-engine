## MSOS_FRONTIER

Purpose: live steering document for the **MSOS Website Program** (platform UI / customer-facing shell).

### Control rule (hard)

- **Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (waterfall queue, top section) + [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md)
- **This file** is the only live frontier for MSOS website/platform BUILD.
- **MVP1 engine relay** (Streamlit implied lab, freeze/review loop): [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) — idle unless a new MVP1 chapter is SELECTION'd.
- **On conflict (MSOS UI vs PPE math):** non-widening rule wins; MVP1 contracts unchanged.

### Current execution focus (MSOS framing)

- **Integrated status:** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
- **Active BUILD chapter:** **MSOS P3 authenticated shell + Command Center** — **READY** (SELECTION 2026-06-03)
- **Relay plan:** [`PHASE_PLANS/msos_p3_command_center_relay.json`](PHASE_PLANS/msos_p3_command_center_relay.json)
- **Sprint:** [`SPRINT_MSOS_P3_COMMAND_CENTER.md`](SPRINT_MSOS_P3_COMMAND_CENTER.md)
- **SELECTION:** [`POST_MSOS_P3_COMMAND_CENTER_SELECTION.md`](POST_MSOS_P3_COMMAND_CENTER_SELECTION.md)
- **Last closed:** **MSOS P2 design system + public homepage** — **COMPLETE** 2026-06-03
- **Evidence (P2):** [`MSOS_P2_HOMEPAGE_EVIDENCE_STATUS.md`](MSOS_P2_HOMEPAGE_EVIDENCE_STATUS.md)
- **Operator:** `run_ppe_local.cmd` — product slice via IDE BUILD + `mark_ide_product_ready.cmd MSOS-P3-Product-Slice002`

### MSOS P3 Command Center — relay queue — **READY** (2026-06-03)

| Status | Slice | Plane |
|--------|--------|-------|
| **NEXT** | `MSOS-P3-Control-Slice001` — charter | EVIDENCE |
| **PENDING** | `MSOS-P3-Product-Slice002` — shell + Command Center | PRODUCT |
| **PENDING** | `MSOS-P3-Platform-Slice003` — Access / routes | EVIDENCE |
| **PENDING** | `MSOS-P3-Witness-Slice004` — witness | EVIDENCE |
| **PENDING** | `MSOS-P3-Closeout-Slice005` — chapter close | EVIDENCE |

**Evidence:** [`MSOS_P3_COMMAND_CENTER_EVIDENCE_STATUS.md`](MSOS_P3_COMMAND_CENTER_EVIDENCE_STATUS.md)

### MSOS P2 homepage — relay queue — **COMPLETE** (2026-06-03)

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P2-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-P2-Product-Slice002` — Next.js homepage | PRODUCT |
| **CLOSED** | `MSOS-P2-Platform-Slice003` — Docker/Caddy wiring | EVIDENCE |
| **CLOSED** | `MSOS-P2-Witness-Slice004` — witness | EVIDENCE |
| **CLOSED** | `MSOS-P2-Closeout-Slice005` — chapter close | EVIDENCE |

**Evidence:** [`MSOS_P2_HOMEPAGE_EVIDENCE_STATUS.md`](MSOS_P2_HOMEPAGE_EVIDENCE_STATUS.md)

### MSOS Website Program P0 — relay queue — **COMPLETE** (2026-06-01)

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P0-Control-Slice001` — charter + queue install | EVIDENCE |
| **CLOSED** | `MSOS-P0-Witness-Slice002` — charter witness + queue health | EVIDENCE |
| **CLOSED** | `MSOS-P0-Closeout-Slice003` — chapter close | EVIDENCE |

**Evidence:** [`MSOS_WEBSITE_PROGRAM_P0_EVIDENCE_STATUS.md`](MSOS_WEBSITE_PROGRAM_P0_EVIDENCE_STATUS.md)

### MSOS P1 stack routing — relay queue — **COMPLETE** (2026-06-01)

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P1-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-P1-Product-Slice002` — stack/routing ADR | CONTROL |
| **CLOSED** | `MSOS-P1-Witness-Slice003` — witness | EVIDENCE |
| **CLOSED** | `MSOS-P1-Closeout-Slice004` — chapter close | EVIDENCE |

**Deliverable:** [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)

### Waterfall backlog (P1–P8)

| Priority | chapterId | Backlog status | Blocker |
|----------|-----------|----------------|---------|
| P1 | `msos_p1_stack_routing` | **done** | — |
| P2 | `msos_p2_homepage` | **done** | — |
| P3 | `msos_p3_command_center` | **queued / READY** | SELECTION 2026-06-03 — relay running |
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
