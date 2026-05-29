# PPE continuous auto-operator

Hands-off chapter runner: drain **`PHASE_QUEUE`**, pull **`queued`** rows from **`PHASE_CHAPTER_BACKLOG.json`**, and optionally **charter** new evidence chapters when idle.

## Two processes (credits vs no credits)

Use **one profile at a time** — do not run local and ACP auto-loops together.

| When | Entry (single chapter) | Entry (continuous) | Config |
|------|------------------------|--------------------|--------|
| **No agent credits** | `run_ppe_local.cmd` | `run_ppe_auto_local_loop.cmd` | [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) |
| **Have agent credits** | `run_ppe_acp.cmd` | `run_ppe_auto_acp_loop.cmd` | [`PPE_AUTO_OPERATOR.acp.json`](PPE_AUTO_OPERATOR.acp.json) |

Set `PPE_OPERATOR_PROFILE=local` or `=acp` (wrappers above do this). Default [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) matches **local**.

### No credits (local)

- **Relay:** deterministic (`PPE_SKIP_ACP=1`) — control, smoke, closeout slices only.
- **Product slices:** continuous run **stops** on PRODUCT (guard) — run [`run_product_slice.cmd`](../../run_product_slice.cmd) once (agent-cli), or BUILD in Cursor IDE, then `run_ppe_local.cmd` for smoke/closeout. See [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md).
- **No** npm steward / ACP / Cursor SDK charter.

### Have credits (acp)

- **Relay:** `ppe-orchestrator-acp` npm steward + ACP workers per slice.
- **Steward charter** when queue idle (`stewardCharter: true`).
- Requires `CURSOR_API_KEY` and sibling `ppe-orchestrator-acp` repo.

## Quick start (repo root)

**Default (local / no credits):**

```bat
run_ppe_auto_local.cmd
run_ppe_auto_local_loop.cmd
```

**With credits:**

```bat
set CURSOR_API_KEY=your_key
run_ppe_auto_acp.cmd
run_ppe_auto_acp_loop.cmd
```

Legacy names (`run_ppe_auto.cmd`) use whatever is in `PPE_AUTO_OPERATOR.json` (local by default).

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
| `stewardCharter` | `true` | When idle and backlog empty, Cursor SDK steward charters next chapter — **only if `skipAcp` is false** (ACP profile); ignored on local profile |
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

**Product chapters under local profile:** continuous stops on PRODUCT (guard). Build product code in Cursor IDE, then re-run `run_ppe_local.cmd` for remaining slices. Under **acp** profile, product slices use ACP / plan `workerMode`.

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

- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
- [`PPE_AUTO_SELECTION_ROADMAP_V1.md`](PPE_AUTO_SELECTION_ROADMAP_V1.md)
- [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)
- [`PPE_STEWARD_CURSOR_V1.md`](PPE_STEWARD_CURSOR_V1.md)
- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
