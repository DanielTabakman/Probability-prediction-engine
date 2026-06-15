# PPE loop host — Hyper-V VM v1

**Plane:** CONTROL-PLANE. **Purpose:** run the headless operator stack on an isolated VM so the daily PC never gets popup/focus storms.

**Host:** Windows 10/11 **Pro** with Hyper-V. **Guest:** Windows 10/11.

**Stack entry (inside VM only):** [`PPE_HEADLESS_STACK_V1.md`](PPE_HEADLESS_STACK_V1.md) · `run_ppe_headless_stack.cmd`

**Multi-clone (optional):** [`PPE_MULTI_OPERATOR_V1.md`](PPE_MULTI_OPERATOR_V1.md) · [`PPE_OUTPUT_PIPELINE_V1.md`](PPE_OUTPUT_PIPELINE_V1.md)

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

Inside VM, Task Scheduler or:

```bat
install_ppe_desktop_operator_task.cmd
```

Ensure task runs `run_ppe_headless_stack.cmd --ensure` (not legacy windowed `start_ppe_desktop_operator.cmd`).

---

## Phase 7 — Keep daily PC clean

On the **host** (daily PC), leave stack **stopped**:

```bat
run_ppe_headless_stack.cmd --stop
```

Do not run `run_ppe_desktop_operator.cmd` or `start_ppe_desktop_operator.cmd` on the host.

---

## Recovery

| Problem | Fix |
|---------|-----|
| Stack misbehaving | VM: `run_ppe_headless_stack.cmd --stop` then `--ensure` |
| Worse | Hyper-V → Restore checkpoint **clean-base** → re-run Phase 4–5 |
| Host focus storms | Confirm no PPE processes on host: `ppe_autobuilder.cmd status` |

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
