# PPE continuous auto-operator

Hands-off chapter runner: drain **`PHASE_QUEUE`**, pull **`queued`** rows from **`PHASE_CHAPTER_BACKLOG.json`**, and optionally **charter** new evidence chapters when idle.

## Quick start (repo root)

```bat
run_ppe_auto.cmd
```

**Keep running** (sleep and retry when the queue empties):

```bat
run_ppe_auto_loop.cmd
```

Monitor (optional second terminal):

```powershell
.\scripts\watch_ppe_live.ps1
```

## What is enabled

Controlled by [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json):

| Flag | Default | Effect |
|------|---------|--------|
| `enabled` | `true` | Master switch for `run_ppe_auto.cmd` |
| `propagateBacklog` | `true` | `queued` backlog → roadmap `pending` → queue `PLANNED` → bootstrap `READY` |
| `stewardCharter` | `true` | When idle and backlog empty, Cursor SDK steward adds next **deterministic** chapter |
| `workerMode` | `deterministic` | Relay worker mode |
| `skipAcp` | `true` | Sets `PPE_SKIP_ACP=1` (local deterministic relay; avoids cloud ACP quota) |
| `continuousMax` | `20` | Max chapters per `--continuous` pass |
| `loopWhenIdle` | `true` | Use `run_ppe_auto_loop.cmd` for outer retry |
| `idleSleepSeconds` | `120` | Sleep between loop passes |

### Operator guards (`guards` object)

When `enabled` is true and the operator is on, `--continuous` runs pre-flight checks before each chapter. A guard stop exits **7** and writes [`artifacts/orchestrator/OPERATOR_GUARD_REPORT.md`](../../artifacts/orchestrator/OPERATOR_GUARD_REPORT.md). `run_ppe_auto_loop.cmd` does **not** sleep and retry on exit 7.

| Guard | Default | Effect |
|-------|---------|--------|
| `stopOnContextEscalate` | `true` | Stop if any sprint spec in the plan is **>400 lines** (ESCALATE band) |
| `stopOnContextWatch` | `false` | Stop if sprint spec **>200 lines** (WATCH band) |
| `maxPhaseSlices` | `6` | Stop if the phase plan has too many slices |
| `blockProductUnderGlobalDeterministic` | `true` | Stop if a **PRODUCT** slice would run as deterministic (SCOPE_AMBIGUITY) |
| `requireTouchSetOnProductSlices` | `true` | PRODUCT slices must declare a non-empty `touchSet` |
| `skipChapterIfEvidenceComplete` | `true` | Skip relay when closeout evidence already says **COMPLETE** |
| `maxConsecutivePhaseFailures` | `2` | Stop after N failed chapters in one `--continuous` pass |
| `runQueueHealthBeforeChapter` | `true` | Auto-repair duplicate READY / stale READY rows |

**Product chapters under auto-operator:** set `workerMode: local-agent` on the product slice (Phase 6 plan does). Slice-level `local-agent` overrides global `PPE_WORKER_MODE=deterministic` so evidence slices stay local while product runs via agent CLI / Cursor BUILD.

Disable all guards: `"guards": { "enabled": false }` or `PPE_OPERATOR_GUARDS=0`.

Environment variables **override** the JSON file (`PPE_AUTO_STEWARD=0` disables steward even if JSON says on).

## Flow

```text
run_ppe_auto.cmd
  → ppe_operator_env.py (apply env from PPE_AUTO_OPERATOR.json)
  → run_ppe.cmd --continuous
       → each chapter: auto_select
            → prepare_selection_idle
                 → sync roadmap → queue
                 → propagate backlog (queued)
                 → steward charter (if still idle)
                 → bootstrap pending → READY
            → relay phase
            → closeout → DONE → advance roadmap
       → if no READY: idle hydrate (second prepare_selection_idle) then stop
```

## Steward requirements

When `stewardCharter` is true:

```bat
pip install cursor-sdk
set CURSOR_API_KEY=your_key
```

See [`PPE_STEWARD_CURSOR_V1.md`](PPE_STEWARD_CURSOR_V1.md). Steward only charters **evidence / deterministic** chapters unless `PPE_STEWARD_ALLOW_PRODUCT=1`.

## Adding work

1. **`queued` in backlog** — preferred (e.g. Phase 6 trust metrics after charter merge).
2. **`pending` on roadmap** — manual or steward output.
3. **`blocked` in backlog** — never auto-propagates; needs steward charter doc first.

## Disable

Set `"enabled": false` in `PPE_AUTO_OPERATOR.json`, or use plain `run_ppe.cmd` without auto env.

## Related

- [`PPE_AUTO_SELECTION_ROADMAP_V1.md`](PPE_AUTO_SELECTION_ROADMAP_V1.md)
- [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)
- [`PPE_STEWARD_CURSOR_V1.md`](PPE_STEWARD_CURSOR_V1.md)
- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
