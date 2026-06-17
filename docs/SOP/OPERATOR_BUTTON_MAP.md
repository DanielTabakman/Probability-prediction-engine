# Operator button map — which machine, which double-click

**Plane:** CONTROL-PLANE · **Canonical layout:** [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md)

| Symptom / verdict | Machine | Action |
|-------------------|---------|--------|
| `VERDICT=IDE_BUILD` | **Desktop PC** | `DESKTOP_BUILD.cmd` → paste in Cursor Agent → gate → commit → PR |
| After product PR merged | **Desktop PC** | `DESKTOP_CONTINUE.cmd` (pull + SSH finish on VM) |
| `PHASE=STACK_DOWN` / `stack_loop=False` | **VM** | `VM_RESTART.cmd` or `VM_AUTO.cmd` |
| Check health | **VM** | `VM_STATUS.cmd` (wait ~10s for `PHASE=`) |
| Emergency stop popups | **VM** | `VM_STOP.cmd` |
| Emergency stop on real PC | **Desktop** | `DESKTOP_STOP.cmd` |
| Stuck relay / stale state | **VM** | `fix_vm_operator.cmd` (= `vm_bootstrap.cmd --recover`) |
| VM reboot — auto-start stack | **VM** (once) | `install_ppe_vm_headless_logon_task.cmd` |
| Desktop IDE-only setup | **Desktop** (once) | `setup_desktop_ide_only.cmd` |
| Sync scripts from GitHub | **VM** | `VM_UPDATE.cmd` |

**Hard rules**

- Loop host = **Hyper-V VM only** (`ppe_operator_loop_host.local.cmd`).
- Desktop = **IDE BUILD only** (`ppe_operator_no_loop.local.cmd`).
- Do **not** enable `DESKTOP_AUTO` on the daily PC unless you explicitly opt in.

Phone ntfy messages append the same hints via `scripts/ppe_operator_hint.py`.
