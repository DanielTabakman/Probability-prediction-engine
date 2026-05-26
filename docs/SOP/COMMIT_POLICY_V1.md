# COMMIT_POLICY_V1

Purpose: remove “should we commit?” and “which tests?” ambiguity for humans and agents.

## Principles

- **Repo/docs truth overrides chat memory.** If it matters for continuity, land it in a commit.
- **Single-plane per execution step** still applies (see `OPERATING_RULES.md`).
- Prefer **small, reviewable commits** over one huge dump.

## Test gates (canonical — tiered local gate)

Run from repo root before `git commit` / `git push` on authorized, complete work:

```bash
python scripts/run_pushable_gate.py
```

Dry-run (tier + commands only):

```bash
python scripts/run_pushable_gate.py --dry-run
```

Implementation: [`scripts/run_pushable_gate.py`](../../scripts/run_pushable_gate.py). Operator setup: [`AGENT_GIT_SETUP.md`](AGENT_GIT_SETUP.md).

PRODUCT diffs under `src/viz/` also run [`scripts/check_viz_layer_budget.py`](../../scripts/check_viz_layer_budget.py).

When `artifacts/control_plane/active_slice_touch_set.json` exists (written by `run_slice.cmd` / relay) or env `PPE_SLICE_TOUCH_SET` is set, the gate also runs [`scripts/check_touch_set.py`](../../scripts/check_touch_set.py). See [`VIZ_LAYER_DISCIPLINE_V1.md`](VIZ_LAYER_DISCIPLINE_V1.md).

### Tier table (local)

| Tier | Condition | Local gate |
|------|-----------|------------|
| **0 — docs_only** | Every changed path under `docs/` only | No ruff or pytest |
| **1 — control_plane** | No `src/**`; may include `scripts/`, `tests/`, `.cursor/`, `.github/`, `pyproject.toml`, `pytest.ini`, mixed `docs/` + non-`src` | `ruff check src tests scripts` + **targeted** `pytest -q` on resolved test files |
| **2 — product** | Any `src/**` | `ruff check src tests scripts` + **full** `pytest -q` |

**Tier 1 escalation to full pytest:** if any changed `scripts/**/*.py` has no resolvable `tests/test_<stem>.py` (and no entry in the script→test map in the gate script), or no pytest targets remain after resolution.

**PR / merge to `main`:** GitHub **CI** still runs **full** ruff + pytest + docker entrypoint (`.github/workflows/ci.yml`). The tiered gate is a **local speed** optimization, not a weaker merge bar.

### Implied-lab UI smoke

| When | Command |
|------|---------|
| **GitHub CI** (every PR / push to `main`) | Job **`ui_smoke_compact`** — `python scripts/run_mvp1_compact_ui_smoke_ci.py` (`MVP1_compact_verification`) |
| **Before merge** (steward / implied-lab chapters) | `python scripts/run_mvp1_dual_implied_lab_smoke.py` — record manifest run IDs in PR or evidence |
| **Every commit** | Not required (live-data flaky) |

### Merge to `main`

- GitHub **CI** (`.github/workflows/ci.yml`): **`CI / pytest`**, **`CI / docker_entrypoint`**, **`CI / ui_smoke_compact`**. **Merge on green** requires the workflow run **`success`** (all jobs).
- Prefer PR + auto-merge per `GITHUB_ZERO_TOUCH_MERGE.md`; do not push directly to `main` when branch protection applies.

## Authorization

**Standing authorization (2026-05-19, tiered gate 2026-05-25):** The steward approved this policy. Agents and automation **may commit and push to feature branches** when `python scripts/run_pushable_gate.py` succeeds and the requested task is complete—**without asking “may I commit?” each time.** Still require explicit instruction for ambiguous scope, recovery, or `main` when PR-only delivery applies.

1. **Do not commit** without steward/user instruction when scope is unclear or the change is not part of an authorized task.
   - Exception: toolchain (e.g. pre-commit) modifies files required to proceed — include in the next authorized commit.
2. If a tool requires a clean tree on the same checkout (relay stage), use an isolated **worktree** or park state on a branch + commit once authorized.
3. After a step produces a decision artifact (relay decision, closeout evidence), **capture continuity in a commit** on the relevant branch once authorized.

## Commit placement

- **CONTROL-PLANE** docs: CONTROL-PLANE branch.
- **PRODUCT-PLANE** / **EVIDENCE-PLANE**: slice BUILD branch (or evidence-only branch when chartered).
- Avoid mixing planes in one commit unless **RECOVERY** and the purpose is separation/repair.

## Minimal commit message standard

- Include: slice ID (or hardening slice ID), plane, and intent.
- Example: `Sprint004-Slice004: directional strip closeout witness (product-plane)`.

## Relationship to other SOPs

- **Cursor agent (always-on):** [`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc) — implements this policy in the IDE (commit, feature-branch push, open PR to `main`).
- **Operator setup:** [`AGENT_GIT_SETUP.md`](AGENT_GIT_SETUP.md)
- Branch/worktree isolation: `FRONTIER_STEWARD_PROTOCOL.md`
- Execution steps + planes: `OPERATING_RULES.md`
- Relay gates: `CODEX_AUTONOMY_V1.md`, `RELAY_RUNTIME_V0.md`
- Auto-merge / CI: `GITHUB_ZERO_TOUCH_MERGE.md`

## Cursor user rules (global)

Paste the snippet in [`.cursor/USER_RULES_GIT_SNIPPET.md`](../../.cursor/USER_RULES_GIT_SNIPPET.md) into **Cursor Settings → Rules** so global “commit only when asked” does not block this repo’s standing authorization. See [`AGENT_GIT_SETUP.md`](AGENT_GIT_SETUP.md).
