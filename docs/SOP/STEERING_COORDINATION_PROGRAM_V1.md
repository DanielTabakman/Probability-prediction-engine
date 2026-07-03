# Steering coordination program v1

**Purpose:** Eliminate relay vs steering drift — factory executes the right chapter while human-facing docs stay derived, honest, and non-alarming.

**Status:** **DRAFT — ready to charter** (high priority)  
**Trigger incident:** [`OPERATOR_ALIGNMENT_NOTES_20260701.md`](OPERATOR_ALIGNMENT_NOTES_20260701.md) — horizon-nav COMPLETE while steering still named it "next BUILD candidate"; relay correctly on visual parity closeout.  
**Plane:** CONTROL-PLANE · **Audience:** stewards, operator agents, charter threads  
**SELECTION (activate):** [`POST_STEERING_COORDINATION_V1_SELECTION.md`](POST_STEERING_COORDINATION_V1_SELECTION.md)

---

## Agent load bundle

| Role | Path |
|------|------|
| Program (this doc) | `docs/SOP/STEERING_COORDINATION_PROGRAM_V1.md` |
| Factory coordination | [`CHAPTER_COORDINATION_V1.md`](CHAPTER_COORDINATION_V1.md) |
| Pipeline / milestone codes | [`PIPELINE_HEALTH_V1.md`](PIPELINE_HEALTH_V1.md) |
| Direction pivot ritual | [`PRODUCT_DIRECTION_PIVOT_V1.md`](PRODUCT_DIRECTION_PIVOT_V1.md) |
| Milestone gate CLI | `python scripts/ppe_milestone_gate.py --json` |
| Reconcile (safe repair) | `python scripts/ppe_milestone_gate.py --reconcile --apply` |
| Resolve topic | `python scripts/resolve_sop.py --topic "steering coordination" --json` |

---

## Problem (one paragraph)

The relay spine (`PHASE_QUEUE.json` → `ACTIVE_PHASE_MANIFEST.json` → markers → evidence) is machine-driven. Human steering (`AGENT_STEERING_V1.json` → propagated frontier / operator status / UX backlog) was steward-hand-set and copied widely. When those diverge, **layer audits pass** (they guard deadlocks, not narrative freshness) while operators read wrong "next BUILD" lines and misleading `MILESTONE_BLOCKED` alarms. Cost: wasted IDE threads, long operator sessions, charter/operator arguments about which queue wins.

---

## Design principles (non-negotiable)

1. **One writer, many readers** — Stewards decide *intent* (SELECTION, queue promote). Machines project *state* (steering fields, operator headlines, propagated markers).
2. **Relay wins execution** — Active manifest chapter is always "now." Steering `nextBuildCandidateId` is "after active gate clears" unless steward retargets queue via SELECTION.
3. **Never hand-edit propagated blocks** — Edit `ACTIVE_PRODUCT_DIRECTION.json` / `AGENT_STEERING_V1.json`, then `sync_product_direction.cmd`.
4. **Drift is repairable by default** — Safe auto-fix (advance stale candidate, prune registry) before human steward pass.
5. **Divergence is normal, not an error** — Active relay ≠ next UX BUILD is expected during closeout; operator UI must say so explicitly.

---

## Decision table (relay vs steering)

| Situation | Winner | Agent action |
|-----------|--------|--------------|
| Manifest active ≠ steering `nextBuildCandidateId` | **Manifest** | Execute relay; do not re-BUILD steering chapter out of order |
| `nextBuildCandidateId` points at COMPLETE chapter | **Milestone gate** | `ppe_milestone_gate.py --reconcile --apply` |
| UX backlog says READY, queue says DONE | **Queue** | Steward updates backlog row; optional gate warn `UX_BACKLOG_QUEUE_MISMATCH` |
| Steward promotes chapter not READY in queue | **Steward** | SELECTION + `PHASE_QUEUE.json` promote, then reconcile |
| READY queue blocked by dependency | **Queue order** | Document in SELECTION; do not override silently |
| `spineQueueAfterCloseout` entry already DONE | **Milestone gate** | Auto-prune from steering (Phase 1) |

Canon anchor: [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md) § Relay spine vs steering.

---

## Current state (Phase 0 — shipped baseline)

| Capability | Status | Gap |
|------------|--------|-----|
| `ppe_milestone_gate.py` | **Shipped** | `docHints.load_*` not refreshed from `resolve_sop` on advance |
| `STEERING_CANDIDATE_STALE` | **Shipped** | Not wired on all closeout paths |
| `post_relay_continue` reconcile hook | **Shipped** | Queue health repair / evidence auto-DONE paths omit hook |
| Registry prune (`CLOSEOUT_REGISTRY_DEBT`) | **Shipped** | Conservative; stale-complete rows linger |
| `MILESTONE_BLOCKED` semantics | **Fixed v2** | Tied to active chapter gate, not stale candidate name |
| Operator ACTIVE vs NEXT headline | **Not shipped** | Single blended paragraph in `OPERATOR_STATUS` |
| UX backlog queue column sync | **Manual** | Drifts from `PHASE_QUEUE.json` |
| `relay_decision_reconcile` steward item | **Open** | Absorbed into this program Phase 3 |

---

## Phased delivery

### Phase 1 — Stop the bleeding (P0)

**Goal:** Steering cannot point at COMPLETE chapters for more than one reconcile tick; operator reads unambiguous "now vs later."

| # | Deliverable | Acceptance |
|---|-------------|------------|
| 1.1 | **Reconcile on all lifecycle hooks** | `reconcile_milestone_gate(apply=True)` runs from: `post_relay_continue`, `ppe_queue_health` mark-DONE repair, `apply_control_closeout` tail, `sync_active_product_direction` when steering touched |
| 1.2 | **Full `docHints` refresh on advance** | When `nextBuildCandidateId` changes, `docHints.nextBuildCandidate` `load_always` / `load_for_build` / `load_on_demand` / `program_doc` populated via `resolve_sop.py --chapter <id> --json` |
| 1.3 | **Spine queue auto-prune** | `spineQueueAfterCloseout` drops ids where `is_chapter_fully_closed`; covered by unit test |
| 1.4 | **Operator status: ACTIVE vs NEXT** | `OPERATOR_STATUS.md` blocks: `**Active relay:**` (manifest) and `**Next UX BUILD:**` (resolved candidate) |
| 1.5 | **Post-reconcile sync** | After `--reconcile --apply`, call `sync_active_product_direction.py` so frontier / integrated markers update in same commit |

**Relay slice (suggested):** `PPE-SteerCoord-Phase1-Control-Slice001` — CONTROL plane.

**Exit criteria:** Stale candidate in test fixture → one reconcile → candidate advanced, docHints match, operator status shows split headlines; gate green.

---

### Phase 2 — Detect earlier (P1)

**Goal:** Drift surfaces in gate / coordination before a human opens a stale operator thread.

| # | Deliverable | Acceptance |
|---|-------------|------------|
| 2.1 | **`STEERING_HINTS_DRIFT`** | Issue when `docHints.nextBuildCandidate.chapter_id` ≠ `nextBuildCandidateId`; gate **warn** (non-blocking) |
| 2.2 | **`SPINE_QUEUE_STALE`** | Issue when `spineQueueAfterCloseout` contains DONE chapter; auto-repair in `--reconcile --apply` |
| 2.3 | **`UX_BACKLOG_QUEUE_MISMATCH`** | Compare `UX_EXECUTION_BACKLOG_V1.md` table vs `PHASE_QUEUE.json`; gate warn |
| 2.4 | **`ACTIVE_VS_STEERING_DIVERGE` (info)** | Log when manifest chapter ≠ resolved next BUILD; not `MILESTONE_BLOCKED` |
| 2.5 | **Coordination doc codes** | [`CHAPTER_COORDINATION_V1.md`](CHAPTER_COORDINATION_V1.md) § Issue codes updated |

**Exit criteria:** Gate warns on fixture with hints drift; `ppe_chapter_coordination.py --json` includes new codes.

---

### Phase 3 — Less to maintain (P2)

**Goal:** Fewer hand-edited parallel surfaces; chapter lifecycle owns projections.

| # | Deliverable | Acceptance |
|---|-------------|------------|
| 3.1 | **`relay_decision_reconcile` closed** | Steward backlog item marked done; decision table in this doc is SSOT |
| 3.2 | **UX backlog single-write** | Queue status derived at sync time or from `resolve_sop --chapter` only |
| 3.3 | **Chapter lifecycle hook module** | `scripts/ppe_chapter_lifecycle.py` — `on_chapter_closed(plan_path)` consolidates hooks |
| 3.4 | **Retire alignment note pattern** | `OPERATOR_ALIGNMENT_NOTES_*` superseded by machine codes |
| 3.5 | **Thread role pin (process)** | Operator vs charter habit in [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) |

**Exit criteria:** Closeout slice only calls `on_chapter_closed`; no duplicate reconcile calls across scripts.

---

## Out of scope

- Merging UX priority queue and relay `PHASE_QUEUE` into one ordered list
- Hard-blocking relay/burst on informational steering drift while factory is moving
- Product feature work (MSOS routes, PPE math, etc.)
- VM/desktop mirror hygiene (separate ops track)

---

## Success metrics

| Metric | Baseline (2026-07) | Target (Phase 1) | Target (Phase 3) |
|--------|-------------------|------------------|------------------|
| Stale `nextBuildCandidateId` after COMPLETE | Days | ≤ 1 relay tick | 0 (auto) |
| `docHints` mismatch after advance | Common | 0 | 0 |
| Operator thread same verdict | 1109m observed | Rotate after closeout | < 4h median |
| Registry stale-complete rows | ~15 | Prune on reconcile | Only actionable debt |

---

## Charter activation checklist

When founder charters **high priority**:

1. [ ] Mark **SELECTED** in [`POST_STEERING_COORDINATION_V1_SELECTION.md`](POST_STEERING_COORDINATION_V1_SELECTION.md)
2. [ ] Set this doc **Status:** `ACTIVE`
3. [ ] Add `PPE-SteerCoord-Phase1-Control-Slice001` to [`PHASE_QUEUE.json`](PHASE_QUEUE.json) (`READY`) + phase plan relay JSON
4. [ ] Set [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) item `steering_coordination_program_v1` → `in_progress`
5. [ ] Operator thread: IDE BUILD for Phase 1.1–1.5
6. [ ] Close `relay_decision_reconcile` when Phase 3.1 ships

---

## Related

- [`OPERATOR_ALIGNMENT_NOTES_20260701.md`](OPERATOR_ALIGNMENT_NOTES_20260701.md) — incident record
- [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md) — autobuilder guards
- Subsumes steward backlog: `relay_decision_reconcile` (Phase 3)
