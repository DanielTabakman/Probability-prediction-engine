---
name: ppe-finish-worker
description: Finishes a PPE chapter when IDE product marker is present. Desktop uses DESKTOP_CONTINUE only; VM uses run_ppe_local.cmd. Use when OPERATOR_STATUS verdict is RUN_LOCAL.
---

You finish one chapter after IDE BUILD already committed.

## Steps

1. Confirm `artifacts/orchestrator/IDE_PRODUCT_READY.json` exists (or status says IDE_MARKER_OK).
2. **Desktop** (`ppe_operator_no_loop.local.cmd` present or guard `"allowed": false`): run `DESKTOP_CONTINUE.cmd --no-pause` only. **VM loop host** (`PPE_LOOP_HOST=1` and guard `"allowed": true`): run `run_ppe_local.cmd`.
3. Read `artifacts/orchestrator/LAST_RUN_REPORT.md` — summary section only.
4. Read `artifacts/orchestrator/OPERATOR_STATUS.md`.

If the mapped command fails, fix and retry once; then stop with a short failure summary. Do not substitute desktop `run_ppe_local.cmd` for a failed desktop bridge.

## Return

- mapped finish command and exit code
- relay decision if present in LAST_RUN_REPORT
- new verdict
- whether terminal loop can continue unattended
