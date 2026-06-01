# PPE continuous auto-operator

Hands-off chapter runner: drain **`PHASE_QUEUE`**, pull **`queued`** rows from **`PHASE_CHAPTER_BACKLOG.json`**, and optionally **charter** new evidence chapters when idle (ACP profile only).

## Two profiles (credits vs no credits)

Use **one profile at a time**.

| When | Entry (single chapter) | Entry (continuous) | Config |
|------|------------------------|--------------------|--------|
| **No agent credits** | `run_ppe_local.cmd` | `run_ppe_auto_local_loop.cmd` | [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) |
| **Have agent credits** | `run_ppe_acp.cmd` | `run_ppe_auto_acp_loop.cmd` | [`PPE_AUTO_OPERATOR.acp.json`](PPE_AUTO_OPERATOR.acp.json) |

Set `PPE_OPERATOR_PROFILE=local` or `=acp` (wrappers above do this). Default [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) matches **local**.

**IDE-native runbook:** [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md).

### No credits (local)

- **Relay:** deterministic (`PPE_SKIP_ACP=1`) — control, smoke, closeout slices only.
- **Product slices:** continuous run **stops** on PRODUCT (guard exit 7 or STOP_FOR_REVIEW) — IDE BUILD, then `run_ppe_local.cmd`.
- **No** steward SDK / ACP when idle.

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

Legacy names (`run_ppe_auto.cmd`, `run_ppe_auto_loop.cmd`) use [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) (local by default).

Monitor (optional second terminal):

```powershell
.\scripts\watch_ppe_live.ps1
```

## What is enabled

Controlled by operator JSON (profile or default):

| Flag | Local default | Effect |
|------|---------------|--------|
| `enabled` | `true` | Master switch for `run_ppe_auto.cmd` |
| `propagateBacklog` | `true` | `queued` backlog → roadmap → queue `READY` |
| `stewardCharter` | `false` (local) | Cursor SDK steward when idle — **acp only** |
| `workerMode` | `deterministic` (local) | Relay worker mode |
| `skipAcp` | `true` (local) | Sets `PPE_SKIP_ACP=1` |
| `continuousMax` | `20` | Max chapters per `--continuous` pass |
| `loopWhenIdle` | `true` | Use `*_loop.cmd` for outer retry |
| `idleSleepSeconds` | `120` | Sleep between loop passes |

Environment variables **override** JSON (`PPE_AUTO_STEWARD=0`, `PPE_OPERATOR_GUARDS=0`).

### Operator guards (`guards` object)

When enabled, `--continuous` may exit **7** and write [`artifacts/orchestrator/OPERATOR_GUARD_REPORT.md`](../../artifacts/orchestrator/OPERATOR_GUARD_REPORT.md). `run_ppe_auto_loop.cmd` does **not** sleep and retry on exit 7.

| Guard | Local default | Effect |
|-------|---------------|--------|
| `blockProductUnderGlobalDeterministic` | `true` | Stop before phase if product slice would run under `PPE_SKIP_ACP=1` |

## Flow

```text
run_ppe_auto_local_loop.cmd
  → PPE_OPERATOR_PROFILE=local
  → run_ppe_auto_loop.cmd
       → run_ppe_auto.cmd
            → ppe_operator_env.py
            → run_ppe.cmd --continuous
                 → guards (product block)
                 → relay phase → closeout → DONE
       → sleep idleSleepSeconds (if exit 0)
```

## Steward requirements (ACP profile only)

```bat
pip install cursor-sdk
set CURSOR_API_KEY=your_key
```

See [`PPE_STEWARD_CURSOR_V1.md`](PPE_STEWARD_CURSOR_V1.md).

## Adding work

1. **`queued` in backlog** — preferred.
2. **`pending` on roadmap** — manual or steward output (acp).
3. **`blocked` in backlog** — never auto-propagates.

## Disable

Set `"enabled": false` in operator JSON, or use plain `run_ppe.cmd` without auto env.

## Related

- [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md)
- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
- [`PPE_AUTO_SELECTION_ROADMAP_V1.md`](PPE_AUTO_SELECTION_ROADMAP_V1.md)
- [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)
- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
