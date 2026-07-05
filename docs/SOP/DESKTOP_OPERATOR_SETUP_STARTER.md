# Desktop operator setup — Cursor Agent starter

**Plane:** CONTROL-PLANE only.

**Layout (Hyper-V VM live):** **VM = loop host 24/7** · **Desktop = Cursor IDE BUILD only**. Canonical map: [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md) · [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md).

**Purpose:** one Agent thread on the **desktop** walks IDE-BUILD-only setup — no loop, no API spend.

**Canonical runbook:** [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) (loop details: [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md))

---

## Leaving the laptop (handoff checklist)

Do this **once** on the laptop before you close Cursor there:

1. **Nothing to save in chat** — instructions live in this repo on GitHub.
2. **Working tree clean?** `git status` should show nothing to commit (or commit/push anything you still need).
3. **On `main`:** `git checkout main` then `git pull`.
4. **On desktop:** clone or `git pull`, run **`setup_desktop_ide_only.cmd`** once, open this folder in Cursor.

GitHub `main` is the single source of truth — desktop and VM are clones.

---

## What to paste in a new Cursor Agent chat (desktop)

```
You are setting up this Windows desktop for PPE IDE BUILD only (zero API spend).
The Hyper-V VM runs the operator loop — NOT this machine.

Read and follow ONLY:
@docs/SOP/PPE_VM_DESKTOP_OPERATOR_HANDOFF.md
@docs/SOP/DESKTOP_OPERATOR_SETUP_STARTER.md
@docs/SOP/OPERATOR_BUTTON_MAP.md

Walk me one step at a time. Run verification commands yourself. Stop after each step until I confirm.
Do NOT start the loop, run_ppe_auto_local_loop, or install PPE Desktop Operator logon tasks on this PC.
Do NOT copy ppe_operator_loop_host.local.cmd to the desktop.
```

---

## Agent rules

| Do | Do not |
|----|--------|
| Run **`setup_desktop_ide_only.cmd`** | Install loop-host token on desktop |
| Verify `ppe_operator_no_loop.local.cmd` exists | `run_ppe_auto_local_loop.cmd` / headless stack on desktop |
| Install shortcuts via `setup_desktop_shortcuts.cmd` | `PPE Desktop Operator` scheduled task |
| Use **DESKTOP BUILD / CONTINUE / STOP** | `DESKTOP_AUTO` unless operator explicitly opts in |

**Three devices:** VM = loop host · desktop = IDE BUILD · phone = ntfy + SSH triage.

---

## Prerequisite: repo has operator files

From repo root, agent checks:

```bat
dir DESKTOP_BUILD.cmd
dir setup_desktop_ide_only.cmd
dir scripts\ppe_notify_push.py
```

If missing: `git pull origin main`.

---

## Step-by-step checklist (agent-led)

### A — Repo and Python

- [ ] `git pull` — desktop clone is current
- [ ] Python 3.11+ available: `python --version`
- [ ] Venv (if none): `python -m venv .venv` then `.venv\Scripts\activate`
- [ ] `pip install -r requirements.txt`
- [ ] `python scripts\ppe_operator_env.py` exits 0

### B — Desktop power

- [ ] Windows **Settings → Power**: plugged in → **Sleep: Never** (display off OK)

### C — Phone push (ntfy)

Operator does on **phone**: install ntfy app, subscribe to a **private** topic.

On **desktop**:

```bat
copy ppe_operator_notify.local.cmd.example ppe_operator_notify.local.cmd
python scripts\bootstrap_operator_notify_secret.py
```

Edit `PPE_NTFY_TOPIC=` to match phone subscription.

Verify:

```bat
python scripts\ppe_notify_push.py --check
python scripts\ppe_notify_push.py --title "PPE test" --body "desktop ready"
```

Operator confirms notification on phone.

### D — Private access (Tailscale + SSH)

- [ ] Tailscale installed on desktop, laptop, phone (same account)
- [ ] OpenSSH Server enabled on desktop (Windows Optional feature)
- [ ] Operator can SSH from phone (Termius/Blink) to desktop Tailscale hostname

Agent: help troubleshoot only if operator is on this step.

### E — Start the stack

```bat
run_ppe_desktop_operator.cmd
```

Propagates the chapter queue, checks whether loop + watch are running, starts them if not, prints verdict.

Two terminals should open: **PPE auto loop** and **PPE mobile watch**.

Verify loop:

```bat
run_ppe_operator.cmd --brief
```

Expected when healthy: `VERDICT=RUN_AUTO` or `VERDICT=SUPPLY_LOW` (idle queue).

### F — Auto-start at logon

```bat
install_ppe_desktop_operator_task.cmd
```

Registers Task Scheduler → at logon → `run_ppe_desktop_operator.cmd`.

### G — Git commits + push from desktop

Closeout slices commit `docs/SOP/` on this machine. Use gitignored env (no global git config required):

```bat
copy ppe_operator_git.local.cmd.example ppe_operator_git.local.cmd
```

Set `GIT_AUTHOR_NAME` / `GIT_AUTHOR_EMAIL` (match your GitHub noreply or primary email).

For **push** and promotion-recovery PRs, log in once:

```bat
gh auth login -h github.com -p https -w
```

Opens a browser on the desktop — or copy the device code URL to your phone/laptop browser.

Verify everything:

```bat
setup_desktop_operator.cmd
```

### H — Permissions: Cursor vs unattended loop

| Context | Who approves | Phone can help? |
|---------|--------------|-----------------|
| **Unattended loop** (`run_ppe_auto_local_loop.cmd`) | Nobody — Python/cmd only | SSH triage only (`run_ppe_operator.cmd`, restart stack) |
| **Cursor Agent on desktop** | You, in Cursor on the desktop | **No** — smart-mode blocks are IDE-only |
| **Windows UAC** (OpenSSH install, etc.) | You, on the desktop (one-time) | No |
| **`gh auth login`** | You, any browser (device code) | **Yes** — paste URL/code from SSH session |

The loop does **not** use Cursor. Once G is done, routine chapters need no Cursor permission prompts.

### I — Remote Desktop (Cursor from phone)

Run **once as Administrator** on the desktop:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\enable_rdp_tailscale.ps1
```

On phone: install **Microsoft Remote Desktop** → PC name `desktop-ge39o15`, user `USER`, Windows password.

When ntfy fires for `IDE_BUILD` / `ERROR`: RDP → Cursor Agent on desktop (you do not code by hand).

### J — Auto git sync (no manual pull from phone)

Enabled in [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) (`gitSync`). Each loop pass pulls `main`; closeout pushes + opens PR automatically.

Verify:

```bat
python scripts\ppe_operator_git_sync.py --pull
```

---

## When loop stops (desktop / phone)

| Verdict | Phone SSH (Termius) | Desktop | VM loop |
|---------|---------------------|---------|---------|
| `IDE_BUILD` | Read guard report | **DESKTOP BUILD** | waits |
| `RUN_LOCAL` | — | — | auto `run_ppe_local` |
| `STACK_DOWN` | — | — | **VM_RESTART** |
| Loop died on VM | `VM_STATUS` / `VM_RESTART` | — | — |

Phone triage (VM):

```bat
ppe_autobuilder.cmd status --brief
type artifacts\orchestrator\OPERATOR_GUARD_REPORT.md
```

---

## Git sync between machines

```
Desktop Cursor BUILD → push → GitHub → VM auto-pulls on loop pass
After merge → DESKTOP CONTINUE (finish on VM)
```

**VM** is the loop host; **desktop** is IDE BUILD only. See [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md).

---

## Related

- [`SECURITY_OPERATOR_CHECKLIST_V1.md`](../DEPLOY/SECURITY_OPERATOR_CHECKLIST_V1.md) — ntfy topic setup, VPS smoke, Phase B TLS
- [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)
- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md)
- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
