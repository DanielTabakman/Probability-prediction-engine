# BUILD packet template (SLIM steward → worker)

Use this template when sending a relay BUILD packet to Cursor or documenting a slice handoff. **Paths only** — do not inline sprint specs, HANDOFF gate blocks, or ledger history.

## Required fields

```text
EXECUTION STEP: BUILD
PLANE: <CONTROL-PLANE | PRODUCT-PLANE | EVIDENCE-PLANE>
SLICE_ID: <sliceId from phase plan>
PHASE_PLAN: docs/SOP/PHASE_PLANS/<plan>.json
SPRINT_SPEC: docs/SOP/SPRINT_<chapter>.md
CONTINUITY_BRIEF: docs/SOP/AGENT_CONTINUITY_BRIEF.md
BASELINE_BRANCH: main
BUILD_BRANCH: build/auto/<sliceId>-<timestamp>  (orchestrator assigns)
```

## AGENT CONTINUITY (required in return)

```text
AGENT CONTINUITY
- Safe to switch agents? YES/NO
- Exact reason:
- If YES: exact handoff payload required:
```

## Forbidden in packets

- Full `HANDOFF.md` gate block pasted inline
- Historical steward ledger from prior Cursor windows
- Full `git diff`, full pytest log, or orchestrator stdout (use artifact paths under `artifacts/`)
- Inline copies of `RELAY_RUNTIME_V0.md` or other protocol anchors

## Cursor context

- **Relay BUILD** runs in a fresh ACP worker per slice (`run_slice.cmd` / `run_phase.cmd`); that is separate from this Cursor thread.
- Prefer a **dedicated BUILD Cursor thread** per slice or sub-sprint; steward SELECTION/planning stays in a **different** thread.
- After chapter CLOSEOUT: open a **new** Cursor thread; load only `AGENT_CONTINUITY_BRIEF.md` (+ linked SELECTION doc if needed). See [`CONTEXT_RULES.md`](../CONTEXT_RULES.md).

## References

- [`OPERATING_RULES.md`](OPERATING_RULES.md) — SLIM MODE default
- [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) — advisory context bands
- [`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md) — Cursor context discipline
