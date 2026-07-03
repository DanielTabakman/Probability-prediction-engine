# PPE mobile operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run the auto-loop on an always-on desktop; monitor and triage from phone.

**Layout (Hyper-V VM):** see [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md). **VM = loop** · **Desktop = IDE BUILD**.

Cross-refs: [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) · [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md)

---

## Roles (three devices)

| Device | Tools | Job |
|--------|-------|-----|
| **VM** (Hyper-V, always on) | Headless loop + ntfy listen | **Loop host** — relay, control slices, `run_ppe_local` |
| **Desktop** (daily PC) | Cursor | **IDE BUILD only** — `DESKTOP_BUILD.cmd`, no loop |
| **Phone** | **ntfy** + **Termius** | Alerts with button hints; SSH triage to VM |

**You do not code by hand.** When something needs judgment, open **Cursor Agent** on the desktop (locally or via phone RDP).

---

## One-time setup

### 1. Desktop power

Windows → Power → **Never sleep** when plugged in (display may turn off).

### 2. ntfy (phone push)

1. Install [ntfy app](https://ntfy.sh) on your phone.
2. Subscribe to a **private topic**.
3. Copy `ppe_operator_notify.local.cmd.example` → `ppe_operator_notify.local.cmd`
4. Set `PPE_NTFY_TOPIC` (gitignored).

Verify:

```bat
python scripts\ppe_notify_push.py --check
python scripts\ppe_notify_push.py --title "PPE test" --body "desktop ready"
```

### 3. Tailscale (private access)

Install Tailscale on **desktop**, **laptop**, and **phone**. No public ports on your router.

### 4. OpenSSH on desktop (Termius triage)

Windows → Optional features → **OpenSSH Server**.

```text
ssh USER@desktop-ge39o15
```

### 5. Remote Desktop on desktop (Cursor from phone)

Run **once as Administrator** on the desktop:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\enable_rdp_tailscale.ps1
```

On your phone, install **Microsoft Remote Desktop** (not Termius):

| Field | Value |
|-------|-------|
| PC name | `desktop-ge39o15` |
| User | `USER` |
| Password | Windows login password |

Use Tailscale hostname only — do not expose port 3389 on your router.

### 6. Git identity + GitHub CLI

```bat
copy ppe_operator_git.local.cmd.example ppe_operator_git.local.cmd
gh auth login -h github.com -p https -w
setup_desktop_operator.cmd
```

---

## Auto git sync (loop host)

Configured in [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) → `gitSync`:

| Setting | Default | Behavior |
|---------|---------|----------|
| `pullEachPass` | true | Each loop pass: `git fetch` + `git pull --ff-only origin main` |
| `publishEachPass` | true | Push unpushed commits on feature branches + open PR |
| `mergeEachPass` | true | Label loop PRs `automerge` and squash-merge when CI is green |
| `pushAfterCommit` | true | After closeout / `run_ppe_local` success: push + open PR |
| `openPrOnPush` | true | `gh pr create` when publishing from `main` |

Disable: `set PPE_GIT_SYNC=0`, `set PPE_GIT_SYNC_PULL=0`, or `set PPE_GIT_SYNC_MERGE=0`.

**You do not manually `git pull` from the phone** — the loop pulls laptop/desktop pushes automatically.

---

## Daily start

### VM (loop host)

```bat
VM_RESTART.cmd
REM or after one-time install: logon task starts stack automatically
VM_STATUS.cmd
```

### Desktop (IDE BUILD only — no loop)

```bat
REM one-time:
setup_desktop_ide_only.cmd
REM when ntfy says IDE_BUILD:
DESKTOP_BUILD.cmd
```

**Legacy (no VM):** `run_ppe_desktop_operator.cmd` / `start_ppe_desktop_operator.cmd` — deprecated when Hyper-V VM is live.

---

## Phone workflow when ntfy fires

### Quick triage (Termius → VM)

```bat
cd C:\Users\ppeloop\Probability-prediction-engine
ppe_autobuilder.cmd status --brief
type artifacts\orchestrator\OPERATOR_GUARD_REPORT.md
```

### IDE BUILD (desktop Cursor — default)

1. On **daily PC**: double-click **DESKTOP BUILD** (or open starter in Cursor)
2. Gate → commit → PR → **DESKTOP CONTINUE** after merge
3. VM loop continues relay automatically

### Verdict matrix

Full table: [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md) · agent routing: [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md)

| Verdict | Phone | Desktop | VM loop |
|---------|-------|---------|---------|
| `SUPPLY_LOW` | Nothing | — | idle |
| `RUN_AUTO` / `RUN_LOCAL` | — | — | auto relay |
| `IDE_BUILD` | Read hint | **DESKTOP BUILD** | waits |
| `ERROR` / `STALE_STATE` | SSH triage | steward chat | `fix_vm_operator.cmd` |
| `STACK_DOWN` | — | — | **VM_RESTART** |

Restart stack from phone (SSH to **VM**):

```bat
VM_RESTART.cmd
```

### Remote commands (ntfy app — no SSH)

When `watch_ntfy_commands.cmd` is running on the **VM** (started by headless stack), publish a message **to your ntfy topic** from the phone app:

| Message | What happens |
|---------|----------------|
| **`build`** | **Primary workflow.** When verdict is `IDE_BUILD`, starts Cursor Agent on the queued product slice (gate → commit → mark ready → `run_ppe_local`). When verdict is `RUN_LOCAL`, runs `run_ppe_local.cmd` on the desktop. |
| `build <note>` | Same as `build`, with extra context in the agent prompt |
| `restart` | Stops loop + watch, restarts the stack |
| `fix` | Investigates the current blocker — headless CLI when allowed, otherwise **IDE handoff** (`IDE_FIX_NOW.md` + continuity brief) |
| `fix <note>` | Same as `fix`, with extra context |
| `status` | VM replies on ntfy with loop/watch state + operator brief |
| `help` | Lists commands (no secret prefix required) |

**Typical phone workflow:** ntfy alert says `IDE_BUILD` → open ntfy → send **`my-secret build`** (prefix with `PPE_NTFY_CMD_SECRET`). **`status`** also needs the secret prefix when a secret is set. **`help`** works without the prefix.

**Fully automatic (default):** when `autoRemoteBuild` is true in [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) (or `PPE_AUTO_REMOTE_BUILD=1`), the **loop** and **mobile watch** start the desktop **agent CLI** on `IDE_BUILD` without a phone tap. Phone `build` remains a manual override. Disable: `set PPE_AUTO_REMOTE_BUILD=0`.

Set `PPE_NTFY_CMD_SECRET` in `ppe_operator_notify.local.cmd` (required for every command except `help`):

```text
my-secret build
my-secret fix can you fix it if so please do
```

**Agent command contract:** `build` and `fix` always try headless CLI when allowed (`autoRemoteBuild`, usage available, `preferIdeOverCli` off). Otherwise they **IDE handoff** — open Cursor, copy prompt, ntfy ping — same near-zero-API path as loop exit 7.

The headless path uses the `agent` CLI when installed, otherwise `cursor-sdk` with `CURSOR_API_KEY`. One-time desktop setup:

```bat
setup_cursor_agent.cmd
agent login
verify_cursor_agent.cmd
```

Progress logs: `artifacts/orchestrator/REMOTE_BUILD_AGENT.log` (build) or `REMOTE_FIX_AGENT.log` (fix). IDE handoff shortcuts: `IDE_BUILD_NOW.md` / `IDE_FIX_NOW.md`. You get ntfy pings when build/fix starts, handoffs, or finishes.

Disable remote commands: `set PPE_NTFY_CMD_ENABLED=0` in `ppe_operator_notify.local.cmd`.

---

## How alerts work

| Trigger | Channel |
|---------|---------|
| Loop guard stop (exit 7) | **ntfy** |
| Verdict change while watch runs | **ntfy** |
| Loop process died | **ntfy** (title: **PPE loop stopped**) |
| Stack started (logon / `run_ppe_desktop_operator.cmd`) | **ntfy** (title: **PPE OK — …**) |
| Every 6h while loop running | **ntfy** heartbeat (title: **PPE OK - …**, low priority) |
| Relay slice completes | **ntfy** (title: **PPE slice done: …**) |
| Chapter closeout completes | **ntfy** (title: **PPE chapter done: …**, includes next chapter if known) |
| Cursor Agent starts fixing a block | **ntfy** (title: **PPE fixing: …**) — agent runs `ppe_notify_fix.py --working` |
| Cursor Agent finishes a fix | **ntfy** (title: **PPE fixed (VERDICT): …** or **PPE fix done: …**) — agent runs `ppe_notify_fix.py --resolved` |
| Stuck verdict clears (watch poll) | **ntfy** (title: **PPE fixed: RUN_AUTO** / **RUN_LOCAL** — includes prior blocker) |
| Monday weekly digest (`weekly_digest_monday.cmd`) | **ntfy** (title: **This week in PPE - …**) |

Disable progress pings: `set PPE_NTFY_PROGRESS=0` in `ppe_operator_notify.local.cmd`.

**Phone check without SSH:** open the **ntfy** app → your topic. Recent **PPE OK** = running. **PPE loop stopped** = needs a reboot or desktop fix. **IDE_BUILD** / **ERROR** = needs you.

Optional: set `PPE_NTFY_HEARTBEAT_HOURS=4` in `ppe_operator_notify.local.cmd` for more frequent OK pings.

---

## Task Scheduler at logon (recommended)

Register once from repo root:

```bat
install_ppe_desktop_operator_task.cmd
```

Runs `run_ppe_desktop_operator.cmd` at user logon (git pull, queue propagate, start stack if missing).

Manual Task Scheduler fields:

| Field | Value |
|-------|--------|
| Program | `cmd.exe` |
| Arguments | `/c "…\run_ppe_desktop_operator.cmd"` |
| Start in | repo root |

---

## Environment variables

| Variable | Required | Default |
|----------|----------|---------|
| `PPE_NTFY_TOPIC` | Yes for mobile push | — |
| `PPE_NTFY_SERVER` | No | `https://ntfy.sh` |
| `PPE_NTFY_CMD_ENABLED` | No | enabled; `0` disables phone commands |
| `PPE_NTFY_CMD_SECRET` | **Yes** for phone commands (except `help`) | long random string — prefix every command, e.g. `my-secret build` |
| `PPE_NOTIFY` | No | enabled; `0` disables |
| `PPE_WEEKLY_DIGEST_TOAST` | No | enabled; `0` skips Windows toast (phone push still uses ntfy) |
| `PPE_NTFY_HEARTBEAT_HOURS` | No | `6` — OK ping interval while loop running; `0` disables |
| `PPE_NTFY_STUCK_HOURS` | No | `8` — re-alert while verdict is FIX_PLAN / IDE_BUILD / ERROR |
| `PPE_NTFY_QUIET_HOURS` | No | `0`; `1` mutes routine alerts during quiet window |
| `PPE_NTFY_QUIET_START` / `PPE_NTFY_QUIET_END` | No | `01:00` / `08:00` local — one stuck ping allowed per night |
| `PPE_NTFY_MORNING_REPORT` | No | `1` — 8am digest when watch is running |
| `PPE_NTFY_MORNING_REPORT_AT` | No | `08:00` local |
| `PPE_NTFY_CMD_POLL_SEC` | No | `30` — phone command poll interval |
| `PPE_GIT_SYNC` | No | enabled |
| `PPE_GIT_SYNC_PULL` | No | enabled |
| `PPE_GIT_SYNC_PUSH` | No | enabled |

---

## Related

- [`SECURITY_OPERATOR_CHECKLIST_V1.md`](../DEPLOY/SECURITY_OPERATOR_CHECKLIST_V1.md) — ntfy secret, VPS smoke, Phase B TLS
- [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md)
- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
