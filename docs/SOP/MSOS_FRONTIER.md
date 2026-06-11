## MSOS_FRONTIER

Purpose: live steering document for the **MSOS Website Program** (platform UI / customer-facing shell).

### Control rule (hard)

- **Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (waterfall queue, top section) + [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md)
- **Acceleration playbook:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md)
- **This file** is the only live frontier for MSOS website/platform BUILD.
- **MVP1 engine relay** (Streamlit implied lab, freeze/review loop): [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) — idle unless a new MVP1 chapter is SELECTION'd.
- **On conflict (MSOS UI vs PPE math):** non-widening rule wins; MVP1 contracts unchanged.

### Current execution focus (MSOS framing)

- **Integrated status:** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
- **Active BUILD chapter:** **MSOS P5 thesis confirmation + durable state** — **READY** (relay running)
- **Relay plan:** [`PHASE_PLANS/msos_p5_thesis_confirm_relay.json`](PHASE_PLANS/msos_p5_thesis_confirm_relay.json)
- **Sprint:** [`SPRINT_MSOS_P5_THESIS_CONFIRM.md`](SPRINT_MSOS_P5_THESIS_CONFIRM.md)
- **SELECTION:** [`POST_MSOS_P5_THESIS_CONFIRM_SELECTION.md`](POST_MSOS_P5_THESIS_CONFIRM_SELECTION.md)
- **Last closed:** **MSOS Strategy Lab distribution demo** + **MVP1 distribution stats legibility** — on `main`
- **Operator:** IDE BUILD + `mark_ide_product_ready.cmd MSOS-P5-Product-Slice002` → `run_ppe_local.cmd`

### MSOS P5 thesis confirmation — relay queue — **READY**

| Status | Slice | Plane |
|--------|--------|-------|
| **PENDING** | `MSOS-P5-Control-Slice001` — charter | EVIDENCE |
| **IN PROGRESS** | `MSOS-P5-Product-Slice002` — confirmation UI + persistence boundary | PRODUCT |
| **PENDING** | `MSOS-P5-Witness-Slice004` — pytest + visual witness | EVIDENCE |
| **PENDING** | `MSOS-P5-Closeout-Slice005` — chapter close | EVIDENCE |

**Visual reference:** storyboard `04_confirmation` · **Route:** `/strategy-lab/confirm` · **Persistence:** `localStorage` preview (`msos.thesis.preview.v1`)

### MSOS P4 Strategy Lab — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P4-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-P4-Product-Slice002` — Strategy Lab route + embed boundary | PRODUCT |
| **CLOSED** | `MSOS-P4-Platform-Slice003` — Caddy/compose proxy | EVIDENCE |
| **CLOSED** | `MSOS-P4-Witness-Slice004` — witness | EVIDENCE |
| **CLOSED** | `MSOS-P4-Closeout-Slice005` — chapter close | EVIDENCE |

**Visual reference:** storyboard `03_ppe_lab` · **Embed:** `NEXT_PUBLIC_PPE_EMBED_URL`

### MSOS P3 Command Center — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P3-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-P3-Product-Slice002` — shell + Command Center | PRODUCT |
| **CLOSED** | `MSOS-P3-Platform-Slice003` — Access / routes | EVIDENCE |
| **CLOSED** | `MSOS-P3-Witness-Slice004` — witness | EVIDENCE |
| **CLOSED** | `MSOS-P3-Closeout-Slice005` — chapter close | EVIDENCE |

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
| P3 | `msos_p3_command_center` | **done** | — |
| P4 | `msos_p4_strategy_lab` | **done** | — |
| P5 | `msos_p5_thesis_confirm` | **queued / READY** | Relay running — product slice IDE BUILD |
| P6 | `msos_p6_expression_sim` | **blocked** (pre-chartered) | After P5 |
| P7 | `msos_p7_monitoring` | **blocked** (pre-chartered) | After P6 |
| P8 | `msos_p8_tester_release` | **blocked** (pre-chartered) | After P7 |

See [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) for propagation state.

### Non-goals (MSOS track)

- Rewriting PPE math in frontend code
- Live execution / order routing (deferred per master)
- Starting P2+ without [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) satisfied
