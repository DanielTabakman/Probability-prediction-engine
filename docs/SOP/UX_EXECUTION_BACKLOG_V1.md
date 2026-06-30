# UX execution backlog v1

**Purpose:** Prioritized UX/workflow BUILD list derived from platform direction review (2026-06-30). Operators and `@ppe-ux-director` use this as the dispatch queue.

**Canon:** [`MSOS_UX_DESIGN_PHILOSOPHY_V1.md`](MSOS_UX_DESIGN_PHILOSOPHY_V1.md) · [`TRADER_LEARNING_SPINE_PROGRAM_V1.md`](TRADER_LEARNING_SPINE_PROGRAM_V1.md) · [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json)

**Coordinator agent:** `@ppe-ux-director` (`.cursor/agents/ppe-ux-director.md`)

**As-of:** 2026-06-30 (steward sync)

**Next UX BUILD candidate:** #3 `msos_trader_workflow_horizon_nav_v1` — **READY** in `PHASE_QUEUE.json` (promoted 2026-06-30).

---

## Acceptance bar (all items)

Every shipped slice must pass the philosophy bar:

1. User identifies **which tool** and **hero object** within ~15s.
2. **One meaningful action** in ~10s with visible feedback on the hero object.
3. Plain-English **what changed** read updates after interaction.
4. **Trust/provenance** findable when prompted.
5. **Restraint states** (empty/degraded/watch-only) feel intentional.

Run `@ux_legibility_reviewer` checklist at closeout when user-visible copy/layout changes.

---

## Execution queue

| # | Priority | Item | Chapter / program | Relay plan | Queue status | Worker | UX outcome |
|---|----------|------|-------------------|------------|--------------|--------|------------|
| 3 | **P1** | Cross-module deep links | `msos_trader_workflow_horizon_nav_v1` | [`msos_trader_workflow_horizon_nav_v1_relay.json`](PHASE_PLANS/msos_trader_workflow_horizon_nav_v1_relay.json) | **READY** | `@ppe-build-worker` after spine closeout | Exposure → Lab, Horizon region → Lab as obvious next actions |
| 4 | **P2** | Forward consistency radar (engine) | `ppe_forward_consistency_radar_v1` | [`ppe_forward_consistency_radar_v1_relay.json`](PHASE_PLANS/ppe_forward_consistency_radar_v1_relay.json) | PLANNED | `@ppe-build-worker` | Trust/edge payload for consistency module |
| 5 | **P2** | Forward consistency MSOS surface | `msos_forward_consistency_radar_v1` | [`msos_forward_consistency_radar_v1_relay.json`](PHASE_PLANS/msos_forward_consistency_radar_v1_relay.json) | PLANNED | `@ppe-build-worker` | `/forward-consistency` radar heatmap |
| 6 | **P2** | Cross-venue Strategy Lab card | `msos_cross_venue_strategy_lab_v1` | [`msos_cross_venue_strategy_lab_v1_relay.json`](PHASE_PLANS/msos_cross_venue_strategy_lab_v1_relay.json) | PLANNED | `@ppe-build-worker` | Read-only gap/backtest credibility card (not signals) |
| 7 | **P2** | Distribution timeseries collector | `mvp1_distribution_timeseries_collector_v1` | [`mvp1_distribution_timeseries_collector_v1_relay.json`](PHASE_PLANS/mvp1_distribution_timeseries_collector_v1_relay.json) | PLANNED | `@ppe-build-worker` (VM ops slice) | Archive feeds future replay charts |

---

## Completed (reference — do not re-queue)

| Item | Chapter | Closed |
|------|---------|--------|
| MSOS post-mortem review loop | `msos_trader_review_loop_v1` | Product on `main` (#590, #792); relay witness/closeout in flight — **do not re-BUILD** |
| Strategy Lab distribution CSV download | `msos_strategy_lab_dist_download_v1` | Product on `main` (#582); relay closeout in flight — **do not re-BUILD** |
| Exposure menu v0 | `ppe_exposure_menu_v1` | 2026-06-29 |
| Options Horizon chart polish | `horizon_chart_polish_v1` | 2026-06-28 (#429) |
| Options Horizon region workflow | `horizon_region_workflow_v1` | COMPLETE |
| Phase 2 desirability on main | `mvp1_phase2_on_main` | 2026-05-19 |
| MSOS P2–P8 storyboard routes | various | 2026-06-12 |
| Belief-input UX, onboarding, disagreement strip | MVP1 sprints | 2026-05–06 |

---

## P3 — deferred (needs charter before BUILD)

| Item | Why deferred | Next step |
|------|--------------|-------------|
| Implied distribution T4 — richer relationship modes | Beyond disagreement-only grammar | Steward SELECTION + registry tier bump |
| Horizon replay scrubber | Blocked on ≥30d archive | Wait for `archive_meta.replay_ready` |
| MSOS-native Strategy Lab shell (migrate off embed) | Architecture slice; MCD-gated | Separate enabling charter |
| Workflow persistence v1 (server-side thesis) | Blocked on MCD phase 3 | [`SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md`](SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md) |
| Public homepage zero-login first action | Partial vs storyboard | MSOS website program follow-up |
| Sensory punctuation (motion on insight moments) | Polish pass across modules | After P0–P2 spine closes |
| Session continuity (“market moved since…”) | Requires workflow tier T4 | After review loop + persistence |

---

## Dispatch rules (`@ppe-ux-director`)

1. Read `artifacts/orchestrator/OPERATOR_STATUS.md` — **relay queue wins** over this backlog when they conflict.
2. Execute **top-down** by priority; skip rows marked COMPLETE.
3. **RUN_LOCAL** → spawn `@ppe-finish-worker` (desktop: `DESKTOP_CONTINUE.cmd`).
4. **IDE_BUILD** → spawn `@ppe-build-worker` with starter from `artifacts/orchestrator/IDE_BUILD_NOW.md`.
5. **PLANNED** rows → do not BUILD until steward promotes to **READY** in `PHASE_QUEUE.json`.
6. After each worker: update insight-collect rows in [`MSOS_UX_DESIGN_PHILOSOPHY_V1.md`](MSOS_UX_DESIGN_PHILOSOPHY_V1.md) at module closeout.
7. Stop after `BURST_PLAN.max_cycles` workers; hand off with `docs/SOP/AGENT_CONTINUITY_BRIEF.md`.

---

## Module insight-collect targets (post-ship)

| Module | Route | Backlog item |
|--------|-------|--------------|
| Monitor + History | `/monitor`, `/history` | #1 review loop |
| Implied distribution | `/strategy-lab` | #2 CSV download, #6 cross-venue card |
| Options Horizon | `/options-horizon` | #3 deep links |
| Forward consistency | `/forward-consistency` | #4–5 radar |
| Exposure menu | `/exposure` | #3 deep links |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-30 | v1 — prioritized queue from UX direction review; `@ppe-ux-director` coordinator |
| 2026-06-30 | Steward sync — #1–#2 product on main; #3 next BUILD candidate; removed duplicate BUILD rows |
