# Operator ops queue — high priority (non-product)

**Plane:** CONTROL-PLANE · **Not** a relay chapter — operator / VM tasks from the VM+desktop cutover backlog.

Mark `status: done` when complete. Product sequence continues via `PHASE_CHAPTER_BACKLOG.json`.

| Priority | Task | Where | Command / doc | Status |
|----------|------|-------|---------------|--------|
| **P0** | Register VM logon auto-start | VM (once) | `install_ppe_vm_headless_logon_task.cmd` | pending |
| **P0** | Confirm desktop loop-off guard | Desktop (once) | `setup_desktop_ide_only.cmd` | pending |
| **P0** | Verify VM stack healthy after reboot | VM | `VM_STATUS.cmd` → expect `stack_loop=True` | pending |
| **P1** | Hyper-V checkpoint `clean-base` | Host | `scripts/create_ppe_loop_host_checkpoint.ps1` (if present) | pending |
| **P1** | Remove stray `DESKTOP AUTO` shortcuts | Desktop | Delete manually if any remain | pending |
| **P1** | Cursor Automation for zero-click BUILD | Desktop | [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md) | optional |
| **P2** | Schedule VM watchdog (optional) | VM | Task Scheduler → `VM_WATCHDOG.cmd` every 10 min | optional |
| **P2** | IDE-on-VM (single machine) | VM | Separate thread — deferred by operator | deferred |

**Code landed (agent):** generic `fix_vm_operator`, git pull exempt paths, relay stale-state heal, ntfy button hints, SOP rewrites, `VM_WATCHDOG`, `setup_desktop_ide_only`, `install_ppe_vm_headless_logon_task.cmd`.

**Operator routine**

1. VM: `VM_STATUS` daily.
2. Phone `IDE_BUILD` ping → desktop `DESKTOP BUILD`.
3. After merge → `DESKTOP CONTINUE`.
4. VM reboot → logon task should auto-start; else `VM_AUTO`.
