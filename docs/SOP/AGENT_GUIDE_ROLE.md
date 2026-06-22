# Agent guide role (static)

Purpose: instructions for a **read-only guide AI** that helps steer the build agent. The guide does not implement product code or edit steering docs unless explicitly running `apply_control_closeout_v1`.

## Load order

1. [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) — **direction SSOT** (pivot, primary focus, active BUILD chapter)
2. [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) — **generated**; gaps and current chapter
3. [`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md) — layer boundaries; match BUILD packet `LAYER_PRESET`
4. [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) — cross-chapter summary
5. [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) or [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) — only if brief reports `steering_aligned: true` for that track
6. [`VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — product canon when scope questions arise
7. [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) — wedge proof, priorities, drift guards before widening scope
8. [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) — trader-facing UI copy when reviewing or steering `msos-shell` / Strategy Lab / Command Center
9. [`MSOS_COPY_AGENT_V1.md`](MSOS_COPY_AGENT_V1.md) — copy agent workflow; operator says *"let's work on copy"* to enter COPY MODE (layers 0–3 in `docs/PRODUCT_COPY/`)
10. [`PRODUCT_DIRECTION_PIVOT_V1.md`](PRODUCT_DIRECTION_PIVOT_V1.md) — how agents pivot direction (operator does not memorize this)
11. [`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md) — monthly/quarterly steward cadence (on demand)
12. [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md) — Google Doc roles (MSOS write / Master read-only for Cursor)

## Do not use as controlling

- `docs/SOP/CURRENT_FRONTIER.md`, `docs/CURRENT_FRONTIER.md`
- `docs/Frontier_Steward_Handoff.md`
- Chat memory when it conflicts with pushed docs

## When `gaps` is non-empty

- Output a numbered checklist for the **build agent** (file paths + fix).
- Do **not** authorize a new BUILD until gaps are cleared or steward records an exception.

## When `gaps` is empty

- Next action comes from **Next SELECTION** doc in the brief (steward queue).
- BUILD agent runs slices on the **VM loop host** via `run_ppe.cmd` / `run_phase.cmd` / `run_slice.cmd`. On the **daily desktop**, product BUILD only — relay continue via `DESKTOP_CONTINUE.cmd` ([`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md)).

## Cursor context (guide agent)

- **Guide role:** SELECTION, gaps checklist, and “what’s next” only — not long implementation in this thread.
- Do **not** accumulate full-phase BUILD, PR fixes, and planning in one Cursor chat; see [`CONTEXT_RULES.md`](../CONTEXT_RULES.md).
- Point the build path to relay/orchestrator; BUILD packets use [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md).

## Relay closeout (automatic)

After slice `CONTINUE`, [`scripts/post_relay_continue.py`](../../scripts/post_relay_continue.py) runs [`apply_control_closeout_v1`](../../scripts/relay_runtime_v0.py), then **`sync_active_product_direction`** (steering markers), then best-effort [`sync_msos_repo_truth_v1`](../../scripts/sync_msos_repo_truth.py) (MSOS Google Doc only). No manual HANDOFF edits required.

**Google Docs:** never write PPE Master via MCP; MSOS is updated by `sync_msos_repo_truth_v1` only. See [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md).

Spec: [`RELAY_RUNTIME_V1.md`](RELAY_RUNTIME_V1.md), [`JOB_REGISTRY_V1.md`](JOB_REGISTRY_V1.md) §§3.5–3.6.
