# PPE operator layout — VM loop host + desktop IDE BUILD ADR

**Status:** Accepted (2026-06-17)  
**Supersedes:** Desktop-as-primary-loop-host (pre–Hyper-V VM cutover)  
**Canon:** [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md) · [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) · [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md)

---

## Context

The PPE near-zero-API operator runs a 24/7 relay loop (control slices, `run_ppe_local`, ntfy) and pauses on **product** slices for **IDE BUILD** in Cursor. Before June 2026 the **daily Windows desktop** was the loop host. That caused:

- `cmd.exe` popup storms (headless loop + logon scheduled tasks on the wrong machine)
- Confusion between `run_ppe_local` and IDE BUILD
- Copy-paste / Win+R operator friction

A dedicated **Hyper-V VM** now runs the loop headlessly; the **daily PC** runs Cursor only.

---

## Decisions

### 1. Machine roles (hard)

| Machine | Role | Loop / stack | Gitignored token |
|---------|------|--------------|------------------|
| **Hyper-V VM** (`PPE-Loop-Host`) | 24/7 operator relay | **Allowed** — headless stack | `ppe_operator_loop_host.local.cmd` → `PPE_LOOP_HOST=1`, `PPE_STACK_HEADLESS=1` |
| **Daily desktop** | Cursor IDE BUILD | **Forbidden** | `ppe_operator_no_loop.local.cmd` → `PPE_STACK_FORBIDDEN=1` |
| **Phone** | ntfy + SSH triage | — | — |

**Forbidden:** running `run_ppe_headless_stack`, `run_ppe_auto_local_loop`, or `start_ppe_desktop_operator` on the daily desktop while the VM is live.

### 2. Headless stack only on loop host

| Item | Decision |
|------|----------|
| Stack mode | **`desktopStack.mode: headless`** or `PPE_STACK_HEADLESS=1` on VM |
| Supervisor | One detached supervisor; workers log under `artifacts/orchestrator/HEADLESS_STACK_*.log` |
| Popups | Loop entry via `ppe_headless_auto_loop_entry.py` — no `cmd /c` loop storms |
| Daily PC | Stack **stopped**; `ppe_loop_host_guard.py` exits **8** if loop host token missing or `PPE_STACK_FORBIDDEN=1` |

### 3. Scheduled tasks

| Task | VM | Daily desktop |
|------|----|---------------|
| **PPE Headless Stack** (logon → `run_ppe_headless_stack.cmd --ensure`) | **Yes** — `install_ppe_vm_headless_logon_task.cmd` | **No** |
| **PPE VM Watchdog** (every 10m → `VM_WATCHDOG.cmd --quiet`) | **Yes** — optional but installed | **No** |
| **PPE Desktop Operator** / **PPE Desktop Operator Watchdog** | **No** | **Removed** — legacy |
| **DESKTOP AUTO** | **No** | **Opt-in only** — `ppe_operator_desktop_auto.local.cmd`; default **off** |

### 4. IDE BUILD vs relay continue

| Step | Where | Action |
|------|--------|--------|
| Loop blocks on product | VM (automatic) | `VERDICT=IDE_BUILD` |
| Implement slice | **Desktop Cursor** | `DESKTOP_BUILD.cmd` or starter `@` file |
| After merge | Desktop | `DESKTOP_CONTINUE.cmd` (SSH finish on VM) |
| Continue relay | **VM** (automatic) | `run_ppe_local` / loop — **not** on desktop |

**Policy:** `run_ppe_local.cmd` does **not** implement product code; it advances relay after `mark_ide_product_ready`.

### 5. Operator UX

| Policy | Detail |
|--------|--------|
| **No Win+R one-liners** for ops | Double-click `VM_*.cmd` / `DESKTOP_*.cmd` |
| **Recovery on VM** | `VM_STOP` → wait → `VM_RESTART` once; `fix_vm_operator.cmd` (= `vm_bootstrap --recover`) |
| **One-shot bootstrap** | `bootstrap_operator_pair.cmd` (desktop + SSH VM) |
| **Phone ntfy** | Messages include button hints (`scripts/ppe_operator_hint.py`) |

### 6. Git hygiene on loop host

| Policy | Detail |
|--------|--------|
| Pull branch | VM stays on `main`; `git pull --ff-only` each loop pass when clean |
| Dirty exempt paths | `.cursor/IDE_BUILD_TRIGGER.json` and other preflight-exempt paths do **not** block pull |
| Bootstrap heal | `ppe_vm_bootstrap.py` resets transient trigger file; heals stale relay `staged_for_worker` |

### 7. IDE on VM (deferred)

Cursor on the VM via Remote-SSH is **documented** ([`PPE_CURSOR_REMOTE_SSH_V1.md`](PPE_CURSOR_REMOTE_SSH_V1.md)) but **not** the default layout. Default remains **desktop BUILD + VM loop**.

---

## Consequences

- Steward / agent docs must not describe the desktop as the primary loop host.
- New operator automation must target the **VM** for loop/watch/ntfy and the **desktop** for IDE BUILD handoff only.
- `DESKTOP_OPERATOR_SETUP_STARTER.md` is **IDE-BUILD setup**; loop host setup is [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md).
- Layer-audit warnings on root `VM_*.cmd` / `DESKTOP_*.cmd` are accepted control-plane operator surface.

---

## Open / verify later

| Item | Notes |
|------|--------|
| VM reboot smoke | Confirm logon task after next VM reboot |
| Hyper-V `clean-base` checkpoint | Host operator — not automated in repo |
| Cursor Automation | Optional zero-click BUILD — [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md) |

**Ops tracker:** [`OPERATOR_OPS_QUEUE.md`](OPERATOR_OPS_QUEUE.md)
