## MSOS_FRONTIER

Purpose: live steering document for the **MSOS Website Program** (platform UI / customer-facing shell).

### Active strategic frame

<!-- ACTIVE_PRODUCT_DIRECTION:START -->
**Direction pivot:** `crypto-multi-asset-v1` · **as-of:** 2026-06-25

- **North star:** See what BTC options imply, where you disagree, and what payoff fits — in under 15 seconds.
- **Primary focus:** G-05 crypto expansion — Deribit ETH + asset registry after usable demo COMPLETE
- **Stage:** multi_asset_expansion — storyboard design **complete** ([`storyboard-v0.6`](docs/VISION/MSOS/storyboard-v0.6/prototype/html/)); **BUILD** integration is active
- **Active BUILD chapter:** `ppe_crypto_multi_asset_v1` · plan [`ppe_crypto_multi_asset_v1_relay.json`](docs/SOP/PHASE_PLANS/ppe_crypto_multi_asset_v1_relay.json)
- **Next steward action:** First slice PPE-CryptoMA-Control-Slice001 — run_ppe.cmd or IDE BUILD starter after manifest READY

**Retired (do not steer BUILD by these):**
- ~~friends-first / friends-and-family cohort gating before demo ships~~ — **retired** by pivot `crypto-multi-asset-v1`
- ~~trader workflow research as primary BUILD blocker~~ — **retired** by pivot `crypto-multi-asset-v1`
- ~~validation-before-build for MSOS shell integration~~ — **retired** by pivot `crypto-multi-asset-v1`
- ~~stocks before crypto multi-asset automation~~ — **retired** by pivot `crypto-multi-asset-v1`

**Side channels (optional, not gates):**
- **TRADER_WORKFLOW_RESEARCH_V1** ([`TRADER_WORKFLOW_RESEARCH_V1.md`](docs/SOP/TRADER_WORKFLOW_RESEARCH_V1.md)) — optional signal logging while demo is built — not scope authority
- **VALIDATION_REALITY_CHECKS** ([`VALIDATION_REALITY_CHECKS.md`](docs/SOP/VALIDATION_REALITY_CHECKS.md)) — session notes when testers use the demo — not a gate
- **POST_PPE_EQUITY_OPTIONS_V1_SELECTION** ([`POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md`](docs/SOP/POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md)) — chartered deferred — NVDA/LEAPS after crypto chapter + G-04 signal
<!-- ACTIVE_PRODUCT_DIRECTION:END -->

- **MSOS** = platform-shaped shell around **PPE** (narrow scope, future-platform-ready architecture).
- **Direction SSOT:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) · pivot runbook [`PRODUCT_DIRECTION_PIVOT_V1.md`](PRODUCT_DIRECTION_PIVOT_V1.md)
- **Do not expand** platform scope (identity, entitlements, Stripe, multi-asset) until usable demo is walkable unless **explicitly SELECTION'd**.
- **Canon:** [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md) · [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md)

### Control rule (hard)

- **Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (waterfall queue, top section) + [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md)
- **Acceleration playbook:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md)
- **This file** is the only live frontier for MSOS website/platform BUILD.
- **MVP1 engine relay** (Streamlit implied lab, freeze/review loop): [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) — idle unless a new MVP1 chapter is SELECTION'd.
- **On conflict (MSOS UI vs PPE math):** non-widening rule wins; MVP1 contracts unchanged.

### Current execution focus (MSOS framing)

- **Integrated status:** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
- **Active BUILD chapter:** `msos_usable_demo_v1` — storyboard BUILD + PPE integration ([`SPRINT_MSOS_USABLE_DEMO_V1.md`](SPRINT_MSOS_USABLE_DEMO_V1.md))
- **Last closed:** **MSOS MCD production witness v1** — 2026-06-21
- **MCD gate:** [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) — **PASSED** 2026-06-21 (criteria met; demo hardening continues under usable-demo chapter)
- **Commercial ADR:** [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md) — **post-demo unless SELECTION'd**
- **Foundation shipped:** `production_wiring` ✓ → `user_state` ✓ → `workflow` ✓ → `embed_shell` ✓ (engineering); **walkable demo** = active BUILD
- **Expansion pipeline (deferred):** `snapshot_owner` → `access_identity` → `monitor_history` → `e2e_witness` → `entitlements` → `billing_stripe`

### Live product sequence — phases 4–7 (chartered, post-MCD deferred)

| Phase | chapterId | Status |
|-------|-----------|--------|
| 4a | `mvp1_snapshot_owner_v1` | BLOCKED — PPE `owner_email` |
| 4b | `msos_access_identity_v1` | BLOCKED — Access on MSOS routes |
| 5 | `msos_monitor_history_live_v1` | BLOCKED — live monitor/history |
| 6 | `msos_e2e_product_witness_v1` | BLOCKED — full journey witness |
| 7a | `msos_entitlements_v1` | BLOCKED — **free tier** + manual paid |
| 7b | `msos_billing_stripe_v1` | BLOCKED — **Stripe** (BUILD when operator ready) |

### MSOS production wiring v1 — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-ProdWireV1-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-ProdWireV1-Product-Slice002` — sign-in, CTA, nav/button wiring (`main` #170) | PRODUCT |
| **CLOSED** | `MSOS-ProdWireV1-Platform-Slice003` — compose/Caddy/env + deploy docs (`main` #171) | EVIDENCE |
| **CLOSED** | `MSOS-ProdWireV1-Witness-Slice004` — pytest + operator checklist | EVIDENCE |
| **CLOSED** | `MSOS-ProdWireV1-Closeout-Slice005` — closeout + check-in | EVIDENCE |

**Evidence:** [`MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md`](MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md)

### MSOS user state v1 — relay queue — **ACTIVE** (HIGH, phase 2)

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-UserStateV1-Control-Slice001` — charter | EVIDENCE |
| **DONE** | `MSOS-UserStateV1-Product-Slice002` — Command Center + snapshot read API (`main` #184) | PRODUCT |
| **PENDING** | `MSOS-UserStateV1-Platform-Slice003` — read-only snapshot volume on `msos_web` | EVIDENCE |
| **PENDING** | `MSOS-UserStateV1-Witness-Slice004` — pytest + operator checklist | EVIDENCE |
| **PENDING** | `MSOS-UserStateV1-Closeout-Slice005` — closeout | EVIDENCE |

**Charter:** [`SPRINT_MSOS_USER_STATE_V1.md`](SPRINT_MSOS_USER_STATE_V1.md) · **Precondition met:** production wiring COMPLETE · **Next:** platform slice then witness/closeout

### MSOS workflow persistence v1 — relay queue — **BLOCKED** (HIGH, phase 3)

| Status | Slice | Plane |
|--------|--------|-------|
| **PENDING** | `MSOS-WorkflowV1-Control-Slice001` — charter | EVIDENCE |
| **PENDING** | `MSOS-WorkflowV1-Product-Slice002` — server thesis/expression store | PRODUCT |
| **PENDING** | `MSOS-WorkflowV1-Platform-Slice003` — compose volume | EVIDENCE |
| **PENDING** | `MSOS-WorkflowV1-Witness-Slice004` — pytest + witness | EVIDENCE |
| **PENDING** | `MSOS-WorkflowV1-Closeout-Slice005` — closeout | EVIDENCE |

**Charter:** [`SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md`](SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md) · **Blocked until** user state bridge COMPLETE

### MSOS Strategy Lab embed shell v1 — relay queue — **BLOCKED** (HIGH, MCD-required — post–phase 3)

| Status | Slice | Plane |
|--------|--------|-------|
| **PENDING** | `MSOS-EmbedShellV1-Control-Slice001` — charter | EVIDENCE |
| **PENDING** | `MSOS-EmbedShellV1-Product-Slice002` — PPE read-only display boundary | PRODUCT |
| **PENDING** | `MSOS-EmbedShellV1-Product-Slice003` — MSOS chart shell (`03_ppe_lab`) | PRODUCT |
| **PENDING** | `MSOS-EmbedShellV1-Platform-Slice004` — Caddy/compose/deploy | EVIDENCE |
| **PENDING** | `MSOS-EmbedShellV1-Witness-Slice005` — pytest + visual witness | EVIDENCE |
| **PENDING** | `MSOS-EmbedShellV1-Closeout-Slice006` — closeout | EVIDENCE |

**Charter:** [`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md) · **Blocked until** workflow persistence COMPLETE · **Does not block** phases 4a–7

### MSOS storyboard visual parity v1 — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-VisParityV1-Control-Slice001` — charter + witness checklist | EVIDENCE |
| **CLOSED** | `MSOS-VisParityV1-Product-Slice002` — homepage (`01_home`) | PRODUCT |
| **CLOSED** | `MSOS-VisParityV1-Product-Slice003` — shell + Command Center (`02`, `08`) | PRODUCT |
| **CLOSED** | `MSOS-VisParityV1-Product-Slice004` — Strategy Lab chrome (`03`) | PRODUCT |
| **CLOSED** | `MSOS-VisParityV1-Product-Slice005` — thesis + expression (`04`, `05`) | PRODUCT |
| **CLOSED** | `MSOS-VisParityV1-Product-Slice006` — monitor, history, learn (`06`, `07`, `09`) | PRODUCT |
| **CLOSED** | `MSOS-VisParityV1-Platform-Slice007` — VPS deploy + routing | EVIDENCE |
| **CLOSED** | `MSOS-VisParityV1-Witness-Slice008` — screenshot witness | EVIDENCE |
| **CLOSED** | `MSOS-VisParityV1-Closeout-Slice009` — chapter close | EVIDENCE |

**Evidence:** [`MSOS_STORYBOARD_VISUAL_PARITY_V1_EVIDENCE_STATUS.md`](MSOS_STORYBOARD_VISUAL_PARITY_V1_EVIDENCE_STATUS.md)

### MSOS public demo launch v1 — relay queue — **COMPLETE**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MSOS-PublicLaunchV1-Control-Slice001` — charter | EVIDENCE |
| **CLOSED** | `MSOS-PublicLaunchV1-Platform-Slice002` — VPS deploy + Caddy | EVIDENCE |
| **CLOSED** | `MSOS-PublicLaunchV1-Product-Slice003` — research beta CTA | PRODUCT |
| **CLOSED** | `MSOS-PublicLaunchV1-Witness-Slice004` — URL witness | EVIDENCE |
| **CLOSED** | `MSOS-PublicLaunchV1-Closeout-Slice005` — closeout + operator check-in | EVIDENCE |

**Evidence:** [`MSOS_PUBLIC_DEMO_LAUNCH_V1_EVIDENCE_STATUS.md`](MSOS_PUBLIC_DEMO_LAUNCH_V1_EVIDENCE_STATUS.md)

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
| P8 | `msos_p8_tester_release` | **done** | — |

See [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) for propagation state.

### Post-demo multi-asset (chartered — blocked)

Crypto expansion (Deribit ETH) and equity options (single-ticker v1) are **chartered** in [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json). **Blocked** until `msos_usable_demo_v1` COMPLETE (crypto) and validation signal (equity). See [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) post-demo table.

### Non-goals (MSOS track)

- Rewriting PPE math in frontend code
- Live execution / order routing (deferred per master)
- Starting P2+ without [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) satisfied
