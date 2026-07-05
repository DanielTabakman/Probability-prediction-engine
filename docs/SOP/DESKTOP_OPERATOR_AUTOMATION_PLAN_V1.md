# Desktop operator automation plan v1

**Plane:** CONTROL-PLANE · **Audience:** founder, operator agents  
**Purpose:** phased automation so desktop factory steps run without manual `what's next?` for every handoff.

**Related:** [`DESKTOP_BUILD_EFFICIENCY_V1.md`](DESKTOP_BUILD_EFFICIENCY_V1.md) · [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) · [`FOUNDER_OPERATOR_SURFACE_V1.md`](FOUNDER_OPERATOR_SURFACE_V1.md) · [`MULTI_AGENT_ROADMAP_V1.md`](MULTI_AGENT_ROADMAP_V1.md)

---

## Problem

VM relay runs autonomously on the loop host. **Desktop** steps (`DESKTOP_CONTINUE`, branch recovery, status refresh, burst routing) today require an **Agent-mode operator thread** saying `what's next?` — even when `ppe_in_flight_monitor` already detected `action_ready`.

Signals are scattered:

| Source | Role |
|--------|------|
| `OPERATOR_STATUS.md` | Human + agent summary (can lag live SSH) |
| `VM_STATUS_CACHE.json` | Live SSH brief |
| `IN_FLIGHT_MONITOR_STATE.json` | Monitor `action_ready` / `watching` |
| `docs/SOP/VM_OPERATOR_PHASE.json` | Git mirror (stale up to ~30m is normal) |
| `BURST_PLAN.json` | `direct_action` routing |

---

## Design principles

1. **Opt-in on daily PC** — desktop automation stays off until explicitly enabled (popups/confusion).
2. **Script dispatch before Cursor chat** — run known `direct_action` values via subprocess; reserve `@ppe-director` for ambiguous verdicts.
3. **Status is SSOT for agents** — promote monitor transitions into `prepare_operator_status()` so one read is enough.
4. **Branch preflight gates relay** — never auto-continue on mixed-plane / wrong branch.
5. **Founder surface unchanged** — automation runs on agent surface; founder still only opens operator thread when alerts fire or they want visibility.

---

## Phased rollout

### Step 1 — `action_ready` in status + burst (shipped in this slice)

**Goal:** When monitor detects phase cleared, `OPERATOR_STATUS` and `BURST_PLAN` say `DESKTOP_CONTINUE` — not stale `wait_for_vm`.

| Change | File |
|--------|------|
| `enrich_operator_status_with_monitor()` | `scripts/ppe_operator_status.py` |
| `action_ready` → `direct_action` | `scripts/ppe_burst_plan.py` |
| Human status line | `scripts/ppe_operator_status.py` `_format_human()` |
| Tests | `tests/test_ppe_burst_plan.py`, `tests/test_ppe_operator_monitor_enrich.py` |

**Acceptance:** Refresh status after monitor `action_ready` → commands list `DESKTOP_CONTINUE`; burst `direct_action` matches.

---

### Step 2 — Central dispatch executor (shipped)

**Goal:** One module executes `direct_action` strings without a Cursor turn.

| Action | Handler |
|--------|---------|
| `DESKTOP_CONTINUE.cmd --no-pause` | subprocess full continue (not slim SSH finish) |
| `wait_for_vm` | `ppe_in_flight_monitor.py --daemon --auto-act` |
| `resolve_lease` | `ppe_worker_lease.py --assess` |
| `coordination_check` | `ppe_coordination_check.py --write` |
| `factory_throughput` | `ppe_factory_throughput.py --write` |
| `pipeline_health` | `ppe_pipeline_health.py --write` |
| `branch_recovery` | `ppe_branch_recovery.py --plane control --ship` (or repo-state recommended cmd) |

**Entry:** `scripts/ppe_operator_dispatch.py` + `ppe_operator_dispatch.cmd`

**Env:** `PPE_AUTO_DISPATCH=1` enables execution; default off.

**CLI:** `--dry-run` · `--from-status` · `--from-burst-plan` · `--force`

**Wire:** `prepare_operator_status()` → `maybe_auto_operate()`; monitor `--auto-act` → dispatch.

---

### Step 3 — Zero-click stack integration (shipped)

**Goal:** Opt-in desktop daemon chain monitor → continue without separate manual steps.

| Change | File | Status |
|--------|------|--------|
| Spawn monitor daemon when auto-operator skips in-flight | `scripts/ppe_desktop_auto_operator.py` | shipped |
| Use full `DESKTOP_CONTINUE` not slim SSH finish | `scripts/ppe_desktop_auto_operator.py` | shipped |
| Start monitor `--daemon --auto-act` from zero-click stack | `scripts/ppe_desktop_zero_click_build.py` | shipped |

**Setup:** `setup_desktop_zero_click_build.cmd` + `PPE_AUTO_DISPATCH=1` (set by `zero_click` start).

---

### Step 4 — Branch recovery gate (shipped)

**Goal:** Mixed-plane / dirty tree triggers recovery before continue or BUILD handoff.

| Change | File | Status |
|--------|------|--------|
| `automation_preflight_blocked()` + dispatch gate | `scripts/ppe_operator_dispatch.py` | shipped |
| Preflight gate in auto-operator | `scripts/ppe_desktop_auto_operator.py` | shipped |
| `direct_action: branch_recovery` when repo-state/coordination blocks | `scripts/ppe_burst_plan.py` (existing) | shipped |
| `maybe_auto_operate` in status write | `scripts/ppe_operator_status.py` | shipped |

**Rule:** `DESKTOP_CONTINUE` auto-dispatch skipped when `branch_preflight.blocks_relay` or `repo_state.relay_allowed` is false; prefers `branch_recovery` when delegation allows.

---

### Step 5 — Founder truth card + alert wiring

**Goal:** One glance answers “wait vs kick vs stuck”; alerts when monitor stuck with no active program.

| Change | File |
|--------|------|
| Truth card block at top of status | `scripts/ppe_operator_status.py` |
| Monitor `stuck` → Layer 3 alert | `scripts/ppe_founder_pulse.py` |
| Pass progress ingest monitor | `scripts/ppe_operator_pass_progress.py` |

**Fields:** live VM phase (SSH), git mirror age, monitor status, recommended founder posture (wait / nothing / alert).

---

### Step 6 — Optional scheduled dispatcher (Task Scheduler)

**Goal:** Headless pass every N minutes on opt-in desktop — no Cursor chat.

**Task:** `ppe_operator_dispatch.cmd --from-status --auto` (Step 2 prerequisite)  
**Install:** extend `install_ppe_desktop_zero_click_task.ps1` or new `install_ppe_operator_dispatch_task.ps1`  
**Default:** not installed; explicit opt-in.

---

## Opt-in matrix

| Capability | Token / flag | Default |
|------------|--------------|---------|
| Desktop auto-operator | `ppe_operator_desktop_auto.local.cmd` | off |
| Auto dispatch execute | `PPE_AUTO_DISPATCH=1` in env or `ppe_operator_desktop_auto.local.cmd` | off |
| Monitor auto-act | `--auto-act` on monitor daemon | off |
| Zero-click BUILD watcher | `setup_desktop_zero_click_build.cmd` | off |
| Scheduled dispatch task | Step 6 installer (`install_ppe_operator_dispatch_task.cmd`) | off |
| action_ready ntfy | deduped in `ACTION_READY_NOTIFY_STATE.json` | on when ntfy configured |

**Opt-in file:** copy `ppe_operator_desktop_auto.local.cmd.example` to `ppe_operator_desktop_auto.local.cmd`. The example sets both `PPE_DESKTOP_AUTO=1` and `PPE_AUTO_DISPATCH=1`; startup and zero-click setup upgrade legacy opt-in files that are missing the dispatch line.

---

## Level A → Level B auto-graduation

When `ppe_operator_desktop_auto.local.cmd` is present with dispatch enabled:

| Env | Default | Meaning |
|-----|---------|---------|
| `PPE_AUTO_GRADUATE_SUCCESSES` | `5` | Successful auto-dispatches before Level B |
| `PPE_AUTO_GRADUATE_MIN_HOURS` | `48` | Minimum hours since first success |

After thresholds met, the factory runs `setup_desktop_zero_click_build` + `start` (BUILD watcher + auto-operator + monitor daemon). Requires `agent login` for full Level B; setup still runs if agent CLI missing (continue-only daemons).

State: `artifacts/control_plane/DESKTOP_AUTOMATION_GRADUATION.json` (gitignored).

---

## What stays manual

- **IDE BUILD product judgment** — agent thread or zero-click watcher
- **`human_only` delegation** — founder decision
- **Charter / SELECTION** — founder threads
- **Canon conflicts** — founder pick

---

## Verification per step

```bat
python -m pytest tests/test_ppe_burst_plan.py tests/test_ppe_operator_monitor_enrich.py tests/test_ppe_in_flight_monitor.py -q
python scripts/ppe_operator_status.py --write
type artifacts\orchestrator\OPERATOR_STATUS.md
ppe_in_flight_monitor.cmd --json
python scripts/ppe_operator_dispatch.py --dry-run   REM after Step 2
```

### Cursor `/loop` when `wait_for_vm`

Operator thread (no `PPE_AUTO_DISPATCH`): loop `ppe_in_flight_monitor.cmd --json`, sleep `next_poll_s`, stop on `done` or `action_ready`. See `.cursor/rules/ppe-in-flight-monitor.mdc`.

---

## Changelog

| Date | Step |
|------|------|
| 2026-07-03 | v1 plan + Step 1 (`action_ready` in status/burst) |
| 2026-07-03 | Step 2 — central dispatch executor (`ppe_operator_dispatch`) |
| 2026-07-03 | Step 3 — zero-click monitor daemon wiring |
| 2026-07-03 | Step 4 — branch recovery preflight gate |
| 2026-07-03 | Steps 2–3 partial: dispatch cmd, `maybe_auto_operate`, auto-operator DESKTOP_CONTINUE |
