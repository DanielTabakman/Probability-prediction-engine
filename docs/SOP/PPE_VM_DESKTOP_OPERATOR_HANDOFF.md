# PPE VM + desktop operator — session handoff

**Plane:** CONTROL-PLANE · **Status:** canonical operator layout after Hyper-V VM cutover

**Policy (accepted):** [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md)  
**Verdict → command (SSOT):** [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md)  
**Human button lookup:** [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md)

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

**Remote publish (agents):** `vm_remote_publish.cmd` — commits staged `docs/SOP/*` on the VM and **loop-publishes** via `ops/loop-publish-*` + PR. **Do not** `git push origin main` over SSH (no TTY → credential hang; main is PR-only anyway). Use `DESKTOP_CONTINUE.cmd --no-pause` for non-interactive agent runs.

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

Current slice: `ppe_autobuilder.cmd status --brief` (do not hard-code chapter ids in docs).

---

## IDE BUILD flow (summary)

**`run_ppe_local.cmd` does not implement the product slice** — it continues the relay after IDE BUILD is done.

1. VM loop blocks → `VERDICT=IDE_BUILD`
2. Desktop → **`DESKTOP BUILD`** (clipboard prompt + starter)
3. Cursor Agent → gate → commit → `mark_ide_product_ready`
4. After PR merge → desktop **`DESKTOP CONTINUE`** (SSH → VM `finish_ide_build.cmd`)
5. VM loop advances automatically

Check **`Mode:`** in `OPERATOR_STATUS.md` — `CLOSEOUT_ONLY` means product on main; **do not re-BUILD** product.

Full step-by-step and forbidden commands: [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md). Human double-click steps: [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md).

---

## Procedure docs to prefer going forward

1. [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md) — verdict → command SSOT
2. [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md) — VM sizing, clone, loop-host token
3. [`PPE_HEADLESS_STACK_V1.md`](PPE_HEADLESS_STACK_V1.md) — headless supervisor model
4. [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) — IDE-native relay, `ppe_go`, director agents
5. [`VM_OPERATOR_README.txt`](../../VM_OPERATOR_README.txt) — one-page VM operator card
6. [`PPE_OPERATOR_PROCESS_V1.md`](PPE_OPERATOR_PROCESS_V1.md) — daily operator process + incident playbook
7. [`OPERATOR_OPS_QUEUE.md`](OPERATOR_OPS_QUEUE.md) — remaining host-only tasks

---

## New thread starters

Copy-paste from [`THREAD_STARTERS_V1.md`](THREAD_STARTERS_V1.md). Summary:

### Operator thread (relay + what's next)

```text
Operator thread. THREAD_ROLE: operator.
Load @docs/SOP/PPE_VM_DESKTOP_OPERATOR_HANDOFF.md
VM loop host: ppeloop@DESKTOP-CAQLL8K. Desktop is IDE BUILD only.
Run what's next; do not restart VM loop unless STACK_DOWN.
```

### Charter thread (UX, data, SELECTION — no relay)

```text
Charter thread. THREAD_ROLE: charter.
Do NOT read OPERATOR_STATUS. Load only your program doc.
Park relay work for the operator thread.
```

---

## Operator checklist (daily)

- [ ] VM: **VM_STATUS** → `stack_loop=True`
- [ ] Desktop: no operator popups; **no** auto-loop
- [ ] If `IDE_BUILD`: **DESKTOP BUILD** in Cursor on desktop; after PR merge → **DESKTOP CONTINUE**
- [ ] If `STACK_DOWN` on VM: **VM_RESTART** once (not repeatedly)
