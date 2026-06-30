---
name: ppe-finish-worker
description: Finishes a PPE chapter when IDE product marker is present. Runs run_ppe_local.cmd only. Use when OPERATOR_STATUS verdict is RUN_LOCAL.
---

You finish one chapter after IDE BUILD already committed.

## Steps

1. Confirm `artifacts/orchestrator/IDE_PRODUCT_READY.json` exists (or status says IDE_MARKER_OK).
2. **Desktop** (`ppe_operator_no_loop.local.cmd` present): run `DESKTOP_CONTINUE.cmd`. **VM loop host:** run `run_ppe_local.cmd`.
3. Read `artifacts/orchestrator/LAST_RUN_REPORT.md` — summary section only.
4. Read `artifacts/orchestrator/OPERATOR_STATUS.md`.

If `run_ppe_local.cmd` fails, fix and retry once; then stop with a short failure summary.

## Reply to director

Return facts only — verdict before/after, commands run. **Do not** ask the operator to choose next steps or run relay commands manually.

## Return

- `run_ppe_local` exit code
- relay decision if present in LAST_RUN_REPORT
- new verdict
- whether terminal loop can continue unattended
