# PPE worker modes v0

**Purpose:** run relay chapters continuously without Cursor ACP when quota blocks `ppe-orchestrator-acp`.

## Modes

| Mode | Env / plan | Worker |
|------|------------|--------|
| **acp** (default) | `PPE_WORKER_MODE=acp` | `ppe-orchestrator-acp` npm `run-slice` |
| **deterministic** | `PPE_WORKER_MODE=deterministic` or `PPE_SKIP_ACP=1` | `scripts/ppe_slice_worker.py` (pytest, dual smoke, relay payload) |
| **local-agent** | `PPE_WORKER_MODE=local-agent` | `phase_orchestrator_v0.py` + `agent` CLI |

Per-slice override in phase plan JSON:

```json
"workerMode": "deterministic"
```

Auto-deterministic (no env) for slice IDs containing **Control**, **Smoke**, **Witness**, or **Closeout** when `PPE_AUTO_DETERMINISTIC` is not `0`.

## Continuous run (no ACP)

From repo root:

```bat
set PPE_WORKER_MODE=deterministic
set PPE_SKIP_ACP=1
run_ppe.cmd --continuous
```

Or:

```bat
run_ppe.cmd --continuous
```

with only `PPE_SKIP_ACP=1` (`run_ppe.cmd` sets `PPE_WORKER_MODE=deterministic` automatically).

Uses `scripts/ppe_relay_phase.py` instead of npm steward. Each slice: deterministic worker → relay resume → `post_relay_continue` → `ppe_promotion_recovery` on exit 20/40.

## PRODUCT slices

Deterministic mode **does not** implement product code changes. **Product** slices get `STOP_FOR_REVIEW` with a note to use ACP or steward BUILD in Cursor, then **promotion recovery** can still merge if you committed on the build branch manually.

## Related

- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
- [`scripts/ppe_promotion_recovery.py`](../../scripts/ppe_promotion_recovery.py)
- [`scripts/ppe_queue_health.py`](../../scripts/ppe_queue_health.py)
