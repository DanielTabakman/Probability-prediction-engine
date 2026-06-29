# Workflow efficiency operator v1

**Plane:** CONTROL-PLANE. **Purpose:** operational runbook for token, user-time, and throughput optimization.

Cross-refs: [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) · [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`WORKFLOW_METRICS_V1.md`](WORKFLOW_METRICS_V1.md)

---

## Four currencies

| Currency | Lever |
|----------|--------|
| **Tokens** | VM local loop (no LLM) + Codex headless BUILD + IDE starter only when blocked |
| **User time** | Guard resume → generated starter; ≤2 roundtrips per slice |
| **Computer time** | `run_pushable_gate.py` tiered gate (unchanged) |
| **Real-life time** | `workflow_metrics.cmd summary --by-lane` — throughput + lane mix (also in `OPERATOR_STATUS`) |

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

### Burst mode (adaptive — default)

- **Start:** `python scripts/ppe_burst_plan.py --write` → `artifacts/control_plane/BURST_PLAN.json`
- **Cap:** `min(remaining_slices, band_cap)` where band_cap is NORMAL→3 workers, WATCH→1, ESCALATE→0
- **Sub-agents:** `IDE_BUILD` / `RUN_LOCAL` → **`@ppe-director`** spawns build/finish workers only
- **Handoff:** `ppe_go.cmd` (burst default); `ppe_go.cmd --single` for one-shot
- Canon: [`.cursor/rules/ppe-burst-mode.mdc`](../../.cursor/rules/ppe-burst-mode.mdc)

---

## Commands

| Command | Purpose |
|---------|---------|
| `run_ppe_operator.cmd` | Status-only verdict (`--brief`, `--notify`, `--json`); auto-loop runs full preflight at startup |
| `verify_build_worker.cmd` | Codex-first BUILD worker policy check |
| `setup_vm_codex.cmd` | **Desktop:** one-time Codex install + login on VM loop host |
| `verify_codex.cmd` | Codex CLI login + resolved worker |
| `token_audit.cmd` | Token economy audit (rules, starters, build worker) |
| `regenerate_ide_starters.cmd` | Bulk refresh on-disk IDE starters |
| `setup_codex.cmd` | One-time Codex CLI install + login |
| `generate_ide_build_starter.cmd` | One-file IDE BUILD bundle |
| `generate_build_packet.cmd` | Slim paths-only BUILD packet |
| `python scripts/ppe_context_preflight.py` | Advisory band check before BUILD |
| `workflow_metrics.cmd session start/stop` | Session logging (~30s) |
| `workflow_metrics.cmd slice close` | Per-slice roundtrips + size + `--worker-lane` |
| `workflow_metrics.cmd summary --days 7 --by-lane` | Throughput + lane rollup |
| `workflow_metrics.cmd export-csv` | Paste into Sheet tabs |
| `dev_changelog.cmd refresh` | Update rolling dev release notes ([`docs/RELEASES/DEV_CHANGELOG.md`](../RELEASES/DEV_CHANGELOG.md)) |
| `weekly_digest.cmd generate` | Monday-style human summary ([`docs/RELEASES/WEEKLY_DIGEST.md`](../RELEASES/WEEKLY_DIGEST.md)) |
| `monday_morning_prep.cmd prep` | Autoclean orphans + queue repair + safe operator fixes |
| `workflow_radar.cmd generate` | Workflow friction scan (`--no-cleanup` when prep already ran) |
| `workflow_radar.cmd cleanup --dry-run` | Orphan scan only (locks, triggers, job files) |
| `weekly_digest.cmd notify` | **ntfy** phone digest when `PPE_NTFY_TOPIC` is set; optional Windows toast (`PPE_WEEKLY_DIGEST_TOAST=0` for phone only) |
| `weekly_digest_monday.cmd` | **Single Monday pipeline:** prep → wait until **08:00** → radar → digest → notify |
| `install_weekly_radar_monday_task.cmd` | Register Task Scheduler: starts **06:00** local, report at **08:00** (run once) |
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

Recommended: **Monday 06:00 local** via `install_weekly_radar_monday_task.cmd` — one task runs `weekly_digest_monday.cmd`, which **preps** (autoclean + easy fixes), **waits until 08:00**, then sends the digest + ntfy. Override report time: `set PPE_MONDAY_REPORT_HOUR=8` in `ppe_operator_local.cmd`.

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
- [`PPE_COST_ACCOUNTING_V1.md`](PPE_COST_ACCOUNTING_V1.md)
- [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md)
