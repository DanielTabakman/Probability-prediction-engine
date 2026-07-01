# PPE canonical operator scripts v1

**Plane:** CONTROL-PLANE · **Audience:** operators, stewards, agents  
**Role:** **Single source of truth** for verdict → machine → command. Other docs link here instead of duplicating tables.

**Related:** [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) (human double-click lookup) · [`PPE_OPERATOR_PROCESS_V1.md`](PPE_OPERATOR_PROCESS_V1.md) · [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md) (policy)

## Why this doc exists

The repo has **80+** `ppe_*.py` scripts and **100+** `.cmd` wrappers. Most are helpers, witnesses, or one-shot utilities. **Five surfaces** drive day-to-day operation — when in doubt, start here.

If any helper, runbook, or agent rule disagrees with this doc, **trust this doc** after `python scripts/ppe_operator_status.py`.

---

## The five canonical surfaces

| # | Surface | Primary entry | What it answers |
|---|---------|---------------|-----------------|
| 1 | **Verdict / status** | `python scripts/ppe_operator_status.py` · `ppe_autobuilder.cmd status --brief` | What should run next? (`IDE_BUILD`, `RUN_LOCAL`, `RUN_AUTO`, …) |
| 2 | **Relay advance** | `run_ppe.cmd` (VM) · `ppe_autobuilder.cmd advance` | Execute the next relay slice or propagate queue |
| 3 | **Pushable gate** | `python scripts/run_pushable_gate.py` | Is this commit/PR safe to push? (tier 0/1/2) |
| 4 | **IDE BUILD handoff** | `DESKTOP_BUILD.cmd` | Stage Cursor/Codex worker when verdict is `IDE_BUILD` |
| 5 | **Relay runtime** | `python scripts/relay_runtime_v0.py` | Stage / resume / abort a single in-flight relay run (file-backed state machine) |

Everything else is **supporting** — deploy witnesses, ntfy helpers, digests, SSH bootstrap, etc.

---

## Verdict → machine → action (SSOT)

Guard before any relay on desktop: `python scripts/ppe_loop_host_guard.py --check` — if `"allowed": false`, do **not** run VM-only relay locally.

| Verdict | **Desktop** (`PPE_STACK_FORBIDDEN` or guard `allowed: false`) | **VM** (`PPE_LOOP_HOST=1`, guard `allowed: true`) |
|---------|----------------------------------------------------------------|-----------------------------------------------------|
| `IDE_BUILD` | `DESKTOP_BUILD.cmd` → implement slice → gate → commit → `mark_ide_product_ready` | Wait — ntfy operator for desktop BUILD |
| `RUN_LOCAL` | **`DESKTOP_CONTINUE.cmd`** only (after product PR merged to `main`) | `run_ppe_local.cmd` or `@ppe-finish-worker` |
| `RUN_AUTO` | SSH `ppe_autobuilder.cmd status --brief` — **do not** local `run_ppe.cmd` | `run_ppe.cmd` or loop advance |
| `SUPPLY_LOW` | Charter / merge to `main`; VM pulls on next pass | Idle until `main` has queued work |
| `ERROR` / `FIX_PLAN` / `STALE_STATE` | Triage; `@ppe-director` when burst allowed | `fix_vm_operator.cmd` or loop triage |

**Common mistake:** `RUN_LOCAL` on desktop **≠** `run_ppe_local.cmd`. On the daily PC it **always** means **`DESKTOP_CONTINUE.cmd`**.

Phone ntfy hints mirror this table via [`scripts/ppe_operator_hint.py`](../../scripts/ppe_operator_hint.py).

---

## Desktop handoff chain (implementation)

### `DESKTOP_BUILD.cmd` (start IDE BUILD)

1. Loads `ppe_operator_no_loop.local.cmd` (`PPE_STACK_FORBIDDEN=1`).
2. `python scripts/ppe_autobuilder.py handoff` — stages starter + `IDE_BUILD_NOW.md` (clipboard off by default).
3. `python scripts/ppe_build_worker.py print-handoff` — on-screen worker steps.

Related helpers: `scripts/ppe_ide_handoff.py`, `scripts/ppe_build_worker.py`.

### `DESKTOP_CONTINUE.cmd` (after PR merge)

1. `git pull origin main` on desktop.
2. SSH to VM → **`ppe_operator_git_sync.py --prepare-handoff`** (abort merges, reset runtime SOP drift, return to `main`) → **`call call_ppe_operator_local.cmd`** → **`finish_ide_build.cmd`**.
3. `finish_ide_build.cmd` runs `scripts/ppe_post_build_watcher.py --finish-handoff` (post-build mark when build branch has commits; **else explicit CLOSEOUT_ONLY `run_ppe_local` trigger** when product is already on `main`).
4. SSH status uses loop-host env: `call call_ppe_operator_local.cmd && ppe_autobuilder.cmd status --brief`.

Agent/non-interactive: `DESKTOP_CONTINUE.cmd --no-pause`.

**VM health check:** `check_vm_loop.cmd --no-pause` on the loop host (loads env + brief status).

**Forbidden on desktop:** `run_ppe_local.cmd`, `run_ppe.cmd`, `finish_ide_build.cmd`, `run_ppe_auto_local_loop.cmd`, `run_ppe_headless_stack.cmd`, `ppe_autobuilder.cmd advance`.

---

## Helper tiers (not canonical — use when needed)

| Tier | Examples | When |
|------|----------|------|
| **Queue / manifest** | `ppe_auto_select.py`, `ppe_manifest.py`, `ppe_propagate_queue.py` | Steward sets next chapter; recovery |
| **Notify / phone** | `ppe_notify_fix.py`, `ppe_ntfy_listen.py`, `ppe_operator_hint.py` | Mobile alerts; blocked-state triage |
| **Witness / deploy** | `verify_msos_web_ship.py`, `ensure_production_deploy.py` | Post-merge production checks |
| **Recovery** | `vm_bootstrap.cmd --recover`, `fix_vm_operator.cmd` | Stale relay, dirty trigger, stack down |
| **Multi-agent leases** | `ppe_worker_lease.py` | Cursor vs Codex lanes; [`WORKER_LANE_POLICY_V1.md`](WORKER_LANE_POLICY_V1.md) |
| **Closeout** | `post_relay_continue.py`, `apply_control_closeout_v1` (via relay) | Chapter COMPLETE propagation |

---

## Agent rule

1. Read `artifacts/orchestrator/OPERATOR_STATUS.md` (or run `ppe_operator_status.py`).
2. Check **`Mode:`** — `CLOSEOUT_ONLY` means product on main; **do NOT re-implement** product slices.
3. Map verdict → **one row** in the table above ([`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) for role load order).
4. Do not invent a new script path when a canonical surface already exists.
5. Add new automation as a **helper** unless steward promotes it in this doc.
6. **Run** mapped commands in-thread (or via `@ppe-director` workers) — do **not** reply with "What you should do" checklists or choice questions for the operator ([`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md) § Operator-facing replies).

Relay orchestration detail: [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md).

---

## Related tests

| Module | Test file |
|--------|-----------|
| `relay_runtime_v0.py` | `tests/test_relay_runtime_v0.py` |
| `run_pushable_gate.py` | `tests/test_run_pushable_gate.py` |
| `ppe_operator_status.py` | `tests/test_ppe_operator_status.py` (if present) |

See [`MODULE_TEST_COVERAGE_V1.md`](MODULE_TEST_COVERAGE_V1.md) for engine/product module coverage.
