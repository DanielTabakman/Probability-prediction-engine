# BUILD packet — MVP1 Phase 6 trust metrics v1

Hand this file (paths only) to a **fresh BUILD** thread or `run_ppe.cmd` after SELECTION.

```text
EXECUTION STEP: BUILD
PLANE: PRODUCT-PLANE
SLICE_ID: MVP1-Phase6Trust-Product-Slice002
PHASE_PLAN: docs/SOP/PHASE_PLANS/mvp1_phase6_trust_metrics_v1_relay.json
SPRINT_SPEC: docs/SOP/SPRINT_MVP1_PHASE6_TRUST_METRICS_V1.md
SELECTION: docs/SOP/POST_PHASE5_PHASE6_TRUST_METRICS_SELECTION_OUTCOME.md
CONTINUITY_BRIEF: docs/SOP/AGENT_CONTINUITY_BRIEF.md
BASELINE_BRANCH: main
BUILD_BRANCH: build/auto/MVP1-Phase6Trust-Product-Slice002-phase6_trust
```

## Product slice intent (one screen)

Add **`by_data_quality`** and **`by_primary_output_state`** to Phase 6 class rollups. Read enums from frozen record top-level fields (`data_quality`, `primary_output_state`); legacy rows without enums use sprint fallback (`unknown` / `degraded` rules in sprint spec).

**Primary files:** `src/viz/reviewed_class_summary.py`, `src/viz/app.py` (Phase 6 expander only), `tests/test_reviewed_class_summary.py`.

## AGENT CONTINUITY (return)

```text
AGENT CONTINUITY
- Safe to switch agents? YES after Product-Slice002 merges and Smoke-Slice003 passes
- Exact reason: bounded touch set; no verification math changes
- If YES: relay_result.json path + pytest count + PR URL
```

## Operator

From repo root after charter is on `main`:

```bat
run_ppe.cmd
```

Or steward-only SELECTION:

```bat
python scripts/ppe_auto_select.py --repo-root . --apply
run_ppe.cmd
```
