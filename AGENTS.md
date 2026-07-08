# Agents (Cursor / Codex)

**Repo:** Probability Prediction Engine — agents **auto-ship** when work is done. Do not ask the operator about commits, pushes, staging, or PRs.

## Ship path

1. `python scripts/run_pushable_gate.py`
2. `git status`, `git diff`, `git log -1 --oneline`
3. Commit (slice/chapter + plane + intent)
4. Feature branch: `python scripts/run_pushable_gate.py --pre-push` → `git push` → `gh pr create` to `main` if no PR

**With an active worker lease:** `python scripts/ppe_worker_lease.py --ship --release` (stages lease paths only, gate, commit, push, PR).

## Gate failed?

```bash
python scripts/ppe_branch_recovery.py --plane control --ship
# or with lease:
python scripts/ppe_worker_lease.py --ship --release
```

See `docs/SOP/COMMIT_POLICY.md` § Gate failed.

## Branch recovery (mixed plane)

```bash
python scripts/ppe_branch_recovery.py --plane control --dry-run
python scripts/ppe_branch_recovery.py --plane control --ship --acquire-lease
```

## Canon

| Topic | Doc / rule |
|-------|------------|
| Auto-ship | [`.cursor/rules/auto-ship.mdc`](.cursor/rules/auto-ship.mdc) |
| Commit policy | [`docs/SOP/COMMIT_POLICY.md`](docs/SOP/COMMIT_POLICY.md) |
| Operator relay | [`.cursor/rules/ppe-operator.mdc`](.cursor/rules/ppe-operator.mdc) |
| Thread roles | [`.cursor/rules/ppe-roles.mdc`](.cursor/rules/ppe-roles.mdc) |
| Multi-agent leases | [`docs/SOP/MULTI_AGENT_WORKER_INTERFACE_V1.md`](docs/SOP/MULTI_AGENT_WORKER_INTERFACE_V1.md) |

## Desktop / VM boundary

Daily PC Codex/Cursor shells are the **operator console**, not the relay loop host. On the desktop, agents may read status artifacts, run status helpers, run `DESKTOP_BUILD.cmd`, and run `DESKTOP_CONTINUE.cmd --no-pause`. Product implementation happens only in an explicit `IDE_BUILD` worker flow, and relay/finish execution happens on the VM through the canonical desktop bridge.

Never run these directly from the daily PC shell: `run_ppe_local.cmd`, `run_ppe.cmd`, `run_ppe_auto_local_loop.cmd`, `run_ppe_auto_loop.cmd`, `run_ppe_headless_stack.cmd`, `finish_ide_build.cmd`, or `ppe_autobuilder.cmd advance`. Before any relay command, apply [`.cursor/rules/ppe-desktop-vm-layout.mdc`](.cursor/rules/ppe-desktop-vm-layout.mdc) and [`docs/SOP/PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](docs/SOP/PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md).

## Delegation gate output

- `human_only` → stop (gate exit 1)
- `steward_packet` / `can_auto_ship=False` → **WARN only**; gate exit 0 → still ship

## External Codex sprint prompts

`docs/CONTROL_PLANE/PROMPTS/*` targets **external Codex workers** (ask before git). Cursor agents follow this file and `auto-ship.mdc` instead.

## Hold (no commit)

Ask/read-only mode; explore with no implementation; user said "don't commit"; charter mixed-plane park.

## Cursor stop hook

When an agent turn ends with scoped dirty work, `.cursor/hooks.json` runs `scripts/ppe_auto_ship_stop_hook.py` once (`loop_limit: 1`) to auto-submit a ship reminder — no operator click.
