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

1. `run_ppe_operator.cmd` — verdict + next commands (`artifacts/orchestrator/OPERATOR_STATUS.md`)
2. Follow verdict: `run_ppe_auto_local_loop.cmd` **or** IDE BUILD path **or** `run_ppe_local.cmd`
3. Optional: `workflow_metrics.cmd session start` at desk open

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
| `run_ppe_operator.cmd` | Status verdict before auto-loop (`--brief`, `--notify`, `--json`) |
| `generate_ide_build_starter.cmd` | One-file IDE BUILD bundle |
| `generate_build_packet.cmd` | Slim paths-only BUILD packet |
| `python scripts/ppe_context_preflight.py` | Advisory band check before BUILD |
| `workflow_metrics.cmd session start/stop` | Session logging (~30s) |
| `workflow_metrics.cmd slice close` | Per-slice roundtrips + size |
| `workflow_metrics.cmd summary --days 7` | Throughput review |
| `workflow_metrics.cmd export-csv` | Paste into Sheet tabs |
| `dev_changelog.cmd refresh` | Update rolling dev release notes ([`docs/RELEASES/DEV_CHANGELOG.md`](../RELEASES/DEV_CHANGELOG.md)) |
| `weekly_digest.cmd generate` | Monday-style human summary ([`docs/RELEASES/WEEKLY_DIGEST.md`](../RELEASES/WEEKLY_DIGEST.md)) |
| `weekly_digest.cmd notify` | Windows toast with latest **In short** (respects `PPE_NOTIFY=0`) |
| `weekly_digest_monday.cmd` | `generate` + `notify` — **Task Scheduler** entry for Monday reminder |

**Monday popup (local):** Task Scheduler — use **cmd.exe** (paths with spaces break if you paste the `.cmd` directly):

| Field | Value |
|-------|--------|
| Program | `cmd.exe` |
| Arguments | `/c "D:\Users\User\Desktop\Probability prediction engine\weekly_digest_monday.cmd"` |
| Start in | `D:\Users\User\Desktop\Probability prediction engine` |

From **PowerShell**, run `.cmd` files via **`cmd /c`** (PowerShell does not execute `.cmd` with `&` alone):

```bat
cmd /c weekly_digest.cmd notify
```

Default popup is a **MessageBox** with **Yes/No to open** [`WEEKLY_DIGEST.md`](../RELEASES/WEEKLY_DIGEST.md) in your default editor. Optional corner toast: `set PPE_WEEKLY_DIGEST_POPUP=toast` or `both`. Skip open prompt: `set PPE_WEEKLY_DIGEST_AUTO_OPEN=0`. Disable all: `set PPE_NOTIFY=0`.

Data lives under `artifacts/workflow_metrics/` (gitignored).

---

## Thread rules

- **Steward thread:** SELECTION, manifest, read `LAST_RUN_REPORT.md`
- **IDE BUILD thread:** starter file only (not steward chat)
- **After closeout:** new thread + `AGENT_CONTINUITY_BRIEF.md` only ([`CONTEXT_RULES.md`](../CONTEXT_RULES.md))

---

## Related

- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md)
