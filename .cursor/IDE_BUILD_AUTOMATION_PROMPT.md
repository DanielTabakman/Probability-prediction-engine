# PPE IDE BUILD automation prompt

Use this as the **Agent prompt** in a Cursor Automation triggered by changes to `artifacts/orchestrator/IDE_BUILD_NOW.md`.

---

Read `artifacts/orchestrator/IDE_BUILD_NOW.md` first.

1. Open the starter file referenced in that doc (`artifacts/orchestrator/IDE_BUILD_STARTER_*.md`) — load **only** that starter plus files it explicitly allows.
2. Implement the product slice within `ALLOWED_PATHS` / `TOUCH_SET`.
3. Follow the starter **## When done (required)** section exactly:
   - `python scripts/run_pushable_gate.py`
   - `git commit` on plan `buildBranch`
   - `mark_ide_product_ready.cmd <sliceId> <phasePlan>`
   - `run_ppe_local.cmd`

Execute autonomously. Do not ask for confirmation. Do not paste orchestrator logs.

If `run_ppe_local.cmd` fails, fix and retry once; then stop with a short failure summary.
