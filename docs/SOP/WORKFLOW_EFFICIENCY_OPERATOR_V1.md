# Workflow efficiency operator v1

**Plane:** CONTROL-PLANE. **Purpose:** operational runbook for token, user-time, and throughput optimization.

Cross-refs: [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) · [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`WORKFLOW_METRICS_V1.md`](WORKFLOW_METRICS_V1.md)

---

## Four currencies

| Currency | Lever |
|----------|--------|
| **Tokens** | Local auto loop + IDE BUILD starter (one file) |
| **User time** | Guard resume → generated starter; ≤2 roundtrips per slice |
| **Computer time** | `run_pushable_gate.py` tiered gate (unchanged) |
| **Real-life time** | `workflow_metrics.cmd summary` — weighted slices per active hour |

---

## Daily (local profile)

**Policy:** [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md) · **Process:** [`PPE_OPERATOR_PROCESS_V1.md`](PPE_OPERATOR_PROCESS_V1.md)

### VM loop host

1. Stack runs via logon task or `VM_RESTART.cmd` — no daily git pull from phone.
2. `ppe_autobuilder.cmd status --brief` when triaging.
3. `fix_vm_operator.cmd` when relay stuck.

### Desktop (IDE BUILD)

1. `git pull` before BUILD sessions.
2. `DESKTOP_BUILD.cmd` on `IDE_BUILD` ntfy.
3. `DESKTOP_CONTINUE.cmd` after product PR merges.

### Legacy single-machine (no VM)

1. `git checkout main && git pull`
2. `python scripts/ppe_operator_status.py`
3. `run_ppe_auto_local_loop.cmd` — only when VM is **not** the loop host

---

## Product guard stop

When `PRODUCT_BLOCKED` or loop exit 7:

```bat
generate_ide_build_starter.cmd <sliceId> <phasePlanPath>
```

1. Open **new** Cursor Agent thread.
2. `@` `artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md` only.
3. Implement → commit on plan `buildBranch`.
4. `mark_ide_product_ready.cmd <sliceId> [phasePlanPath]`
5. `run_ppe_local.cmd`

Optional before BUILD:

```bat
python scripts/ppe_context_preflight.py --phase-plan <phasePlanPath> --slice-id <sliceId>
```

---

## Context bands (advisory)

Heuristics from [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md):

- Sprint spec ≤200 lines → NORMAL; 201–400 → WATCH; >400 → ESCALATE (continuous run stops)
- Generated BUILD packet target ≤~80 lines
- One Cursor thread per slice/chapter; no SELECTION+BUILD+PR mega-thread

---

## Commands

| Command | Purpose |
|---------|---------|
| `run_ppe_operator.cmd` | Status-only verdict (`--brief`, `--notify`, `--json`); auto-loop runs full preflight at startup |
| `generate_ide_build_starter.cmd` | One-file IDE BUILD bundle |
| `generate_build_packet.cmd` | Slim paths-only BUILD packet |
| `python scripts/ppe_context_preflight.py` | Advisory band check before BUILD |
| `workflow_metrics.cmd session start/stop` | Session logging (~30s) |
| `workflow_metrics.cmd slice close` | Per-slice roundtrips + size |
| `workflow_metrics.cmd summary --days 7` | Throughput review |
| `workflow_metrics.cmd export-csv` | Paste into Sheet tabs |
| `dev_changelog.cmd refresh` | Update rolling dev release notes ([`docs/RELEASES/DEV_CHANGELOG.md`](../RELEASES/DEV_CHANGELOG.md)) |
| `weekly_digest.cmd generate` | Monday-style human summary ([`docs/RELEASES/WEEKLY_DIGEST.md`](../RELEASES/WEEKLY_DIGEST.md)) |
| `workflow_radar.cmd generate` | Monday workflow friction scan + orphan auto-cleanup ([`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md)) |
| `workflow_radar.cmd cleanup --dry-run` | Orphan scan only (locks, triggers, job files) |
| `weekly_digest.cmd notify` | **ntfy** phone digest when `PPE_NTFY_TOPIC` is set; optional Windows toast (`PPE_WEEKLY_DIGEST_TOAST=0` for phone only) |
| `weekly_digest_monday.cmd` | `workflow_radar` + `generate` + `notify` — **Task Scheduler** entry (Monday 04:00) |
| `install_weekly_radar_monday_task.cmd` | Register Monday 04:00 local Task Scheduler job (run once) |
| `install_weekly_digest_monday_task.cmd` | Legacy alias — prefer `install_weekly_radar_monday_task.cmd` |
| `bootstrap_operator_pair.cmd` | One-shot desktop IDE-only + VM SSH setup ([`PPE_OPERATOR_PROCESS_V1.md`](PPE_OPERATOR_PROCESS_V1.md)) |
| `VM_RESTART.cmd` / `VM_STATUS.cmd` | **VM** loop host stack ([`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md)) |
| `DESKTOP_BUILD.cmd` / `DESKTOP_CONTINUE.cmd` | **Desktop** IDE BUILD handoff |
| [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md) | Paste prompt for new Cursor Agent chat on desktop |
| `start_ppe_desktop_operator.cmd` | **Legacy** — desktop stack when no VM; do not use on daily PC with VM live |
| `watch_operator_mobile.cmd` | ntfy push on verdict change or loop death (`PPE_NTFY_TOPIC`) |

**Monday popup (local):** Task Scheduler — use **cmd.exe** (paths with spaces break if you paste the `.cmd` directly):

| Field | Value |
|-------|--------|
| Program | `cmd.exe` |
| Arguments | `/c "D:\Users\User\Desktop\Probability prediction engine\weekly_digest_monday.cmd"` |
| Start in | `D:\Users\User\Desktop\Probability prediction engine` |

Recommended: **Monday 04:00 local** via `install_weekly_radar_monday_task.cmd` (radar + digest + notify). Radar scans workflow friction, auto-cleans stale operator artifacts (build locks, stuck triggers, orphan job files), then refreshes the digest.

From **PowerShell**, run `.cmd` files via **`cmd /c`** (PowerShell does not execute `.cmd` with `&` alone):

```bat
cmd /c weekly_digest.cmd notify
```

Requires PC on at run time. One-time scheduler: `install_weekly_radar_monday_task.cmd`. Radar output: `artifacts/control_plane/WORKFLOW_RADAR_LATEST.md`. Notify reads `artifacts/control_plane/WEEKLY_DIGEST_NOTIFY.json`. Disable all notify: `set PPE_NOTIFY=0`. Phone-only: `set PPE_WEEKLY_DIGEST_TOAST=0` in `ppe_operator_notify.local.cmd`.

Data lives under `artifacts/workflow_metrics/` (gitignored).

---

## Thread rules

- **Steward thread:** SELECTION, manifest, read `LAST_RUN_REPORT.md`
- **IDE BUILD thread:** starter file only (not steward chat)
- **After closeout:** new thread + `AGENT_CONTINUITY_BRIEF.md` only ([`CONTEXT_RULES.md`](../CONTEXT_RULES.md))

---

## Related

- [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)
- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md)
