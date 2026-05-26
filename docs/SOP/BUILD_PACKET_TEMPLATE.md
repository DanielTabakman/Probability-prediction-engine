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
CLOSEOUT: auto-commit per COMMIT_POLICY_V1 when python scripts/run_pushable_gate.py passes
LAYER: <L0 | L1 | L2 | L3 | L4>   # see VIZ_LAYER_DISCIPLINE_V1.md
PRIMARY_MODULE: <repo-relative path>
TOUCH_SET: <comma-separated path prefixes; all changed files must match>
FORBIDDEN_TOUCH: <prefixes that must not change; default src/viz/app.py unless L0 shell/extract slice>
```

**PRODUCT slices:** `TOUCH_SET` / `FORBIDDEN_TOUCH` must match the phase plan JSON (`touchSet` / `forbiddenTouch`). `run_slice.cmd` writes `artifacts/control_plane/active_slice_touch_set.json` automatically when a phase plan is set.

Example (L2 panel slice — parallel-safe):

```text
LAYER: L2
PRIMARY_MODULE: src/viz/app_panels.py
TOUCH_SET: src/viz/implied_lab_provenance.py, src/viz/app_panels.py, tests/test_trust_strip.py
FORBIDDEN_TOUCH: src/viz/app.py, src/viz/app_bitcoin_implied_lab.py
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

## Cycle boundaries

- **Before phase run (SELECTION):** steward runs `run_ppe.cmd` → automatic **cycle-start** refresh; optional explicit `refresh_google_docs.cmd`.
- **After chapter closeout slice:** automatic **cycle-end** refresh (Live Mirror + `artifacts/control_plane/google_docs_refresh_report.md`).
- Human command: **refresh Google Docs** — see [`GOOGLE_DOCS_REFRESH_V1.md`](GOOGLE_DOCS_REFRESH_V1.md).

## References

- [`COMMIT_POLICY_V1.md`](COMMIT_POLICY_V1.md) — tiered pushable gate
- [`AGENT_GIT_SETUP.md`](AGENT_GIT_SETUP.md) — Cursor user-rules + auto-commit setup
- [`OPERATING_RULES.md`](OPERATING_RULES.md) — SLIM MODE default
- [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) — advisory context bands
- [`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md) — Cursor context discipline
- [`VIZ_LAYER_DISCIPLINE_V1.md`](VIZ_LAYER_DISCIPLINE_V1.md) — thin shell, touch sets, parallel BUILD
- [`GOOGLE_DOCS_REFRESH_V1.md`](GOOGLE_DOCS_REFRESH_V1.md) — control-plane doc refresh at cycle start/end
