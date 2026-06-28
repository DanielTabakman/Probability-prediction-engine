# PPE canonical operator scripts v1

**Plane:** CONTROL-PLANE · **Audience:** operators, stewards, agents  
**Related:** [`OPERATOR_BUTTON_MAP.md`](OPERATOR_BUTTON_MAP.md) · [`PPE_OPERATOR_PROCESS_V1.md`](PPE_OPERATOR_PROCESS_V1.md)

## Why this doc exists

The repo has **80+** `ppe_*.py` scripts and **100+** `.cmd` wrappers. Most are helpers, witnesses, or one-shot utilities. **Five surfaces** drive day-to-day operation — when in doubt, start here.

---

## The five canonical surfaces

| # | Surface | Primary entry | What it answers |
|---|---------|---------------|-----------------|
| 1 | **Verdict / status** | `python scripts/ppe_operator_status.py` · `ppe_autobuilder.cmd status --brief` | What should run next? (`IDE_BUILD`, `RUN_LOCAL`, `RUN_AUTO`, …) |
| 2 | **Relay advance** | `run_ppe.cmd` (VM) · `ppe_autobuilder.cmd advance` | Execute the next relay slice or propagate queue |
| 3 | **Pushable gate** | `python scripts/run_pushable_gate.py` | Is this commit/PR safe to push? (tier 0/1/2) |
| 4 | **IDE BUILD handoff** | `DESKTOP_BUILD.cmd` → `scripts/ppe_ide_handoff.py` | Stage Cursor/Codex worker when verdict is `IDE_BUILD` |
| 5 | **Relay runtime** | `python scripts/relay_runtime_v0.py` | Stage / resume / abort a single in-flight relay run (file-backed state machine) |

Everything else is **supporting** — deploy witnesses, ntfy helpers, digests, SSH bootstrap, etc.

---

## Machine → canonical action

| Machine | Verdict | Run |
|---------|---------|-----|
| **Desktop** | `IDE_BUILD` | `DESKTOP_BUILD.cmd` (never `run_ppe_local.cmd`) |
| **Desktop** | After product PR merged | `DESKTOP_CONTINUE.cmd` |
| **VM** | `RUN_LOCAL` | `run_ppe_local.cmd` |
| **VM** | `RUN_AUTO` | `run_ppe.cmd` or `ppe_autobuilder.cmd advance` |
| **Either** | Unsure | `python scripts/ppe_operator_status.py` first |

Guard before any relay on desktop: `python scripts/ppe_loop_host_guard.py --check` — if `"allowed": false`, do **not** run VM-only relay locally.

---

## Helper tiers (not canonical — use when needed)

| Tier | Examples | When |
|------|----------|------|
| **Queue / manifest** | `ppe_auto_select.py`, `ppe_manifest.py`, `ppe_propagate_queue.py` | Steward sets next chapter; recovery |
| **Notify / phone** | `ppe_notify_fix.py`, `ppe_ntfy_listen.py`, `ppe_operator_hint.py` | Mobile alerts; blocked-state triage |
| **Witness / deploy** | `verify_msos_web_ship.py`, `ensure_production_deploy.py` | Post-merge production checks |
| **Recovery** | `vm_bootstrap.cmd --recover`, `fix_vm_operator.cmd` | Stale relay, dirty trigger, stack down |
| **Closeout** | `post_relay_continue.py`, `apply_control_closeout_v1` (via relay) | Chapter COMPLETE propagation |

If a helper and a canonical surface disagree, **trust the canonical surface** after `ppe_operator_status.py`.

---

## Agent rule

1. Read `artifacts/orchestrator/OPERATOR_STATUS.md` (or run `ppe_operator_status.py`).
2. Map verdict → **one row** in the machine table above.
3. Do not invent a new script path when a canonical surface already exists.
4. Add new automation as a **helper** unless steward promotes it in this doc.

---

## Related tests

| Module | Test file |
|--------|-----------|
| `relay_runtime_v0.py` | `tests/test_relay_runtime_v0.py` |
| `run_pushable_gate.py` | `tests/test_run_pushable_gate.py` |
| `ppe_operator_status.py` | `tests/test_ppe_operator_status.py` (if present) |

See [`MODULE_TEST_COVERAGE_V1.md`](MODULE_TEST_COVERAGE_V1.md) for engine/product module coverage.
