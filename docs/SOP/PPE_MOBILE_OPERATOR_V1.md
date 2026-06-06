# PPE mobile operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run the auto-loop on an always-on desktop; monitor and triage from phone.

Cross-refs: [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) · [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

---

## Roles

| Device | Job |
|--------|-----|
| **Desktop** (plugged in, never sleeps) | `run_ppe_auto_local_loop.cmd` + mobile watch |
| **Phone** | ntfy alerts + SSH status checks |
| **Laptop** | Cursor IDE BUILD when verdict is `IDE_BUILD` |

---

## One-time setup

### 1. Desktop power

Windows → Power → **Never sleep** when plugged in (display may turn off).

### 2. ntfy (phone push)

1. Install [ntfy app](https://ntfy.sh) on your phone.
2. Subscribe to a **private topic** (long random string, e.g. `ppe-msos-abc123xyz`).
3. Copy `ppe_operator_notify.local.cmd.example` → `ppe_operator_notify.local.cmd`
4. Set `PPE_NTFY_TOPIC` to that topic (file is gitignored).

Verify:

```bat
python scripts\ppe_notify_push.py --check
python scripts\ppe_notify_push.py --title "PPE test" --body "desktop ready"
```

Disable all notifications: `set PPE_NOTIFY=0`.

### 3. Tailscale (private access)

Install Tailscale on **desktop**, **laptop**, and **phone**. No public SSH ports on your router.

### 4. OpenSSH on desktop

Windows Settings → Apps → Optional features → **OpenSSH Server**.

Phone/laptop connect: `ssh youruser@<desktop-tailscale-name>`

---

## Daily start (desktop)

One command opens two terminals (loop + watch):

```bat
start_ppe_desktop_operator.cmd
```

Or manually:

```bat
run_ppe_auto_local_loop.cmd
watch_operator_mobile.cmd
```

---

## Phone triage

When ntfy alerts fire, SSH to the desktop and run:

```bat
run_ppe_operator.cmd --brief
type artifacts\orchestrator\OPERATOR_GUARD_REPORT.md
type artifacts\orchestrator\LAST_RUN_REPORT.md
```

| Verdict | Phone can | Needs laptop Cursor |
|---------|-----------|---------------------|
| `RUN_AUTO` | Watch — loop handles it | — |
| `RUN_LOCAL` | `run_ppe_local.cmd` (if marker set) | — |
| `IDE_BUILD` | Read reports | Agent BUILD + commit + `mark_ide_product_ready.cmd` |
| `SUPPLY_LOW` | Wait (loop idles) | Add backlog rows when ready |
| `STALE_STATE` / `ERROR` | Read reports; restart loop if crashed | Fix root cause |

Restart stack from phone:

```bat
start_ppe_desktop_operator.cmd
```

---

## How alerts work

| Trigger | Channel |
|---------|---------|
| Loop guard stop (exit 7) | Windows toast + **ntfy** (`run_ppe_auto_loop.cmd` → `--notify`) |
| Verdict change while watch runs | **ntfy** (`watch_operator_mobile.cmd`) |
| Loop process died | **ntfy** (watch detects missing `run_ppe_auto_loop`) |

Watch state: `artifacts/control_plane/MOBILE_WATCH_STATE.json` (gitignored with `artifacts/`).

---

## Optional: Task Scheduler at logon

| Field | Value |
|-------|--------|
| Program | `cmd.exe` |
| Arguments | `/c "D:\path\to\Probability prediction engine\start_ppe_desktop_operator.cmd"` |
| Start in | repo root |

---

## Environment variables

| Variable | Required | Default |
|----------|----------|---------|
| `PPE_NTFY_TOPIC` | Yes for mobile push | — |
| `PPE_NTFY_SERVER` | No | `https://ntfy.sh` |
| `PPE_NTFY_TOKEN` | No | — (auth for private server) |
| `PPE_NOTIFY` | No | enabled; set `0` to disable |

---

## Related

- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
