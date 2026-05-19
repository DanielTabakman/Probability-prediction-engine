# COMMIT_POLICY_V1

Purpose: remove “should we commit?” and “which tests?” ambiguity for humans and agents.

## Principles

- **Repo/docs truth overrides chat memory.** If it matters for continuity, land it in a commit.
- **Single-plane per execution step** still applies (see `OPERATING_RULES.md`).
- Prefer **small, reviewable commits** over one huge dump.

## Test gates (canonical — 2026-05-19)

### Every pushable commit (code or mixed docs+code)

Run from repo root before `git commit` / `git push`:

```bash
python -m ruff check src tests scripts
python -m pytest -q
```

This matches the **`CI / pytest`** workflow (ruff + full pytest). Do not use “targeted pytest only” for commits intended to be shared.

### Docs-only exception

When the diff touches **only** paths under `docs/` (and no `src/`, `tests/`, `scripts/`, or config):

- **pytest:** not required.
- **ruff:** optional unless Python under `scripts/` changed.

### Implied-lab UI (before merge, not every commit)

When a PR or slice changes `src/viz/**` or `scripts/*smoke*` / `implied_lab_ui_smoke_harness.py`:

- Run **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** once before opening or merging the PR.
- Record pass/fail and manifest run IDs in PR text or slice evidence.
- **Not** a commit gate (live-data flaky); **not** in CI yet.

### Merge to `main`

- GitHub required check: **`CI / pytest`** (ruff + full pytest).
- Prefer PR + auto-merge per `GITHUB_ZERO_TOUCH_MERGE.md`; do not push directly to `main` when branch protection applies.

## Authorization

**Standing authorization (2026-05-19):** The steward approved this policy. Agents and automation **may commit and push to feature branches** when the pushable commit gate passes and the requested task is complete—**without asking “may I commit?” each time.** Still require explicit instruction for ambiguous scope, recovery, or `main` when PR-only delivery applies.

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

- Branch/worktree isolation: `FRONTIER_STEWARD_PROTOCOL.md`
- Execution steps + planes: `OPERATING_RULES.md`
- Relay gates: `CODEX_AUTONOMY_V1.md`, `RELAY_RUNTIME_V0.md`
- Auto-merge / CI: `GITHUB_ZERO_TOUCH_MERGE.md`
