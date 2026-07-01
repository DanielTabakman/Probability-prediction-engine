# PPE IDE-native operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run relay chapters without Cursor API / ACP when credits are exhausted.

**Verdict → command (SSOT):** [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md) · human buttons: [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) · agent routing: [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md)

**Checklist:** [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)

**Operator layout (canonical):** [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md) · [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md)

**Desktop IDE BUILD setup:** [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md) · [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)

---

## Quick start — two machines

**Founder surface:** [`FOUNDER_OPERATOR_SURFACE_V1.md`](FOUNDER_OPERATOR_SURFACE_V1.md) — **runtime automation is SSOT**. Founder does **not** open Cursor threads or run relay for factory on a normal day.

| Machine | Normal day (automation) | Degraded only |
|---------|------------------------|---------------|
| **Hyper-V VM** (24/7) | Nothing — headless stack runs loop + watch + ntfy | `VM_RESTART.cmd` if stack down (agent or ntfy `restart`) |
| **Real daily PC** | Nothing — `autoRemoteBuild` + postBuildWatcher dispatch BUILD and continue | See [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) § degraded |

### Default factory path (zero founder steps)

1. VM headless stack: loop + mobile watch + `watch_ide_build_local` ([`PPE_HEADLESS_STACK_V1.md`](PPE_HEADLESS_STACK_V1.md)).
2. On `IDE_BUILD`: loop/watch calls headless Codex CLI (`autoRemoteBuild: true`, [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json)).
3. Post-build watcher: mark ready → `run_ppe_local` → relay continues.
4. Founder: optional ntfy read only — **no** Cursor, **no** paste, **no** `what's next?`

Config reference: [`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md) · autobuilder: [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md)

### Degraded — when automation fails (not daily process)

| Symptom | Agent / override path |
|---------|-------------------------|
| Headless BUILD blocked | `ppe_autobuilder.cmd advance` or ntfy `build` |
| CLI quota / DEGRADED | IDE handoff — agent opens Cursor, not founder ritual |
| Last resort | `DESKTOP BUILD` → agent thread with starter → `DESKTOP CONTINUE` after merge |

**Do not** document degraded steps as the founder's normal job. Agents try autobuilder + ntfy + burst before any handoff.

Monitor (optional): `.\scripts\watch_ppe_live.ps1`

---

## What the loop does (background)

Startup preflight writes `artifacts/orchestrator/OPERATOR_STATUS.md`. Control/witness/closeout slices run unattended; **product** slices stop until IDE BUILD completes. After closeout, the next blocked MSOS row with `planPath` promotes to **queued** automatically.

### Director agents (behind `ppe_go.cmd`)

| Agent | Role |
|-------|------|
| `@ppe-director` | Read `OPERATOR_STATUS.md`; spawn workers; never run `run_ppe_auto_local_loop` |
| `@ppe-build-worker` | One product slice from `IDE_BUILD_STARTER_*.md` → gate → commit → mark ready → `run_ppe_local` |
| `@ppe-finish-worker` | `RUN_LOCAL` / `CLOSEOUT_ONLY` — VM: `run_ppe_local.cmd`; desktop: `DESKTOP_CONTINUE.cmd` |
| `@ppe-triage-worker` | `FIX_PLAN` / `STALE_STATE` / `ERROR` diagnosis |

Definitions: [`.cursor/agents/`](../.cursor/agents/). Handoff script: [`scripts/ppe_director_go.py`](../../scripts/ppe_director_go.py).

**Manual fallback (agent / degraded — not founder daily):**

```text
what's next?
```

Used when automation is blocked and an **agent** opens Cursor to execute burst. Founder does not run this as routine process.

Emergency clipboard paste (`ppe_go_clipboard.cmd`) — agent recovery only.

**After chapter closeout:** runtime + `post_relay_continue` update continuity brief; **no** founder thread ritual required.

**Optional Automation (zero-click happy path):** Cursor Automation on `.cursor/IDE_BUILD_TRIGGER.json` — prompt in [`.cursor/IDE_BUILD_AUTOMATION_PROMPT.md`](../.cursor/IDE_BUILD_AUTOMATION_PROMPT.md). Use Automation for `IDE_BUILD`; use `ppe_go.cmd` for exceptions.

**Autobuilder (pipeline SRE):** [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) · `ppe_autobuilder.cmd` · `@ppe-autobuilder-operator` — status, diagnose, and `advance` without product BUILD.

---

## Two profiles

Use **one profile at a time**.

| When | Entry (continuous) | Config |
|------|-------------------|--------|
| **No API credits** | `run_ppe_auto_local_loop.cmd` | [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) |
| **Have API credits** | `run_ppe_auto_acp_loop.cmd` | [`PPE_AUTO_OPERATOR.acp.json`](PPE_AUTO_OPERATOR.acp.json) |

Plain `run_ppe_auto.cmd` uses [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) (defaults to **local**).

Set profile explicitly: `set PPE_OPERATOR_PROFILE=local` or `=acp`.

---

## Distribution snapshot collector (MVP)

Headless daily CSV capture (same schema as implied-lab download):

```bat
python scripts/collect_distribution_stats_snapshot.py
```

Writes under `artifacts/distribution_snapshots/YYYY-MM-DD/`. Schedule via Task Scheduler or cron on a machine with Deribit network access; not run by the relay loop.

---

## Cross-venue quant workflow

Daily + weekly pipeline: [`CROSS_VENUE_COLLECTOR_OPS_V1.md`](CROSS_VENUE_COLLECTOR_OPS_V1.md)

```bat
run_cross_venue_daily.cmd
REM or step-by-step:
python scripts/collect_cross_venue_snapshot.py
python scripts/run_cross_venue_scan.py
python scripts/run_cross_venue_backtest.py
```

VM: `install_cross_venue_collector_task.cmd` (daily 07:15). Weekly backtest via `weekly_digest_monday.cmd`.

See [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md).

---

## IDE BUILD closeout (product slices)

After implementing a product slice, run the full closeout — **do not stop at “code looks done”**:

```bat
ppe_ide_build_closeout.cmd <sliceId> <phasePlanPath>
```

That script runs gate → reminds you to commit on `buildBranch` → `mark_ide_product_ready.cmd` → `run_ppe_local.cmd` with **git sync disabled** on `build/auto/*` branches (avoids checkout to `main` mid-closeout).

Manual equivalent:

```bat
mark_ide_product_ready.cmd MVP1-CrossVenue-Product-Slice003 docs/SOP/PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json
set PPE_GIT_SYNC_PULL=0
set PPE_GIT_SYNC_PUSH=0
run_ppe_local.cmd
```

---

## IDE product-ready marker

After IDE BUILD and commit, write `artifacts/orchestrator/IDE_PRODUCT_READY.json` so continuous guards allow the phase to run:

```bat
mark_ide_product_ready.cmd MVP1-Phase6Trust-Product-Slice002
mark_ide_product_ready.cmd MVP1-Phase6Trust-Product-Slice002 docs/SOP/PHASE_PLANS/my_relay.json
```

Requires commits on the plan `buildBranch` ahead of baseline. Cleared automatically when `run_ppe_local.cmd` exits 0.

### Pushable gate (mixed-plane branches)

On `build/auto/*` with multiple planes in branch history, scope the gate to the slice commit:

```bat
python scripts/run_pushable_gate.py --base-ref HEAD~1 --no-auto-upstream
```

Docs-only closeout: stage only `docs/SOP/*`, then `--base-ref HEAD --no-auto-upstream`.

### Evidence doc stub (closeout hardening)

Relay chapters with a closeout block get a **PENDING** evidence stub automatically when `ppe_auto_select.py --apply` selects the plan. Closeout flips it to COMPLETE. Do not delete the stub before closeout.

### Control/smoke `STOP_FOR_REVIEW` in worktrees

Control and smoke slices often exit `STOP_FOR_REVIEW` / `UNCLEAR_TEST_RESULTS` in isolated worktrees — **normal, not a manual review**. `ppe_promotion_recovery` advances the phase automatically; `LAST_RUN_REPORT` buckets these as `auto_advance_promotion_recovery` with `awaiting_user: false`. **Only product slices** block on `IDE_PRODUCT_READY` (operator verdict `IDE_BUILD`).

| Relay signal | You needed? |
|--------------|-------------|
| Exit 20 + evidence/control/smoke slice | **No** — loop continues |
| Exit 20 + product `SCOPE_AMBIGUITY` | **Yes** — IDE BUILD + marker |
| Guard exit **7** / `PRODUCT_BLOCKED` | **Yes** — `ppe_go.cmd` |

---

## What runs unattended

| Step | Local profile |
|------|----------------|
| Backlog → queue propagation | Yes |
| Steward charter when idle | **No** (no API) |
| Control / smoke / closeout slices | Yes (pytest/scripts) |
| Product slices | **No** — guard stop until marker + `run_ppe_local` |

---

## Jump-in matrix

| Signal | Founder | Automation / agent |
|--------|---------|-------------------|
| Guard exit **7** / `PRODUCT_BLOCKED` | **Nothing** (default) | `autoRemoteBuild` → Codex CLI; else autobuilder `advance` / ntfy `build` |
| Relay exit **20** on control/smoke/witness | **Nothing** | Auto-advance |
| `IDE_BUILD` with stack healthy | **Nothing** | Headless BUILD + postBuildWatcher |
| `CONTEXT_ESCALATE` / `TOO_MANY_SLICES` | **Nothing** | Agent fixes plan/spec |
| Headless DEGRADED / CLI blocked | **Nothing** unless agent escalates | Agent IDE handoff or `@ppe-director` |
| Queue idle, no `READY` | **Decision** if SELECTION needed | Agent queues after founder direction |
| Test/smoke fail | **Nothing** | Agent fixes; `run_ppe_local` via loop |
| Chapter closeout complete | **Nothing** | Loop + closeout jobs continue |

---

## Parallel IDE work (Multitask)

Cursor **Multitask** does **not** replace `run_ppe_local.cmd` or the product-ready marker. It does not run the relay control plane.

Suggested pattern:

- **Terminal:** `run_ppe_auto_local_loop.cmd` (queue, guards, evidence slices).
- **Multitask / extra Agent threads:** product BUILD, doc review, or a second slice — one BUILD thread per product slice.
- Do not merge SELECTION + BUILD + closeout + `gh` in one mega-thread ([`CONTEXT_RULES.md`](../CONTEXT_RULES.md)).

---

## Related

- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
- [`PPE_WORKER_MODES_V1.md`](PPE_WORKER_MODES_V1.md)
- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
- [`.cursor/agents/`](../.cursor/agents/) — `ppe-director`, `ppe-build-worker`, `ppe-finish-worker`, `ppe-triage-worker`
