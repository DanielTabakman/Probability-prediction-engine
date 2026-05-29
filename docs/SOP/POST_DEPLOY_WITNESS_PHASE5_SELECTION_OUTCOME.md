# Post–deploy witness — Phase 5 review persistence SELECTION outcome

**Status:** **SELECTION COMPLETE** 2026-05-28  
**Prior chapter:** MVP1 deploy witness refresh **COMPLETE**

## Selected next BUILD chapter

| Field | Value |
|-------|--------|
| **Chapter** | MVP1 Phase 5 review UX / persistence hardening |
| **Canon** | [`MVP1_PHASE1_3_SPRINT.md`](MVP1_PHASE1_3_SPRINT.md) — `MVP1-Phase5-Slice002` |
| **Phase plan** | [`PHASE_PLANS/mvp1_phase5_review_hardening_relay.json`](PHASE_PLANS/mvp1_phase5_review_hardening_relay.json) |
| **Sprint** | [`SPRINT_MVP1_PHASE5_REVIEW_HARDENING.md`](SPRINT_MVP1_PHASE5_REVIEW_HARDENING.md) |

## Scope (v0 charter)

- Enable SQLite **`PRAGMA foreign_keys=ON`** on frozen evaluation DB connections.
- Optional **`FOREIGN KEY(snapshot_id)`** on `snapshot_reviews` with sane migration for existing DBs.
- Targeted pytest on `tests/test_frozen_review_store.py` / `tests/test_frozen_evaluation_store.py`.

## Deferred (next queue)

| Candidate | Source |
|-----------|--------|
| ~~Phase 6 trust metrics v1~~ | **Chartered** — [`POST_PHASE5_PHASE6_TRUST_METRICS_SELECTION_OUTCOME.md`](POST_PHASE5_PHASE6_TRUST_METRICS_SELECTION_OUTCOME.md) |
| Steward VPS CTA | Commercial ops (not agent BUILD) |

## Relay

`workerMode` on **Product** slice: `local-agent` (Cursor `agent` CLI). Control/Smoke/Closeout: deterministic.
