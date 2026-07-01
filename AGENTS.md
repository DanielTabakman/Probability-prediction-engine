# Agents (Cursor / Codex)

**Repo:** Probability Prediction Engine — agents **auto-ship** when work is done. Do not ask the operator about commits, pushes, staging, or PRs.

## Ship path

1. `python scripts/run_pushable_gate.py`
2. `git status`, `git diff`, `git log -1 --oneline`
3. Commit (slice/chapter + plane + intent)
4. Feature branch: `python scripts/run_pushable_gate.py --pre-push` → `git push` → `gh pr create` to `main` if no PR

**With an active worker lease:** `python scripts/ppe_worker_lease.py --ship --release` (stages lease paths only, gate, commit, push, PR).

## Gate failed?

Layer audit / mixed branch / wrong branch → **agent fixes hygiene**, not operator choice. See `docs/SOP/COMMIT_POLICY.md` § Gate failed.

## Canon

| Topic | Doc / rule |
|-------|------------|
| Auto-ship | [`.cursor/rules/auto-ship.mdc`](.cursor/rules/auto-ship.mdc) |
| Commit policy | [`docs/SOP/COMMIT_POLICY.md`](docs/SOP/COMMIT_POLICY.md) |
| Operator relay | [`.cursor/rules/ppe-operator.mdc`](.cursor/rules/ppe-operator.mdc) |
| Thread roles | [`.cursor/rules/ppe-roles.mdc`](.cursor/rules/ppe-roles.mdc) |
| Multi-agent leases | [`docs/SOP/MULTI_AGENT_WORKER_INTERFACE_V1.md`](docs/SOP/MULTI_AGENT_WORKER_INTERFACE_V1.md) |

## Delegation gate output

- `human_only` → stop (gate exit 1)
- `steward_packet` / `can_auto_ship=False` → **WARN only**; gate exit 0 → still ship

## External Codex sprint prompts

`docs/CONTROL_PLANE/PROMPTS/*` targets **external Codex workers** (ask before git). Cursor agents follow this file and `auto-ship.mdc` instead.

## Hold (no commit)

Ask/read-only mode; explore with no implementation; user said "don't commit"; charter mixed-plane park.

## Cursor stop hook

When an agent turn ends with scoped dirty work, `.cursor/hooks.json` runs `scripts/ppe_auto_ship_stop_hook.py` once (`loop_limit: 1`) to auto-submit a ship reminder — no operator click.
