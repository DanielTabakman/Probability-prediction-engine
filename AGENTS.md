# Agents — Probability Prediction Engine

Repo-native index for Cursor / Codex workers. **Do not widen scope** beyond starter `ALLOWED_PATHS`.

## Operator agents (`.cursor/agents/`)

| Agent | Role |
|-------|------|
| `@ppe-autobuilder-operator` | Pipeline SRE — `ppe_autobuilder.cmd`, no product code |
| `@ppe-director` | Verdict router from `OPERATOR_STATUS.md` |
| `@ppe-build-worker` | One IDE product slice from `IDE_BUILD_STARTER_*.md` |
| `@ppe-finish-worker` | `RUN_LOCAL` only |
| `@ppe-triage-worker` | `FIX_PLAN` / `ERROR` diagnosis |

## Layer map

- [`docs/SOP/REPO_LAYER_MAP_V1.md`](docs/SOP/REPO_LAYER_MAP_V1.md)
- Presets: [`docs/SOP/REPO_LAYER_PATH_PREFIXES.json`](docs/SOP/REPO_LAYER_PATH_PREFIXES.json)

## BUILD starters

- `artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md` (generated)
- Template: [`docs/SOP/BUILD_PACKET_TEMPLATE.md`](docs/SOP/BUILD_PACKET_TEMPLATE.md)

## Forbidden without steward exception

- `src/engine/`, `src/models/`, `src/data/` from MSOS UI slices
- `apps/msos-web/` math reimplementation of PPE
- Hand-editing `MVP1_FRONTIER.md` / `HANDOFF.md` during BUILD (closeout job only)

## Control plane entrypoints

- `ppe_autobuilder.cmd` — status / advance / diagnose
- `run_ppe.cmd` — relay phase
- [`docs/SOP/PPE_AUTOBUILDER_V1.md`](docs/SOP/PPE_AUTOBUILDER_V1.md)

## Gate repair

On gate failure: `artifacts/orchestrator/BUILD_REPAIR_HINT.md` — fix and re-run `ppe_ide_build_closeout.cmd`.
