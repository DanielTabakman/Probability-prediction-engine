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
- **Active BUILD chapter:** **none on MSOS track** — MVP1 dist-quant v2 finishing on parallel queue ([`MVP1_FRONTIER.md`](MVP1_FRONTIER.md))
- **Next MSOS chapter (chartered, MEDIUM):** **Storyboard visual parity v1** — blocked until dist-quant closeout
- **Relay plan:** [`PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json`](PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json)
- **Sprint:** [`SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md`](SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md)
- **SELECTION:** [`POST_MSOS_STORYBOARD_VISUAL_PARITY_V1_SELECTION.md`](POST_MSOS_STORYBOARD_VISUAL_PARITY_V1_SELECTION.md)
- **Last closed:** **MSOS P8 tester release** — 2026-06-12 on `main`

### MSOS storyboard visual parity v1 — relay queue — **BLOCKED** (MEDIUM)

| Status | Slice | Plane |
|--------|--------|-------|
| **PENDING** | `MSOS-VisParityV1-Control-Slice001` — charter + witness checklist | EVIDENCE |
| **PENDING** | `MSOS-VisParityV1-Product-Slice002` — homepage (`01_home`) | PRODUCT |
| **PENDING** | `MSOS-VisParityV1-Product-Slice003` — shell + Command Center (`02`, `08`) | PRODUCT |
| **PENDING** | `MSOS-VisParityV1-Product-Slice004` — Strategy Lab chrome (`03`) | PRODUCT |
| **PENDING** | `MSOS-VisParityV1-Product-Slice005` — thesis + expression (`04`, `05`) | PRODUCT |
| **PENDING** | `MSOS-VisParityV1-Product-Slice006` — monitor, history, learn (`06`, `07`, `09`) | PRODUCT |
| **PENDING** | `MSOS-VisParityV1-Platform-Slice007` — VPS deploy + routing | EVIDENCE |
| **PENDING** | `MSOS-VisParityV1-Witness-Slice008` — screenshot witness | EVIDENCE |
| **PENDING** | `MSOS-VisParityV1-Closeout-Slice009` — chapter close | EVIDENCE |

**Visual reference:** storyboard `01_home` … `09_conclusion` · **Compare:** `prototype/html/*.html` side-by-side with `npm run dev`

### MSOS public demo launch v1 — relay queue — **BLOCKED** (MEDIUM, after parity)

| Status | Slice | Plane |
|--------|--------|-------|
| **PENDING** | `MSOS-PublicLaunchV1-Control-Slice001` — charter | EVIDENCE |
| **PENDING** | `MSOS-PublicLaunchV1-Platform-Slice002` — VPS deploy + Caddy | EVIDENCE |
| **PENDING** | `MSOS-PublicLaunchV1-Product-Slice003` — research beta CTA | PRODUCT |
| **PENDING** | `MSOS-PublicLaunchV1-Witness-Slice004` — URL witness | EVIDENCE |
| **PENDING** | `MSOS-PublicLaunchV1-Closeout-Slice005` — closeout + operator check-in | EVIDENCE |

**Charter:** [`SPRINT_MSOS_PUBLIC_DEMO_LAUNCH_V1.md`](SPRINT_MSOS_PUBLIC_DEMO_LAUNCH_V1.md) · **Blocked until** visual parity COMPLETE

### MVP1 mobile research demo v1 — **BLOCKED** (P3, after public launch)

| Field | Value |
|-------|--------|
| **chapterId** | `mvp1_mobile_research_demo_v1` |
| **Backlog** | `blocked` — no relay plan yet |
| **Runs after** | `msos_public_demo_launch_v1` closeout (`queueAfterPlanPath`) |
| **SELECTION** | [`POST_MVP1_MOBILE_RESEARCH_DEMO_V1_SELECTION.md`](POST_MVP1_MOBILE_RESEARCH_DEMO_V1_SELECTION.md) |

Phone-friendly Streamlit demo layout + 3-min script. Charter sprint/relay when public URL is live, then `ppe_queue_insert_after.py`.

### MSOS P8 tester release — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P8-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-P8-Product-Slice002` — conclusion / learn loop UI | PRODUCT |
| **CLOSED** | `MSOS-P8-Witness-Slice004` — witness + validation report stub | EVIDENCE |
| **CLOSED** | `MSOS-P8-Closeout-Slice005` — closeout + next-queue note | EVIDENCE |

**Visual reference:** storyboard `09_conclusion` · **Route:** `/learn`

### MSOS P7 monitoring — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P7-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-P7-Product-Slice002` — monitor + history + updated Command Center | PRODUCT |
| **CLOSED** | `MSOS-P7-Witness-Slice004` — pytest + visual witness | EVIDENCE |
| **CLOSED** | `MSOS-P7-Closeout-Slice005` — chapter close | EVIDENCE |

**Visual reference:** storyboard `06_monitor` / `07_history` / `08_updated_command` · **Routes:** `/monitor`, `/history`

### MSOS P6 expression planning — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P6-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-P6-Product-Slice002` — expression planning + sim-only save | PRODUCT |
| **CLOSED** | `MSOS-P6-Witness-Slice004` — pytest + visual witness | EVIDENCE |
| **CLOSED** | `MSOS-P6-Closeout-Slice005` — chapter close | EVIDENCE |

**Visual reference:** storyboard `05_execution` · **Route:** `/strategy-lab/expression` · **Persistence:** `localStorage` preview (`msos.expression.preview.v1`)

### MSOS P5 thesis confirmation — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-P5-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-P5-Product-Slice002` — confirmation UI + persistence boundary | PRODUCT |
| **CLOSED** | `MSOS-P5-Witness-Slice004` — pytest + visual witness | EVIDENCE |
| **CLOSED** | `MSOS-P5-Closeout-Slice005` — chapter close | EVIDENCE |

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
| P5 | `msos_p5_thesis_confirm` | **done** | — |
| P6 | `msos_p6_expression_sim` | **done** | — |
| P7 | `msos_p7_monitoring` | **done** | — |
| P8 | `msos_p8_tester_release` | **queued / READY** | Relay running — product slice IDE BUILD |

See [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) for propagation state.

### Non-goals (MSOS track)

- Rewriting PPE math in frontend code
- Live execution / order routing (deferred per master)
- Starting P2+ without [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) satisfied
