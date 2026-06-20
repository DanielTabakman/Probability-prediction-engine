# PPE IDE BUILD automation prompt

Use this as the **Agent prompt** in a Cursor Automation triggered by changes to `.cursor/IDE_BUILD_TRIGGER.json`.

---

Read `.cursor/IDE_BUILD_TRIGGER.json` first.

## Preflight (scope — do not widen)

Before implementing, confirm the slice advances **one of**:

1. Minimum Credible Demo ([`docs/SOP/MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](docs/SOP/MINIMUM_CREDIBLE_DEMO_GATE_V1.md))
2. Seamless PPE-in-MSOS integration
3. Workflow-research ingestion
4. Grounded build-factory reliability

If the starter or trigger would **widen scope beyond** these (broad platform, execution, new assets, commercial plumbing, ungrounded control-plane) → implement **only** the chartered slice; note deferred expansions in commit message; do not add unrequested surface area.

---

1. If `status` is not `"pending"`, exit immediately with a one-line no-op (do not build).
2. Open the `starter` path from the trigger (e.g. `artifacts/orchestrator/IDE_BUILD_STARTER_*.md`) — load **only** that starter plus files it explicitly allows.
3. Implement the product slice within `ALLOWED_PATHS` / `TOUCH_SET`.
4. Follow the starter **## When done (required)** section exactly:
   - `git commit` on plan `buildBranch` (if not already committed)
   - `ppe_ide_build_closeout.cmd <sliceId> <phasePlan>` (preferred — gate + mark ready + run_ppe_local)

Manual equivalent: gate → `mark_ide_product_ready.cmd` → `run_ppe_local.cmd` with `PPE_GIT_SYNC_PULL=0` on `build/auto/*` branches.

Execute autonomously. Do not ask for confirmation. Do not paste orchestrator logs.

If `run_ppe_local.cmd` fails, fix and retry once; then stop with a short failure summary.

Human-readable handoff (optional): `artifacts/orchestrator/IDE_BUILD_NOW.md`.
