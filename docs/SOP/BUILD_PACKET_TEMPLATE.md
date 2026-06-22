# BUILD packet template (SLIM steward → worker)

Use this template when sending a relay BUILD packet to Cursor or documenting a slice handoff. **Paths only** — do not inline sprint specs, HANDOFF gate blocks, or ledger history.

**Layer map (required for all BUILD packets):** [`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md) · presets [`REPO_LAYER_PATH_PREFIXES.json`](REPO_LAYER_PATH_PREFIXES.json)

## Required fields

```text
EXECUTION STEP: BUILD
PLANE: <CONTROL-PLANE | PRODUCT-PLANE | EVIDENCE-PLANE>
LAYER: <msos-shell | ppe-ui | ppe-core | dev-factory | platform | product-canon>
LAYER_PRESET: <MSOS_UI | PPE_UI | PPE_CORE | CONTROL | PLATFORM | DOCS_CANON | DOCS_ONLY | MSOS_PROXY>
ALLOWED_PATHS:
  - <prefix/from/preset/or/sprint>
FORBIDDEN_PATHS:
  - <prefix/from/preset/or/sprint>
SLICE_ID: <sliceId from phase plan>
PHASE_PLAN: docs/SOP/PHASE_PLANS/<plan>.json
SPRINT_SPEC: docs/SOP/SPRINT_<chapter>.md
CONTINUITY_BRIEF: docs/SOP/AGENT_CONTINUITY_BRIEF.md
BASELINE_BRANCH: main
BUILD_BRANCH: build/auto/<sliceId>-<timestamp>  (orchestrator assigns)
```

`LAYER` must match the preset’s `layer` in `REPO_LAYER_PATH_PREFIXES.json`. Copy `ALLOWED_PATHS` / `FORBIDDEN_PATHS` from the preset unless the sprint narrows them further. **Do not widen** forbidden paths without steward exception in the sprint or SELECTION doc.

### Preset quick reference

| LAYER_PRESET | LAYER | Typical PLANE |
|--------------|-------|---------------|
| `MSOS_UI` | `msos-shell` | `PRODUCT-PLANE` |
| `PPE_UI` | `ppe-ui` | `PRODUCT-PLANE` |
| `PPE_CORE` | `ppe-core` | `PRODUCT-PLANE` |
| `CONTROL` | `dev-factory` | `CONTROL-PLANE` or `EVIDENCE-PLANE` |
| `PLATFORM` | `platform` | `EVIDENCE-PLANE` |
| `DOCS_CANON` | `product-canon` | `CONTROL-PLANE` |
| `DOCS_ONLY` | (docs only) | `CONTROL-PLANE` |
| `MSOS_PROXY` | `msos-shell` | `PRODUCT-PLANE` (P4; steward only) |

## AGENT CONTINUITY (required in return)

```text
AGENT CONTINUITY
- Safe to switch agents? YES/NO
- Exact reason:
- If YES: exact handoff payload required:
```

## Focus playbook (scope-expanding slices)

When the slice adds product surface, assets, or commercial claims, cite [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md):

```markdown
## Focus playbook
- Priority tier: P0 / P1 / P2 (from playbook priority stack)
- Drift guards checked: yes / N/A — <exception note if steward approved>
```

## Public copy (`MSOS_UI` / `msos-shell`)

Any slice that changes visitor-visible strings must follow [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md) (trader voice, banned jargon, degraded messages). Prefer `apps/msos-web/src/lib/publicCopy.ts` for shared footers and error sanitization.

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

- [`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md) — folder ownership, import rules, parallel development
- [`OPERATING_RULES.md`](OPERATING_RULES.md) — SLIM MODE default
- [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) — advisory context bands
- [`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md) — Cursor context discipline
- [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) — strategic focus and anti-drift
