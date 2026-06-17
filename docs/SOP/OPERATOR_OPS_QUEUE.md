# Operator ops queue — high priority (non-product)

**Plane:** CONTROL-PLANE · **Not** a relay chapter — operator / VM tasks from the VM+desktop cutover backlog.

Mark `status: done` when complete. Product sequence continues via `PHASE_CHAPTER_BACKLOG.json`.

| Priority | Task | Where | Command / doc | Status |
|----------|------|-------|---------------|--------|
| **P0** | Register VM logon auto-start | VM (once) | `install_ppe_vm_headless_logon_task.cmd` | **done** (2026-06-17, agent via SSH) |
| **P0** | Confirm desktop loop-off guard | Desktop (once) | `setup_desktop_ide_only.cmd` | **done** (2026-06-17, agent) |
| **P0** | Verify VM stack healthy | VM | `ppe_autobuilder status --brief` | **done** — `stack_loop=True` `VERDICT=RUN_LOCAL` |
| **P0** | Reboot smoke (logon task) | VM | After next reboot → `VM_STATUS.cmd` | pending (needs real reboot) |
| **P1** | Hyper-V checkpoint `clean-base` | Host | Hyper-V Manager (host admin) | **queued** — needs host UI |
| **P1** | Remove stray `DESKTOP AUTO` shortcuts | Desktop | Auto-refresh shortcuts | **done** (no AUTO icons on Desktop) |
| **P1** | Cursor Automation zero-click BUILD | Desktop | [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md) | optional |
| **P2** | Schedule VM watchdog | VM | `install_ppe_vm_watchdog_task.cmd` | in progress (agent) |
| **P2** | IDE-on-VM (single machine) | VM | Separate thread | deferred |

**One-shot bootstrap (desktop):** `bootstrap_operator_pair.cmd` — desktop IDE-only + SSH VM logon task + stack ensure.

**Code landed (agent):** generic `fix_vm_operator`, git pull exempt paths, relay stale-state heal, ntfy button hints, SOP rewrites, `VM_WATCHDOG`, `setup_desktop_ide_only`, `install_ppe_vm_headless_logon_task.cmd`.

**Operator routine**

1. VM: `VM_STATUS` daily.
2. Phone `IDE_BUILD` ping → desktop `DESKTOP BUILD`.
3. After merge → `DESKTOP CONTINUE`.
4. VM reboot → logon task should auto-start; else `VM_AUTO`.
