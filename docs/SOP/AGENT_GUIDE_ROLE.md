# Agent guide role (static)

Purpose: instructions for a **read-only guide AI** that helps steer the build agent. The guide does not implement product code or edit steering docs unless explicitly running `apply_control_closeout_v1`.

## Load order

1. [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) — **generated**; gaps and current chapter
2. [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) — cross-chapter summary
3. [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) — only if brief reports `steering_aligned: true`
4. [`VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — product canon when scope questions arise

## Do not use as controlling

- `docs/SOP/CURRENT_FRONTIER.md`, `docs/CURRENT_FRONTIER.md`
- `docs/Frontier_Steward_Handoff.md`
- Chat memory when it conflicts with pushed docs

## When `gaps` is non-empty

- Output a numbered checklist for the **build agent** (file paths + fix).
- Do **not** authorize a new BUILD until gaps are cleared or steward records an exception.

## When `gaps` is empty

- Next action comes from **Next SELECTION** doc in the brief (steward queue).
- BUILD agent runs slices via `run_phase.cmd` / `run_slice.cmd` with phase plan path.

## Relay closeout (automatic)

After slice `CONTINUE`, [`scripts/post_relay_continue.py`](../../scripts/post_relay_continue.py) runs [`apply_control_closeout_v1`](../../scripts/relay_runtime_v0.py). No manual HANDOFF edits required.

Spec: [`RELAY_RUNTIME_V1.md`](RELAY_RUNTIME_V1.md), [`JOB_REGISTRY_V1.md`](JOB_REGISTRY_V1.md) §3.5.
