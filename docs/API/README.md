# API / Distribution

This directory is the canonical documentation home for the MSOS/PPE API / Distribution lane.

Start with **[API_LANE_CHARTER_V1.md](API_LANE_CHARTER_V1.md)** for the lane mission and **[API_LANE_AUTONOMOUS_OPERATOR_V1.md](API_LANE_AUTONOMOUS_OPERATOR_V1.md)** for the self-driving execution loop used by the API Cursor/Codex lane.

## Cursor / agent entry point

For day-to-day autonomous lane work, load [API_LANE_AUTONOMOUS_OPERATOR_V1.md](API_LANE_AUTONOMOUS_OPERATOR_V1.md). It is authorized to reconcile stale state, finish the selected API product, and continue to the next eligible API product using the existing PPE control plane and factory.

## Source-of-truth rule

API work remains inside the existing PPE repository and control plane.

- **Product/API docs:** `docs/API/`
- **Execution charters and phase plans:** `docs/SOP/`
- **Live queue/state:** `docs/SOP/ACTIVE_PHASE_MANIFEST.json`, `PHASE_QUEUE.json`, `PHASE_CHAPTER_BACKLOG.json`
- **Implementation:** existing product/runtime modules selected by the active charter
- **Tests/conformance:** `tests/` and `scripts/`
- **Deploy:** `docs/DEPLOY/`

Do **not** create a second API queue or a separate API repository merely to organize the lane.

## Product slots

| Qatom slot | Product | Current disposition |
|---|---|---|
| 1 | Options Market Read | Existing; partner/Qatom acceptance is the first API-lane execution job |
| 2 | Best Exposure | Next product; API contract not yet frozen |
| 3 | Exposure Compare | WAIT — determine whether separate from Best Exposure |
| 4 | Reserved | No product assigned |
| 5 | Reserved | No product assigned |

See the charter for the rule governing when a slot may be consumed.

## Options Market Read

- [OPTIONS_MARKET_READ_V1.md](OPTIONS_MARKET_READ_V1.md) — public product/API contract
- [options-market-read.openapi.yaml](options-market-read.openapi.yaml) — OpenAPI
- [QATOM_OPTIONS_MARKET_READ_HANDOFF_V1.md](QATOM_OPTIONS_MARKET_READ_HANDOFF_V1.md) — Qatom/partner handoff
- [QATOM_OPTIONS_MARKET_READ_PARTNER_DECISIONS_V1.md](QATOM_OPTIONS_MARKET_READ_PARTNER_DECISIONS_V1.md) — founder-delegated integration controls for partner acceptance
- [OPTIONS_MARKET_READ_STAGING_PLAN_V1.md](OPTIONS_MARKET_READ_STAGING_PLAN_V1.md) — staging topology and promotion gate
- [OPTIONS_MARKET_READ_UPTIME_V1.md](OPTIONS_MARKET_READ_UPTIME_V1.md) — uptime/conformance agreement

Execution authority and current status for partner acceptance live under `docs/SOP/`, not here.

## Lane boundary

The API lane productizes approved MSOS/PPE products. It owns public contracts, adapters, validation, documentation, conformance, staging/production acceptance, external integration and monitoring. It does not independently change financial semantics or build a second product engine.

For cross-lane coordination and worktree isolation, see [THREE_TRACK_COORDINATION_HANDOFF_V1.md](../SOP/THREE_TRACK_COORDINATION_HANDOFF_V1.md).
