# Options Horizon charter v1 — SELECTION

**Chapter:** `horizon_charter_v1`  
**Display name:** Options Horizon (chart-first region thesis workspace)  
**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**Milestone:** [`MILESTONE_OPTIONS_HORIZON_V1.md`](MILESTONE_OPTIONS_HORIZON_V1.md)

---

## Status

**SELECTED** 2026-06-26 — charter and vision contracts; no product BUILD until gating satisfied.

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Operator intent | Chart-first tool: price + volume + options-implied forward + region box → expression preview |
| Distinct from PPE | Separate MSOS workspace; PPE remains distribution/disagreement lab |
| Historical options | Archive-first daily snapshots; replay after ~30 days |
| Execution | Explicitly out of scope for v1 |
| Priority | LOW / P2 — after tradeable universe infra |

**Blocked until:** `ppe_tradeable_universe_v1` **COMPLETE** for first BUILD slice (`horizon_surface_archive_v1`).

---

## Acceptance (charter chapter)

1. [`MILESTONE_OPTIONS_HORIZON_V1.md`](MILESTONE_OPTIONS_HORIZON_V1.md) committed.
2. [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md) committed.
3. Vision contracts under `docs/VISION/OPTIONS_HORIZON/`.
4. Backlog rows for `horizon_charter_v1` + `horizon_surface_archive_v1` (blocked).
5. Product hierarchy updated in [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md).
6. Side channel in [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json).

---

## Non-goals

- MSOS route or chart UI in charter slice
- Live trading or broker integration
- Historical options third-party backfill
