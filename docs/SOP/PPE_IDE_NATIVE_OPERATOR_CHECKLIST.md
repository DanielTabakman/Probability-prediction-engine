# IDE-native operator checklist

Runnable steps for **no API credits** operation. Full runbook: [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md).

---

## Bootstrap

- [ ] Repo includes operator files (`VM_*.cmd`, `DESKTOP_*.cmd`, `run_ppe_auto_local_loop.cmd`).
- [ ] On `main` before treating layout as canonical.
- [ ] **VM once:** [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md) + `setup_vm_loop_host.cmd` + `install_ppe_vm_headless_logon_task.cmd`.
- [ ] **Desktop once:** `setup_desktop_ide_only.cmd` — [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md).

---

## Daily run (two machines)

- [ ] **VM:** `VM_STATUS.cmd` — expect `stack_loop=True` and sensible `PHASE=` / `VERDICT=`.
- [ ] **Desktop:** loop **off** (`ppe_operator_no_loop.local.cmd`); use Cursor for IDE BUILD only.
- [ ] Phone ntfy: follow button hint in message ([`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md)).
- [ ] `IDE_BUILD` ping → desktop `DESKTOP_BUILD.cmd`; after merge → `DESKTOP_CONTINUE.cmd`.
- [ ] VM `STACK_DOWN` → `VM_RESTART.cmd` on VM (not on desktop).

---

## Daily run (legacy single-machine — deprecated)

- [ ] On **`main`**: `git pull`.
- [ ] **Preflight:** `python scripts/ppe_operator_status.py`.
- [ ] Only if no VM: `start_ppe_desktop_operator.cmd` — prefer VM layout above.

---

## When the loop stops (product)

- [ ] Read `artifacts/orchestrator/IDE_BUILD_NOW.md` or `OPERATOR_GUARD_REPORT.md`.
- [ ] **Autobuilder:** `ppe_autobuilder.cmd status` — agent `@ppe-autobuilder-operator` ([`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md))
- [ ] **Local trigger watcher:** `watch_ide_build_local.cmd` running (desktop stack item 4); `setup_cursor_agent.cmd` + `agent login`
- [ ] **Automation (legacy):** [`CURSOR_IDE_BUILD_AUTOMATION_V1.md`](CURSOR_IDE_BUILD_AUTOMATION_V1.md) cloud webhook — optional; prefer local watcher
- [ ] **Manual:** `@` `IDE_BUILD_STARTER_<sliceId>.md` — starter includes **## When done**.
- [ ] If agent committed but stalled: `finish_ide_build.cmd`
- [ ] Optional: `workflow_metrics.cmd slice close --slice-id <sliceId> --size M --roundtrips N`
- [ ] Loop continues on next pass (or restart loop).

---

## When credits return

- [ ] Stop **local** loop (Ctrl+C).
- [ ] Use **`run_ppe_auto_acp_loop.cmd`** only — do not run local and ACP loops together.
- [ ] `set CURSOR_API_KEY=...` if steward charter is needed.

---

## After chapter closeout

- [ ] New Cursor thread; load only [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md).
- [ ] Do not paste orchestrator logs into steward chat.

---

## Tips

- **Evidence-only chapters** (no Product slice in plan): loop can run control/smoke/closeout unattended.
- **Mixed chapters** with Product: use marker + `run_ppe_local` after IDE BUILD.
- **Split plans** (control/smoke in one plan, product in another) if you want more unattended control work before IDE BUILD.
- **Multitask:** parallel IDE agents are fine for BUILD; they do not replace `run_ppe_local` or the marker.

---

## Chapter hygiene (avoid false PRODUCT_BLOCKED)

- [ ] When product + smoke are witness-complete on `main`, set evidence doc line 2–4 to **`**Status:** **COMPLETE** YYYY-MM-DD`** (required for skip guards).
- [ ] Do **not** leave witness-complete chapters in backlog **`blocked`** — mark **`done`** or run closeout slice promptly.
- [ ] Loop startup runs `run_codebase_health_gate.py --skip-relay`; manual check: same command from repo root.

---

## Related

- [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md)
- [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
- [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)
