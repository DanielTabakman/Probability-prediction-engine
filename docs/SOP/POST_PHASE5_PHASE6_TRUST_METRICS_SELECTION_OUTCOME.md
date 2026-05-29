# Post–Phase 5 — Phase 6 trust metrics v1 SELECTION outcome

**Status:** **SELECTION COMPLETE** 2026-05-29  
**Prior chapter:** MVP1 Phase 5 review persistence hardening **COMPLETE** ([`MVP1_PHASE5_REVIEW_HARDENING_EVIDENCE_STATUS.md`](MVP1_PHASE5_REVIEW_HARDENING_EVIDENCE_STATUS.md))

## Selected next BUILD chapter

| Field | Value |
|-------|--------|
| **Chapter** | MVP1 Phase 6 trust metrics v1 (class rollup) |
| **Canon** | [`MVP1_PHASE1_3_SPRINT.md`](MVP1_PHASE1_3_SPRINT.md) — Phase 6 v0 landed; this slice = **beyond v0** trust enums in rollups |
| **Phase plan** | [`PHASE_PLANS/mvp1_phase6_trust_metrics_v1_relay.json`](PHASE_PLANS/mvp1_phase6_trust_metrics_v1_relay.json) |
| **Sprint** | [`SPRINT_MVP1_PHASE6_TRUST_METRICS_V1.md`](SPRINT_MVP1_PHASE6_TRUST_METRICS_V1.md) |
| **BUILD packet** | [`BUILD_PACKETS/MVP1_PHASE6_TRUST_METRICS_V1.md`](BUILD_PACKETS/MVP1_PHASE6_TRUST_METRICS_V1.md) |

## Why this is unblocked now

Prior backlog note (“verification payload lacks explicit trust enums”) was **overstated for new freezes**:

- [`implied_lab_provenance.py`](../../src/viz/implied_lab_provenance.py) already writes `data_quality`, `classification_label`, and `primary_output_state` into `verification_summary` from [`mvp1_decision_surface.py`](../../src/viz/mvp1_decision_surface.py).
- [`frozen_evaluation_record.py`](../../src/viz/frozen_evaluation_record.py) persists top-level `data_quality` and `primary_output_state` on each frozen snapshot.

**Remaining gap (in scope):** Phase 6 v0 class rollup still counts **`by_trust_breeden`** (Breeden gate string) instead of MVP1 **`usable | degraded | invalid`** and **`candidate | watch_only | no_trade`**. This chapter closes that gap without changing execution/ticket semantics.

## Scope (v1 charter)

1. **Rollup dimensions:** add `by_data_quality` and `by_primary_output_state` to `build_class_summary` / CSV export.
2. **Dimension extraction:** prefer frozen record top-level fields; sane legacy fallback when absent (see sprint spec).
3. **UI:** Phase 6 expander shows trust enums alongside (or replacing) Breeden-only trust proxy labeling.
4. **Tests:** extend `tests/test_reviewed_class_summary.py`; full pytest green before closeout.

## Out of scope

- Execution engine, ticket ledger, automated deployment.
- New verification math or materiality rule changes.
- Re-freezing historical DB rows (legacy snapshots may bucket as `unknown`).

## Relay

| Slice | Plane | Worker |
|-------|-------|--------|
| Control-Slice001 | EVIDENCE | deterministic |
| Product-Slice002 | PRODUCT | `local-agent` (UI + rollup logic) |
| Smoke-Slice003 | EVIDENCE | deterministic |
| Closeout-Slice004 | EVIDENCE | deterministic |

## Deferred (after this chapter)

| Candidate | Source |
|-----------|--------|
| Phase 6 richer trust breakdowns (multi-field trust witness) | [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) — only if canon expands beyond enum rollups |
| Steward VPS CTA | Commercial ops |
