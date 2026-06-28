# PPE operator process v1 — VM loop + desktop IDE BUILD

**Plane:** CONTROL-PLANE · **Policy:** [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md) · **Buttons:** [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md)

**Purpose:** steward/agent process after the June 2026 Hyper-V cutover — what runs where, and what not to do.

---

## Machine roles (one line)

| Machine | Runs | Does not run |
|---------|------|----------------|
| **VM** | `run_ppe_headless_stack`, auto-loop, `run_ppe_local`, ntfy listen | Cursor IDE BUILD (default) |
| **Desktop** | Cursor IDE BUILD, `DESKTOP_BUILD` / `DESKTOP_CONTINUE` | Loop, headless stack, logon auto-start |

---

## Daily process

### VM (automatic after one-time setup)

1. Logon task **PPE Headless Stack** → `run_ppe_headless_stack.cmd --ensure`
2. Watchdog **PPE VM Watchdog** every 10m (optional recovery)
3. Operator sanity: `VM_STATUS.cmd` when unsure

**One-time VM:** `install_ppe_vm_headless_logon_task.cmd` · `install_ppe_vm_watchdog_task.cmd`

### Desktop (you)

1. `setup_desktop_ide_only.cmd` once — no-loop guard + shortcuts
2. When ntfy says `IDE_BUILD` → **DESKTOP BUILD** → merge → **DESKTOP CONTINUE**
3. Do **not** start `run_ppe_auto_local_loop` or `DESKTOP_AUTO` unless explicitly opted in

**One-shot both machines:** `bootstrap_operator_pair.cmd`

---

## Agent / steward rules

| Rule | Detail |
|------|--------|
| **SELECTION / relay** | Manifest + queue on `main`; VM loop executes — agents do not ask operator to paste orchestrator logs |
| **IDE BUILD** | Product code on **desktop** only; starter `@` file; gate → commit → PR |
| **After product merge** | `mark_ide_product_ready` + VM continues relay (`DESKTOP_CONTINUE` or loop auto) |
| **Recovery** | VM: `fix_vm_operator.cmd` / `vm_bootstrap --recover`; never put loop back on desktop |
| **Docs** | Cite [`PPE_OPERATOR_LAYOUT_ADR.md`](PPE_OPERATOR_LAYOUT_ADR.md) for layout disputes |

---

## Incident playbook (lessons from cutover)

| Symptom | Cause | Fix |
|---------|-------|-----|
| cmd popup storm | Loop on desktop or repeated VM_START | Desktop: `DESKTOP_STOP`; VM: `VM_STOP` → wait 30s → `VM_RESTART` **once** |
| `Windows can't find set` | Pasted batch into Win+R | Double-click `.cmd` files only |
| `git pull` blocked on VM | Dirty `IDE_BUILD_TRIGGER.json` | `vm_bootstrap` or `VM_RESTART` (git hygiene) |
| `relay_result.json not found` | Stale relay state | `fix_vm_operator.cmd` |
| `STACK_DOWN` | Stack crashed or post-reboot | `VM_AUTO` / `VM_RESTART` on **VM** |
| Confused BUILD vs relay | Operator myth | BUILD = desktop Cursor; `run_ppe_local` = VM relay only |

---

## What changed from pre-2026 process

| Old | New |
|-----|-----|
| Desktop = loop host | **VM** = loop host |
| `start_ppe_desktop_operator.cmd` daily | `VM_RESTART` / logon task on VM |
| Phone `build` runs agent on desktop loop | Phone `IDE_BUILD` → **DESKTOP BUILD** on PC |
| Win+R operator commands | `VM_*` / `DESKTOP_*` double-click |
| `fix_vm_operator` hardcoded slice | `vm_bootstrap --recover` (manifest-aware) |

---

## Related

- [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md) — five canonical operator surfaces vs helpers
- [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md) — session handoff
- [`OPERATOR_OPS_QUEUE.md`](OPERATOR_OPS_QUEUE.md) — remaining host-only tasks
- [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) — relay + `ppe_go`
- [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md) — metrics + digests
- [`OPERATING_RULES.md`](OPERATING_RULES.md) — hard operator layout rule
