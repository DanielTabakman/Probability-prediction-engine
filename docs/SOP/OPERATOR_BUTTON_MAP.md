# Operator button map — which machine, which double-click

**Plane:** CONTROL-PLANE · **Policy:** [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md)  
**Verdict → command (SSOT):** [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md)  
**Layout / thread handoff:** [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md)

## IDE BUILD — when phone says `IDE_BUILD` (most common)

**Machine:** your **real daily PC** — never the Hyper-V VM.

| Step | What you do |
|------|-------------|
| 1 | Double-click **`DESKTOP BUILD`** (shortcut to `DESKTOP_BUILD.cmd` in repo) |
| 2 | Follow on-screen worker steps (**Cursor Agent** or **Codex** — see `CONTROL_PLANE_STATUS.json` → `runtime.build.handoff_worker`) |
| 3 | Build prompt is **already on clipboard** — **Ctrl+V** → Enter |
| 4 | Agent implements slice, runs gate, commits, closeout |
| 5 | After PR merges → double-click **`DESKTOP CONTINUE`** |

You do **not** need Automations, API credits, or `run_ppe_local` on the desktop. The VM loop continues automatically after closeout.

`DO_THE_THING.cmd` exists in the repo folder as a smart fallback; the desktop shortcut you want is **`DESKTOP BUILD`**.

---

| Symptom / verdict | Machine | Action |
|-------------------|---------|--------|
| `VERDICT=IDE_BUILD` | **Real PC** | **`DESKTOP BUILD`** → new Agent → **Ctrl+V** → Enter |
| After product PR merged | **Real PC** | **`DESKTOP CONTINUE`** (pull + SSH finish on VM) |
| Live VM health from desktop | **Real PC** | **`DESKTOP VM STATUS`** (SSH + auto-ensure stack) |
| `PHASE=STACK_DOWN` / `stack_loop=False` | **VM** | `VM_RESTART.cmd` or `VM_AUTO.cmd` |
| Check health | **VM** | `VM_STATUS.cmd` or `check_vm_loop.cmd --no-pause` |
| Weekly git/worktree hygiene | **VM** (once) | `install_ppe_vm_hygiene_task.cmd` |
| Status stale / docs disagree | **Either** | `ppe_request.cmd reconcile` → `CONTROL_PLANE_STATUS.json` |
| Queue human chapter work | **Steward** | `ppe_request.cmd --chapter-id … --reason "…" [--apply]` |
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

Full verdict table and forbidden desktop commands: [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md).

Phone ntfy messages append the same hints via `scripts/ppe_operator_hint.py`.
