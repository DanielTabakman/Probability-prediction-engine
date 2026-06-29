# Options Horizon replay scrubber v1 — SELECTION

**Chapter:** `horizon_replay_scrubber_v1`  
**Display name:** Options Horizon replay scrubber (timeline of past implied surfaces)  
**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**Milestone:** [`MILESTONE_OPTIONS_HORIZON_V1.md`](MILESTONE_OPTIONS_HORIZON_V1.md)  
**Archive contract:** [`SURFACE_ARCHIVE_CONTRACT_V1.md`](../VISION/OPTIONS_HORIZON/SURFACE_ARCHIVE_CONTRACT_V1.md)  
**Relay plan:** [`PHASE_PLANS/horizon_replay_scrubber_v1_relay.json`](PHASE_PLANS/horizon_replay_scrubber_v1_relay.json)  
**Sprint:** [`SPRINT_OPTIONS_HORIZON_REPLAY_SCRUBBER_V1.md`](SPRINT_OPTIONS_HORIZON_REPLAY_SCRUBBER_V1.md)

---

## Status

**CHARTERED** 2026-06-29 — first H5 overlay after region workflow; **LOW / P2** side channel.

**First slice:** `Horizon-ReplayScrub-Control-Slice001`

**Promote to `READY` when:** `archive_meta.replay_ready` is `true` (≥30 calendar days with surface snapshots). Until then queue stays `PLANNED`; daily collector on VM grows archive ([`HORIZON_SURFACE_COLLECTOR_OPS_V1.md`](HORIZON_SURFACE_COLLECTOR_OPS_V1.md)).

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Program sequence | Next chapter after `horizon_region_workflow_v1` **COMPLETE** (2026-06-29) |
| Archive gate | Replay needs history — archive-first strategy; no vendor backfill in v1 |
| Operator value | Scrub timeline of implied surfaces without re-fetching live Deribit on every frame |
| Priority | LOW — does not preempt trader-workflow milestone relay |

**Blocked until:** `archive_meta.replay_ready` (`available_days >= 30`) **and** region workflow COMPLETE (**satisfied** 2026-06-29).

---

## Acceptance (chapter)

1. `/options-horizon` exposes a replay scrubber (date or index slider) when archive has usable history.
2. Scrubber loads archived surface snapshots via existing horizon surface API — no TypeScript density math.
3. Chart updates implied overlay for selected archive date; spot/historical panes remain honest (simulation-only).
4. Scrubber hidden or disabled with clear copy when `replay_ready` is false.
5. Evidence doc COMPLETE.

---

## Non-goals

- Liquidation overlay (`horizon_liquidation_overlay_v1`)
- Outcome ghosts (`horizon_outcome_ghosts_v1`)
- Third-party historical options backfill
- Multi-asset Horizon replay
- Execution or broker copy

---

## Next (program)

Deferred H5b/H5c: `horizon_liquidation_overlay_v1` (vendor TBD), `horizon_outcome_ghosts_v1` (after replay scrubber).
