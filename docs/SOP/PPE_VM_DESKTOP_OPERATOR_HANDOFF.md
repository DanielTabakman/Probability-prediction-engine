# PPE VM + desktop operator — session handoff (2026-06)

**Plane:** CONTROL-PLANE · **Status:** canonical operator layout after Hyper-V VM cutover

**Policy (accepted):** [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md)

Use this doc when opening a **new Cursor thread** after VM/desktop operator work. Companion quick ref: [`VM_OPERATOR_README.txt`](../../VM_OPERATOR_README.txt) (repo root).

---

## Current layout (two machines)

| Machine | Path | Role | Loop |
|---------|------|------|------|
| **Daily PC** | `C:\Users\USER\Desktop\Probability-prediction-engine` | Cursor IDE BUILD, steward chat | **Off** (`ppe_operator_no_loop.local.cmd` → `PPE_STACK_FORBIDDEN=1`) |
| **Hyper-V VM** (`ppeloop@DESKTOP-CAQLL8K`) | `C:\Users\ppeloop\Probability-prediction-engine` | Headless operator 24/7 | **On** (`ppe_operator_loop_host.local.cmd` → `PPE_LOOP_HOST=1` + `PPE_STACK_HEADLESS=1`) |

**Do not** install `PPE Desktop Operator` scheduled task on the daily PC. **Do not** copy `ppe_operator_loop_host.local.cmd` to the desktop.

---

## VM operator — double-click only (no Win+R paste)

| Script | Purpose |
|--------|---------|
| `VM_UPDATE.cmd` | `git pull origin main` |
| `VM_STOP.cmd` | Emergency stop + kill stray workers |
| `VM_STATUS.cmd` | Health check (**wait ~10s** for `PHASE=` line) |
| `VM_START.cmd` | Start loop once (after STOP) |
| `VM_RESTART.cmd` | STOP → wait 30s → START (preferred) |
| `VM_AUTO.cmd` | Alias for VM_RESTART |
| `VM_WATCHDOG.cmd` | Rate-limited auto-restart if stack down (optional scheduled task) |
| `install_ppe_vm_headless_logon_task.cmd` | One-time logon auto-start (Phase 6) |

Desktop shortcuts: run `setup_operator_shortcuts.cmd` once (or auto from **DESKTOP_BUILD** / **VM_UPDATE**).

**Remote triage from daily PC:** `ssh ppeloop@desktop-caqll8k` — see [`PPE_CURSOR_REMOTE_SSH_V1.md`](PPE_CURSOR_REMOTE_SSH_V1.md).

---

## Healthy VM status (example)

```text
PHASE=RUN_LOCAL_PENDING VERDICT=RUN_LOCAL stack_loop=True stack_watch=True next=run-local
```

| Reading | Meaning |
|---------|---------|
| `stack_loop=True` / `stack_watch=True` | Headless stack OK |
| `VERDICT=IDE_BUILD` | Product slice needs **Cursor BUILD on desktop** → `DESKTOP_BUILD.cmd` |
| `VERDICT=RUN_LOCAL` | Relay continuing on VM after product merge |
| `PHASE=STACK_DOWN` + `stack_loop=False` | Loop off → double-click **VM_RESTART** on VM |
| `next=handoff` | Waiting for IDE work, not `run_ppe_local` yet |

**Active chapter:** `msos_user_state_v1` — check `ppe_autobuilder.cmd status --brief` for current slice.

---

## IDE BUILD vs `ppe_go.cmd` vs `run_ppe_local.cmd`

**Common confusion:** `run_ppe_local.cmd` does **not** implement the product slice. It continues the relay **after** IDE BUILD is done.

| Step | Where | Command / action |
|------|--------|------------------|
| 1. Operator blocks on product | VM loop (automatic) | `VERDICT=IDE_BUILD` in status |
| 2. Start BUILD | **Real PC** | Double-click **`DESKTOP BUILD`** — copies prompt to clipboard, opens starter |
| 3. Paste in Agent | **Real PC Cursor** | New Agent chat → **Ctrl+V** → Enter |
| 4. Agent closeout | **Real PC** | Gate → commit → `mark_ide_product_ready` (agent runs this) |
| 5. After PR merge | **Real PC** | **`DESKTOP CONTINUE`** |
| 6. Continue relay | **VM** (automatic) | Loop runs `run_ppe_local` — no VM action needed |

**Phone ntfy** messages include button hints — see [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md).

---

## Incidents fixed this session (code + ops)

| Issue | Root cause | Fix |
|-------|------------|-----|
| Popup cmd storm (VM) | Headless loop spawned `cmd /c` windows; repeated START | `ppe_headless_auto_loop_entry.py`, `CREATE_NO_WINDOW`, `VM_STOP` / `VM_RESTART` |
| Popups on daily PC | `PPE Desktop Operator` logon task + `PPE_LOOP_HOST=1` on desktop | `DESKTOP_STOP.cmd`, `ppe_operator_no_loop.local.cmd`, removed logon task |
| `Windows can't find set` | Pasted `set "..."` into Win+R | Use double-click scripts only |
| Status window closes | `VM_STATUS` had no pause; `PHASE=` takes ~10s | `VM_STATUS.cmd` wait + `pause` |
| Empty `PPE_STACK_HEADLESS` | Stale `ppe_operator_loop_host.local.cmd` on VM | Refresh from `.example` on START/RESTART |
| Copy-paste fatigue | Too many one-liners | `VM_*.cmd` + Desktop shortcuts + this doc |

**Merged PRs (representative):** #181 headless popup fix, #186 double-click VM scripts, #187 VM_UPDATE, #189 VM_RESTART, #191 VM_STATUS pause.

---

## Procedure docs to prefer going forward

1. [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md) — VM sizing, clone, loop-host token
2. [`PPE_HEADLESS_STACK_V1.md`](PPE_HEADLESS_STACK_V1.md) — headless supervisor model
3. [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) — IDE-native relay, `ppe_go`, director agents
4. [`VM_OPERATOR_README.txt`](../../VM_OPERATOR_README.txt) — one-page VM operator card
5. [`PPE_OPERATOR_PROCESS_V1.md`](PPE_OPERATOR_PROCESS_V1.md) — daily operator process + incident playbook
6. [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) — symptom → which `.cmd` on which machine
7. [`OPERATOR_OPS_QUEUE.md`](OPERATOR_OPS_QUEUE.md) — remaining host-only tasks

---

## New thread starter (desktop steward)

```text
Load @docs/SOP/PPE_VM_DESKTOP_OPERATOR_HANDOFF.md and @docs/SOP/AGENT_CONTINUITY_BRIEF.md.
VM loop host: ppeloop@DESKTOP-CAQLL8K. Desktop is IDE BUILD only.
Continue MSOS live sequence from operator status; do not restart VM loop unless STACK_DOWN.
```

---

## Operator checklist (daily)

- [ ] VM: **VM_STATUS** → `stack_loop=True`
- [ ] Desktop: no operator popups; **no** auto-loop
- [ ] If `IDE_BUILD`: BUILD in Cursor on desktop, then mark ready + `run_ppe_local` on VM
- [ ] If `STACK_DOWN` on VM: **VM_RESTART** once (not repeatedly)
