# PPE headless desktop stack v1

**Plane:** CONTROL-PLANE. **Purpose:** run loop + watch + ntfy + IDE watcher without popup `cmd` windows.

**Entry:** `run_ppe_headless_stack.cmd`

---

## Quick start

| When | Command |
|------|---------|
| **Start (one terminal)** | `run_ppe_headless_stack.cmd` — Ctrl+C stops supervisor + workers |
| **Start detached** (Task Scheduler / logon) | `run_ppe_headless_stack.cmd --ensure` |
| **Stop** | `run_ppe_headless_stack.cmd --stop` |
| **Status** | `ppe_autobuilder.cmd status` |

Enable in [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json):

```json
"desktopStack": { "mode": "headless" }
```

Or set `PPE_STACK_HEADLESS=1`.

---

## What runs

One **supervisor** process spawns and monitors detached workers:

| Worker | Log |
|--------|-----|
| Auto loop | `artifacts/orchestrator/HEADLESS_STACK_LOOP.log` |
| Mobile watch | `artifacts/orchestrator/HEADLESS_STACK_WATCH.log` |
| ntfy commands | `artifacts/orchestrator/HEADLESS_STACK_NTFY_LISTEN.log` |
| IDE BUILD watcher | `artifacts/orchestrator/HEADLESS_STACK_LOCAL_TRIGGER_WATCHER.log` |
| Supervisor | `artifacts/orchestrator/HEADLESS_STACK_SUPERVISOR.log` |

State: `artifacts/orchestrator/HEADLESS_STACK_SUPERVISOR.json`

`ensure` / `restart` / `start_ppe_desktop_operator.cmd` use headless mode when configured — no extra windows.

---

## VM recommendation

Run headless stack on a **Hyper-V VM** (loop host). Your daily PC stays clean; restore VM snapshot if the stack misbehaves.

On a daily-driver PC until the VM exists: keep `ideHandoff.openCursor: false` so handoff does not steal Cursor focus.

**VM loop host:** [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md) — run headless stack on Hyper-V; keep daily PC stack off.

See [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md) · [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md).

---

## Legacy windows mode

Set `desktopStack.mode` to `windows` (or `PPE_STACK_HEADLESS=0`) to restore the old four-window `start_ppe_desktop_operator.cmd` behavior.
