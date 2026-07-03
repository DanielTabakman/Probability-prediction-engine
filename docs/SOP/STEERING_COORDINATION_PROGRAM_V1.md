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
| 1.2 | **Full `docHints` refresh on advance** | When `nextBuildCandidateId` changes, `docHints.nextBuildCandidate` populated via `resolve_sop.py --chapter <id> --json` |
| 1.3 | **Spine queue auto-prune** | `spineQueueAfterCloseout` drops ids where `is_chapter_fully_closed`; unit test |
| 1.4 | **Operator status: ACTIVE vs NEXT** | `OPERATOR_STATUS.md`: `**Active relay:**` + `**Next UX BUILD:**` |
| 1.5 | **Post-reconcile sync** | After `--reconcile --apply`, call `sync_active_product_direction.py` |

**Relay slice:** `PPE-SteerCoord-Phase1-Control-Slice001` — CONTROL plane.

**Exit criteria:** Stale candidate fixture → one reconcile → advanced + docHints match + split headlines; gate green.

---

### Phase 2 — Detect earlier (P1)

| # | Deliverable | Acceptance |
|---|-------------|------------|
| 2.1 | **`STEERING_HINTS_DRIFT`** | `docHints.chapter_id` ≠ `nextBuildCandidateId`; gate warn |
| 2.2 | **`SPINE_QUEUE_STALE`** | DONE ids in spine queue; auto-repair on reconcile |
| 2.3 | **`UX_BACKLOG_QUEUE_MISMATCH`** | Backlog table vs `PHASE_QUEUE.json`; gate warn |
| 2.4 | **`ACTIVE_VS_STEERING_DIVERGE` (info)** | Manifest ≠ resolved next BUILD; not `MILESTONE_BLOCKED` |
| 2.5 | **Coordination doc codes** | Update [`CHAPTER_COORDINATION_V1.md`](CHAPTER_COORDINATION_V1.md) |

---

### Phase 3 — Less to maintain (P2)

| # | Deliverable | Acceptance |
|---|-------------|------------|
| 3.1 | Close **`relay_decision_reconcile`** | Decision table in this doc is SSOT |
| 3.2 | **UX backlog single-write** | Queue status derived at sync |
| 3.3 | **`ppe_chapter_lifecycle.py`** | `on_chapter_closed(plan_path)` consolidates hooks |
| 3.4 | Retire **`OPERATOR_ALIGNMENT_NOTES_*`** pattern | Machine codes instead |
| 3.5 | Thread role pin | [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) |

---

## Out of scope

- Merging UX and relay queues
- Hard-blocking factory on informational steering drift
- Product features; VM mirror hygiene (separate track)

---

## Success metrics

| Metric | Baseline | Phase 1 | Phase 3 |
|--------|----------|---------|---------|
| Stale candidate after COMPLETE | Days | ≤ 1 tick | 0 |
| docHints mismatch | Common | 0 | 0 |
| Operator thread stuck same verdict | 1109m | Rotate after closeout | < 4h |

---

## Charter activation checklist

1. [ ] **SELECTED** in [`POST_STEERING_COORDINATION_V1_SELECTION.md`](POST_STEERING_COORDINATION_V1_SELECTION.md)
2. [ ] This doc **Status:** `ACTIVE`
3. [ ] `PPE-SteerCoord-Phase1-Control-Slice001` in queue + phase plan
4. [ ] Backlog item `steering_coordination_program_v1` → `in_progress`
5. [ ] IDE BUILD Phase 1.1–1.5
6. [ ] Close `relay_decision_reconcile` at Phase 3.1

---

## Related

- [`OPERATOR_ALIGNMENT_NOTES_20260701.md`](OPERATOR_ALIGNMENT_NOTES_20260701.md)
- Subsumes `relay_decision_reconcile` (Phase 3)
