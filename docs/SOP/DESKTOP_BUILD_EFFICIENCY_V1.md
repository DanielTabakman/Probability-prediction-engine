# Desktop BUILD efficiency v1

**Plane:** CONTROL-PLANE · **Canon:** [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md) · [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md)

---

## Goal

Shrink **IDE_BUILD → merge → CONTINUE** wall clock on the daily desktop without moving the relay loop off the VM.

---

## One-time setup (daily PC)

```bash
setup_desktop_build_efficiency.cmd
```

This runs [`setup_desktop_zero_click_build.cmd`](../../setup_desktop_zero_click_build.cmd) which:

1. Ensures `ppe_operator_no_loop.local.cmd` (desktop must not run VM loop)
2. Creates `ppe_operator_desktop_auto.local.cmd` opt-in token
3. Installs **logon Task Scheduler** task for zero-click watcher
4. Starts **local IDE_BUILD trigger watcher** + post-build watcher path

Prerequisites: `setup_cursor_agent.cmd` + `agent login` on desktop.

---

## What runs automatically after setup

| Stage | Automation |
|-------|------------|
| VM blocks on product slice | ntfy `IDE_BUILD` |
| Handoff file written | `.cursor/IDE_BUILD_TRIGGER.json` |
| Desktop watcher (~5s) | Dispatches agent CLI with starter packet |
| Agent commits product code | `ppe_post_build_watcher.py` can `mark_ide_product_ready` |
| PR pushed | **automerge** + CI squash merge (no click) |
| **You** | `DESKTOP_CONTINUE.cmd` after merge (SSH finish on VM) |

**Your remaining manual step:** `DESKTOP_CONTINUE.cmd` once PR merges — keep desktop reachable when ntfy fires.

---

## Buttons

| Script | When |
|--------|------|
| `DESKTOP_BUILD.cmd` | Manual BUILD if zero-click missed |
| `DESKTOP_CONTINUE.cmd` | After PR merge — VM relay continue |
| `DESKTOP_ZERO_CLICK_START.cmd` / `STOP.cmd` | Watcher daemon control |

---

## Disable

Delete `ppe_operator_desktop_auto.local.cmd` and run `DESKTOP_ZERO_CLICK_STOP.cmd`.
