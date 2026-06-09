# Desktop operator setup — Cursor Agent starter

**Plane:** CONTROL-PLANE only. **Machine:** always-on Windows **desktop** (loop host).

**Purpose:** one Agent thread on the desktop walks the operator through bootstrap — no copy-paste from laptop chat.

**Canonical runbook:** [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)

---

## What to paste in a new Cursor Agent chat (desktop)

```
You are setting up this Windows desktop as the PPE loop host (zero API spend).

Read and follow ONLY:
@docs/SOP/DESKTOP_OPERATOR_SETUP_STARTER.md
@docs/SOP/PPE_MOBILE_OPERATOR_V1.md

Walk me one step at a time. Run verification commands yourself. Stop after each step until I confirm.
Do NOT start ACP, run_ppe_auto_acp_loop, or steward charter.
Do NOT do product IDE BUILD on this machine unless I ask — laptop handles BUILD; desktop runs the loop.
```

---

## Agent rules

| Do | Do not |
|----|--------|
| Run commands in **this repo root** on the desktop | Product slice implementation unless operator asks |
| Verify each step before the next | `run_ppe_auto_acp_loop.cmd` / API relay |
| Create `ppe_operator_notify.local.cmd` from example (gitignored) | Commit secrets or `ppe_operator_notify.local.cmd` |
| Create `ppe_operator_git.local.cmd` from example (gitignored) | Commit secrets or `ppe_operator_git.local.cmd` |
| Use local profile only | Paste laptop chat history |

**Three devices:** desktop = loop host · phone = ntfy + SSH triage · laptop = Cursor BUILD.

---

## Prerequisite: repo has mobile operator files

From repo root, agent checks:

```bat
dir start_ppe_desktop_operator.cmd
dir scripts\ppe_notify_push.py
dir watch_operator_mobile.cmd
```

If missing: `git pull origin main` (after mobile-operator PR merged) or ask operator which branch to checkout.

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
start_ppe_desktop_operator.cmd
```

Two terminals should open: **PPE auto loop** and **PPE mobile watch**.

Verify loop:

```bat
run_ppe_operator.cmd --brief
```

Expected when healthy: `VERDICT=RUN_AUTO` or `VERDICT=SUPPLY_LOW` (idle queue).

### F — Optional: auto-start at logon

Task Scheduler → At logon → `cmd.exe /c "…\start_ppe_desktop_operator.cmd"` with **Start in** = repo root.

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

| Verdict | Phone SSH (Termius) | Phone RDP + Cursor | Loop auto |
|---------|---------------------|--------------------|-----------|
| `IDE_BUILD` | Read `OPERATOR_GUARD_REPORT.md` | Agent BUILD on desktop | `git pull` each pass |
| `RUN_LOCAL` | `run_ppe_local.cmd` | — | pull + publish |
| `SUPPLY_LOW` | Nothing — idle | — | — |
| Loop died | `start_ppe_desktop_operator.cmd` | — | — |

Phone triage commands:

```bat
run_ppe_operator.cmd --brief
type artifacts\orchestrator\OPERATOR_GUARD_REPORT.md
```

---

## Git sync between laptop and desktop

```
Any machine (Cursor BUILD) → push → GitHub → desktop loop auto-pulls each pass
Closeout on desktop → auto-push + PR (no manual phone git)
```

Desktop is the **primary** loop host and recommended Cursor Agent machine. Laptop remains optional.

---

## Related

- [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)
- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md)
- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
