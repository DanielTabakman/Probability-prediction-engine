# PPE loop host — Hyper-V VM v1

**Plane:** CONTROL-PLANE. **Purpose:** run the headless operator stack on an isolated VM so the daily PC never gets popup/focus storms.

**Policy:** [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md) (accepted 2026-06-17)

**Host:** Windows 10/11 **Pro** with Hyper-V. **Guest:** Windows 10/11.

**Stack entry (inside VM only):** [`PPE_HEADLESS_STACK_V1.md`](PPE_HEADLESS_STACK_V1.md) · `run_ppe_headless_stack.cmd`

**Related:** [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md) · [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)

---

## Roles after VM is live

| Machine | Job |
|---------|-----|
| **Daily PC** | Normal Cursor work — **no** auto-loop |
| **Hyper-V VM** | Headless stack 24/7 (loop + watch + ntfy + IDE watcher) |
| **Phone** | ntfy alerts + optional RDP into VM |

---

## Host sizing (this PC: ~16 GB RAM, 8 threads)

| Resource | VM allocation | Leave for host |
|----------|---------------|----------------|
| RAM | **8192 MB** (6 GB minimum) | ~8 GB |
| vCPU | **2** | 6 |
| Disk | **80 GB** dynamic VHD | — |

---

## Phase 1 — Enable Hyper-V on host (once, Administrator)

Open **PowerShell as Administrator** on the daily PC:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

Reboot when prompted.

Verify after reboot:

```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All | Select-Object State
```

Expect `State : Enabled`.

---

## Phase 2 — Create the VM (Hyper-V Manager)

1. Open **Hyper-V Manager** → **New** → **Virtual Machine**.
2. **Name:** `PPE-Loop-Host`
3. **Generation:** 2
4. **Memory:** 8192 MB · uncheck *Use Dynamic Memory* (or cap at 8192)
5. **Networking:** Default Switch (or External if you need VM on LAN)
6. **Disk:** 80 GB VHDX
7. **Install OS:** mount Windows 10/11 ISO (same language as host is fine)
8. Complete Windows setup inside VM (local account OK)

**First snapshot (important):**

```text
Hyper-V Manager → PPE-Loop-Host → Checkpoint → "clean-base"
```

Or from an **Administrator** PowerShell on the host:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_ppe_loop_host_checkpoint.ps1
```

Restore this checkpoint anytime the VM stack goes sideways.

---

## Phase 3 — VM guest settings (inside VM)

### Power

Settings → Power → plugged in → **Sleep: Never** (display off OK).

### Tailscale

Install Tailscale on the VM (same account as phone/host). Note VM hostname (e.g. `ppe-loop-host`).

### Remote Desktop (optional, phone triage)

Run as Administrator inside VM (from repo after clone):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\enable_rdp_tailscale.ps1
```

Use Microsoft Remote Desktop from phone over Tailscale — not on daily PC unless fixing something.

---

## Phase 4 — Repo + operator config (inside VM)

```bat
git clone https://github.com/DanielTabakman/Probability-prediction-engine.git
cd Probability-prediction-engine
git pull
python --version
pip install -r requirements.txt
python scripts\ppe_operator_env.py
```

**Loop-host token (required before starting stack):**

```bat
copy ppe_operator_loop_host.local.cmd.example ppe_operator_loop_host.local.cmd
```

This sets `PPE_LOOP_HOST=1`. Without it, `run_ppe_headless_stack.cmd` exits **8** and refuses to start.

Copy notify config from host (or recreate):

```bat
copy ppe_operator_notify.local.cmd.example ppe_operator_notify.local.cmd
```

Edit `PPE_NTFY_TOPIC=` to match phone (same topic as before is fine).

Verify push:

```bat
python scripts\ppe_notify_push.py --check
python scripts\ppe_notify_push.py --title "PPE VM ready" --body "loop host online"
```

Confirm `docs/SOP/PPE_AUTO_OPERATOR.local.json` has:

```json
"desktopStack": { "mode": "headless" },
"ideHandoff": { "openCursor": false }
```

(`openCursor: true` is OK **inside VM only** if BUILD runs there — still optional.)

Install **Cursor** inside VM if phone `build` / IDE BUILD should run on the VM.

---

## Phase 5 — Start headless stack (inside VM only)

```bat
run_ppe_headless_stack.cmd --ensure
ppe_autobuilder.cmd status --brief
```

Expect `stack_running=True`, no popup windows.

Logs: `artifacts\orchestrator\HEADLESS_STACK_*.log`

**Stop:**

```bat
run_ppe_headless_stack.cmd --stop
```

---

## Phase 6 — Auto-start at VM logon (optional)

Inside VM, double-click once:

```bat
install_ppe_vm_headless_logon_task.cmd
```

This registers Task Scheduler task **PPE Headless Stack** → `run_ppe_headless_stack.cmd --ensure` at user logon.

To remove: `powershell -File scripts\install_ppe_vm_headless_logon_task.ps1 -RepoRoot . -Unregister`

**Do not** use `install_ppe_desktop_operator_task.cmd` on the VM or daily PC (legacy windowed stack).

---

## Phase 7 — Keep daily PC clean

On the **host** (daily PC), install the no-loop guard **once**:

```bat
copy ppe_operator_no_loop.local.cmd.example ppe_operator_no_loop.local.cmd
```

This sets `PPE_STACK_FORBIDDEN=1`. Any attempt to start the stack or auto-loop on the host exits **8** with a clear message — only the VM may run the loop.

Leave stack **stopped** on the host:

```bat
run_ppe_headless_stack.cmd --stop
```

Do not run `run_ppe_desktop_operator.cmd` or `start_ppe_desktop_operator.cmd` on the host (guard blocks them anyway).

**Remote agent on VM:** [`PPE_CURSOR_REMOTE_SSH_V1.md`](PPE_CURSOR_REMOTE_SSH_V1.md)

---

## Hard rules (two-loop prevention)

| Machine | File (gitignored) | Env var | Effect |
|---------|-------------------|---------|--------|
| **VM only** | `ppe_operator_loop_host.local.cmd` | `PPE_LOOP_HOST=1` | Stack/loop **allowed** |
| **Host only** | `ppe_operator_no_loop.local.cmd` | `PPE_STACK_FORBIDDEN=1` | Stack/loop **blocked** |
| Neither / both missing | — | — | Stack **blocked** (safe default) |

Guard script: `scripts/ppe_loop_host_guard.py` · wired into `run_ppe_headless_stack.cmd`, `run_ppe_auto_loop.cmd`, `ensure_stack`.

**Escape hatch (emergency only):** `set PPE_FORCE_STACK=1` bypasses the guard — do not use on the daily PC while the VM is live.

**Stop always works:** `run_ppe_headless_stack.cmd --stop` ignores the guard so you can kill a stray stack on either machine.

---

## Recovery

| Problem | Fix |
|---------|-----|
| Stack misbehaving / popups | VM: **`VM_STOP.cmd`** → close blank windows → **`VM_RESTART.cmd`** once |
| Check health | VM: **`VM_STATUS.cmd`** (wait ~10s for `PHASE=` line) |
| Missing scripts on VM | VM: **`VM_UPDATE.cmd`** or `git pull origin main` |
| Stack misbehaving (CLI) | VM: `run_ppe_headless_stack.cmd --stop` then `--ensure` |
| Stuck `RUN_LOCAL` / split state | VM: `vm_bootstrap.cmd` then `fix_vm_operator.cmd` |
| First boot / after checkpoint | VM: `setup_vm_loop_host.cmd` then `vm_bootstrap.cmd --recover` |
| Daily status (CLI) | VM: `check_vm_loop.cmd` or `ppe_autobuilder.cmd status --brief` |
| Worse | Hyper-V → Restore checkpoint **clean-base** → re-run Phase 4–5 |
| Host focus storms | Desktop: **`DESKTOP_STOP.cmd`** · confirm `ppe_operator_no_loop.local.cmd` exists |
| `stack_forbidden` on VM | Remove `ppe_operator_no_loop.local.cmd` (or run `setup_vm_loop_host.cmd` — renames to `.off-vm`) |

**Operator card:** [`VM_OPERATOR_README.txt`](../../VM_OPERATOR_README.txt) · **Session handoff:** [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md)

---

## Agent prompt (new Cursor chat **inside VM**)

```text
You are bootstrapping this Hyper-V VM as the PPE loop host.

Read and follow ONLY:
@docs/SOP/PPE_VM_LOOP_HOST_V1.md
@docs/SOP/PPE_HEADLESS_STACK_V1.md
@docs/SOP/PPE_MOBILE_OPERATOR_V1.md

Walk one step at a time. Run verification commands yourself. Stop after each step until I confirm.
Do NOT start the stack on the daily PC — only inside this VM.
```
