# PPE mobile operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run the auto-loop on an always-on desktop; monitor and triage from phone.

**New desktop?** [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md)

Cross-refs: [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) · [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

---

## Roles (three devices)

| Device | Tools | Job |
|--------|-------|-----|
| **Desktop** (plugged in, never sleeps) | Loop + **Cursor** + RDP host | Loop host; primary Agent machine; optional direct work |
| **Phone** | **ntfy** + **Termius** + **Microsoft Remote Desktop** | Alerts; quick SSH triage; full Cursor via RDP |
| **Laptop** | Cursor + Termius (optional) | Alternate BUILD machine if desktop unavailable |

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
| `pushAfterCommit` | true | After closeout / `run_ppe_local` success: push + open PR |
| `openPrOnPush` | true | `gh pr create` when publishing from `main` |

Disable: `set PPE_GIT_SYNC=0` or `set PPE_GIT_SYNC_PULL=0`.

**You do not manually `git pull` from the phone** — the loop pulls laptop/desktop pushes automatically.

---

## Daily start (desktop)

**One command** (git pull, propagate queue, ensure loop + watch, print verdict):

```bat
run_ppe_desktop_operator.cmd
```

Low-level (opens two cmd windows only — no queue/stack check):

```bat
start_ppe_desktop_operator.cmd
```

---

## Phone workflow when ntfy fires

### Quick triage (Termius)

```bat
cd C:\Users\USER\Desktop\Probability-prediction-engine
run_ppe_operator.cmd --brief
type artifacts\orchestrator\OPERATOR_GUARD_REPORT.md
```

### Fix with Cursor Agent (Microsoft Remote Desktop)

1. Open **Microsoft Remote Desktop** → connect to `desktop-ge39o15`
2. Open **Cursor** on the desktop
3. New Agent thread → load `artifacts/orchestrator/IDE_BUILD_STARTER_*.md` or `AGENT_CONTINUITY_BRIEF.md`
4. Agent implements / fixes; commit happens on desktop
5. Loop auto-pulls/pushes — or run `run_ppe_local.cmd` if verdict is `RUN_LOCAL`

### Verdict matrix

| Verdict | Phone (Termius) | Phone (RDP + Cursor) | Loop auto |
|---------|-----------------|----------------------|-----------|
| `SUPPLY_LOW` | Nothing — idle | — | — |
| `RUN_AUTO` | Watch | — | Runs relay |
| `RUN_LOCAL` | `run_ppe_local.cmd` | Agent if stuck | Pull + publish |
| `IDE_BUILD` | Send **`build`** on ntfy | **Cursor Agent BUILD** (or **`build`** from phone) | Pull after push |
| `ERROR` / `STALE_STATE` | Read reports; restart stack | Agent fix | — |

Restart stack from phone (Termius):

```bat
start_ppe_desktop_operator.cmd
```

### Remote commands (ntfy app — no SSH)

When `watch_ntfy_commands.cmd` is running (started automatically by `start_ppe_desktop_operator.cmd`), publish a message **to your ntfy topic** from the phone app:

| Message | What happens |
|---------|----------------|
| **`build`** | **Primary workflow.** When verdict is `IDE_BUILD`, starts Cursor Agent on the queued product slice (gate → commit → mark ready → `run_ppe_local`). When verdict is `RUN_LOCAL`, runs `run_ppe_local.cmd` on the desktop. |
| `build <note>` | Same as `build`, with extra context in the agent prompt |
| `restart` | Stops loop + watch, restarts the stack |
| `fix` | Starts Cursor Agent to investigate the current blocker (use when stuck, not for normal slice work) |
| `fix <note>` | Same as `fix`, with extra context |
| `status` | Desktop replies on ntfy with loop/watch state + operator brief |
| `help` | Lists commands |

**Typical phone workflow:** ntfy alert says `IDE_BUILD` → open ntfy → send **`build`**. No SSH, no RDP, no opening Cursor manually.

Optional shared secret (set `PPE_NTFY_CMD_SECRET` in `ppe_operator_notify.local.cmd`):

```text
my-secret build
my-secret fix can you fix it if so please do
```

The `build` / `fix` commands use the `agent` CLI when installed, otherwise `cursor-sdk` with `CURSOR_API_KEY`. One-time desktop setup:

```bat
setup_cursor_agent.cmd
agent login
verify_cursor_agent.cmd
```

Progress logs: `artifacts/orchestrator/REMOTE_BUILD_AGENT.log` (build) or `REMOTE_FIX_AGENT.log` (fix). You get ntfy pings when build/fix starts and finishes.

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
| `PPE_NTFY_CMD_SECRET` | No | optional shared secret prefix for commands |
| `PPE_NOTIFY` | No | enabled; `0` disables |
| `PPE_WEEKLY_DIGEST_TOAST` | No | enabled; `0` skips Windows toast (phone push still uses ntfy) |
| `PPE_NTFY_HEARTBEAT_HOURS` | No | `6` — OK ping interval while loop running |
| `PPE_NTFY_STUCK_HOURS` | No | `4` — re-alert while verdict is FIX_PLAN / IDE_BUILD / ERROR |
| `PPE_GIT_SYNC` | No | enabled |
| `PPE_GIT_SYNC_PULL` | No | enabled |
| `PPE_GIT_SYNC_PUSH` | No | enabled |

---

## Related

- [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md)
- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
