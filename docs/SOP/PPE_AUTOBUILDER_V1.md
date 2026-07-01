# PPE autobuilder v1

**Plane:** CONTROL-PLANE. **Purpose:** one bounded system for running and diagnosing the IDE BUILD pipeline (loop → dispatch → closeout → relay).

**Agent:** `@ppe-autobuilder-operator` · **Entry:** `ppe_autobuilder.cmd`

**Related:** [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) · [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md)

---

## Quick start

| You want | Command / agent |
|----------|-----------------|
| **Which button?** | [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) |
| **Status snapshot** | `ppe_autobuilder.cmd status` |
| **Diagnose stuck pipeline** | `ppe_autobuilder.cmd diagnose` or `@ppe-autobuilder-operator diagnose the autobuilder` |
| **Auto-fix current phase** | `ppe_autobuilder.cmd advance` |
| **Start stack** | `ppe_autobuilder.cmd ensure` |
| **Implement product code** | `@ppe-build-worker` + starter (not autobuilder operator) |

Default `ppe_autobuilder.cmd` (no args) prints brief status and writes `artifacts/orchestrator/AUTOBUILDER_STATUS.json`.

---

## What the autobuilder owns

On the **VM loop host** (headless stack via `run_ppe_headless_stack.cmd` — see [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md)):

1. **Loop** — `run_ppe_auto_local_loop.cmd` (relay + guards)
2. **Watch** — `watch_operator_mobile.cmd` (ntfy + auto-dispatch + post-build finish)
3. **ntfy commands** — `watch_ntfy_commands.cmd` (phone `build` / `fix`)

Legacy single-machine entry: `start_ppe_desktop_operator.cmd` — **not** for daily desktop when VM is live.

Plus dispatch paths:

- Unified BUILD worker ([`ppe_build_worker.py`](../../scripts/ppe_build_worker.py)): local profile uses **`buildWorker: codex`** (Codex CLI → desktop Codex; Cursor when Codex blocked). Override with `auto` (Cursor → Codex) or `cursor` / `manual`.
- Headless CLI (`agent` / `codex exec`) when `autoRemoteBuild` allows
- Desktop handoff (`DESKTOP_BUILD.cmd` → starter + IDE_BUILD_NOW.md; opens Cursor or Codex)
- Post-build watcher (`mark_ide_product_ready` + `run_ppe_local`)

---

## Phases

| Phase | Meaning | Typical action |
|-------|---------|----------------|
| `STACK_DOWN` | Loop or watch not running | `ensure` |
| `HEALTHY_IDLE` | `RUN_AUTO` / `SUPPLY_LOW`, stack OK | none |
| `AWAITING_BUILD` | Product slice needs IDE BUILD | `advance` / `retry-build` |
| `BUILD_IN_FLIGHT` | `REMOTE_BUILD_LOCK.json` active | wait |
| `CLOSEOUT_PENDING` | Commits on build branch, no marker | `finish-pending` |
| `FINISH_IN_FLIGHT` | post_build worker running | wait |
| `RUN_LOCAL_PENDING` | Marker present, relay pending | `run-local` |
| `DEGRADED` | CLI quota / automation broken | `handoff` |
| `FIX_PLAN` / `STALE_STATE` / `ERROR` | Plan or relay issue | triage worker |

Canonical JSON: `artifacts/orchestrator/AUTOBUILDER_STATUS.json`

---

## Commands

```bat
ppe_autobuilder.cmd status --json --write
ppe_autobuilder.cmd diagnose
ppe_autobuilder.cmd ensure
ppe_autobuilder.cmd advance
ppe_autobuilder.cmd retry-build
ppe_autobuilder.cmd handoff
ppe_autobuilder.cmd finish-pending
ppe_autobuilder.cmd run-local
```

---

## Agent prompts

**Diagnose:**

```text
@ppe-autobuilder-operator Diagnose the autobuilder. Use only ppe_autobuilder.cmd. Do not implement product code.
```

**Run / advance:**

```text
@ppe-autobuilder-operator Run ppe_autobuilder.cmd advance and report phase before/after.
```

**Product slice (separate thread):**

```text
@ppe-build-worker Load artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md
```

---

## Separation of roles

| Agent | Owns |
|-------|------|
| `@ppe-autobuilder-operator` | Pipeline health, dispatch, closeout recovery |
| `@ppe-director` | Manual `ppe_go.cmd` verdict routing |
| `@ppe-build-worker` | One product slice implementation |
| `@ppe-finish-worker` | `RUN_LOCAL` only |
| `@ppe-triage-worker` | `FIX_PLAN` / `ERROR` diagnosis |

---

## Artifacts

| File | Role |
|------|------|
| `CONTROL_PLANE_STATUS.json` | **Canonical human read** — run `ppe_autobuilder.cmd reconcile` |
| `AUTOBUILDER_STATUS.json` | Machine snapshot (embedded in control plane) |
| `AUTOBUILDER_DIAGNOSE.md` | Human diagnose report |
| `OPERATOR_STATUS.md` | Legacy verdict summary (regenerated on reconcile) |
| `IDE_BUILD_TRIGGER.json` | Cursor Automation trigger |
| `IDE_PRODUCT_READY.json` | Product slice marker for guards |
