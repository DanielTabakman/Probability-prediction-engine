# PPE VM + desktop operator — session handoff (2026-06)

**Plane:** CONTROL-PLANE · **Status:** canonical operator layout after Hyper-V VM cutover

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

Desktop shortcuts: run `setup_vm_desktop_shortcuts.cmd` once on VM (or use shortcuts already on VM Desktop).

**Remote triage from daily PC:** `ssh ppeloop@desktop-caqll8k` — see [`PPE_CURSOR_REMOTE_SSH_V1.md`](PPE_CURSOR_REMOTE_SSH_V1.md).

---

## Healthy VM status (example)

```text
PHASE=AWAITING_BUILD VERDICT=IDE_BUILD slice=MSOS-UserStateV1-Product-Slice002 stack_loop=True stack_watch=True next=handoff
```

| Reading | Meaning |
|---------|---------|
| `stack_loop=True` / `stack_watch=True` | Headless stack OK |
| `VERDICT=IDE_BUILD` | Product slice needs **Cursor BUILD on desktop** |
| `PHASE=STACK_DOWN` + `stack_loop=False` | Loop off → double-click **VM_RESTART** on VM |
| `next=handoff` | Waiting for IDE work, not `run_ppe_local` yet |

---

## IDE BUILD vs `ppe_go.cmd` vs `run_ppe_local.cmd`

**Common confusion:** `run_ppe_local.cmd` does **not** implement the product slice. It continues the relay **after** IDE BUILD is done.

| Step | Where | Command / action |
|------|--------|------------------|
| 1. Operator blocks on product | VM loop (automatic) | `VERDICT=IDE_BUILD` in status |
| 2. Implement slice | **Desktop Cursor** | Open `artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md`, build, gate, commit, PR |
| 3. Optional director handoff | **Desktop** | `ppe_go.cmd` → paste in new Agent chat (`@ppe-director` prompt). *May look like “nothing happened” — it copies to clipboard.* |
| 4. Mark product ready | Desktop or agent | `mark_ide_product_ready.cmd <sliceId>` (after merge/gate) |
| 5. Continue relay | **VM** (or desktop if asked) | `run_ppe_local.cmd` — advances control/platform/witness |

**Active slice (as of session end):** `MSOS-UserStateV1-Product-Slice002` — starter at `artifacts/orchestrator/IDE_BUILD_STARTER_MSOS-UserStateV1-Product-Slice002.md`.

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
5. **This file** — session handoff / two-machine truth

**Stale:** [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md) still describes desktop as primary loop host — **override with VM layout** when Hyper-V VM is live.

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
