# RELAY_RUNTIME_V1

Purpose: extend [`RELAY_RUNTIME_V0.md`](RELAY_RUNTIME_V0.md) with **mandatory, deterministic CONTROL-CLOSEOUT** via job `apply_control_closeout_v1`. v0 behavior is unchanged unless this doc is invoked.

Status: **v1 — local-only.** Same machine constraints as v0 (no LLM in runtime, no remote dispatch).

Precedence: same stack as v0, with this doc after `RELAY_RUNTIME_V0.md` for closeout-specific rules.

## 1. What v1 adds

- **Fifth job:** `apply_control_closeout_v1` (see [`JOB_REGISTRY_V1.md`](JOB_REGISTRY_V1.md) §3.5).
- **Allow-listed writes** under `docs/SOP/` only, driven by phase-plan `closeout` metadata — no LLM prose generation.
- **Mandatory chaining:** after slice run `CONTINUE` with `ready_for_control_closeout == true`, wrappers **must** run closeout (via [`scripts/post_relay_continue.py`](../../scripts/post_relay_continue.py)) before the next slice in a phase plan.
- **Outputs:** patched steering docs + [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) + `artifacts/control_plane/continuity_brief.json` (gitignored).
- **Sixth job (best-effort):** `sync_msos_repo_truth_v1` (§3.6) — **PPE / MSOS Repo Truth — Live Mirror** Google Doc only; chained by [`post_relay_continue.py`](../../scripts/post_relay_continue.py) after successful closeout. Skip (missing OAuth/markers/deps) does **not** fail closeout; marker missing with credentials → non-zero for operator visibility.

## 2. Relationship to v0

| Topic | v0 | v1 |
|-------|----|----|
| `run_selected_slice_v1` | unchanged | unchanged |
| Writes to `docs/SOP/**` | forbidden | allowed **only** via `apply_control_closeout_v1` |
| On `CONTINUE` | hand back to steward | hand back **and** run closeout job (automation) |
| SELECTION | steward-only | steward-only |

## 3. Stop conditions (closeout job)

- Missing `closeout` block on closeout slice in phase plan → `BLOCKED`.
- `steering_alignment` hard checks fail after patch → `BLOCKED`.
- `control_plane_consistency_check` errors → `BLOCKED`.
- Allow-list violation (write outside listed paths) → internal error / `BLOCKED`.

## 4. Steward-only (unchanged)

- SELECTION and new chartering.
- Disposition of `STOP_FOR_REVIEW` / `BLOCKED` on slice runs.
- Promotion when baseline is checked out elsewhere (procedural STOP_FOR_REVIEW).

## 5. Last updated

2026-05-25 — Document `sync_msos_repo_truth_v1` post-closeout chaining (PPE / MSOS live mirror Google Doc).

2026-05-20 — Initial v1 closeout automation spec (companion to `apply_control_closeout_v1` implementation).
