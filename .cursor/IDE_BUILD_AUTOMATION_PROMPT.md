# PPE IDE BUILD automation prompt

Use this as the **Agent prompt** in a Cursor Automation triggered by changes to `.cursor/IDE_BUILD_TRIGGER.json`.

---

Read `.cursor/IDE_BUILD_TRIGGER.json` first.

1. If `status` is not `"pending"`, exit immediately with a one-line no-op (do not build).
2. Open the `starter` path from the trigger (e.g. `artifacts/orchestrator/IDE_BUILD_STARTER_*.md`) — load **only** that starter plus files it explicitly allows.
3. Implement the product slice within `ALLOWED_PATHS` / `TOUCH_SET`.
4. Follow the starter **## When done (required)** section exactly:
   - `python scripts/run_pushable_gate.py`
   - `git commit` on plan `buildBranch`
   - `mark_ide_product_ready.cmd <sliceId> <phasePlan>`
   - `run_ppe_local.cmd`

Execute autonomously. Do not ask for confirmation. Do not paste orchestrator logs.

If `run_ppe_local.cmd` fails, fix and retry once; then stop with a short failure summary.

Human-readable handoff (optional): `artifacts/orchestrator/IDE_BUILD_NOW.md`.

Pipeline health (optional): `artifacts/orchestrator/AUTOBUILDER_STATUS.json` — use `@ppe-autobuilder-operator` for stuck/closeout issues, not product rewrites.
