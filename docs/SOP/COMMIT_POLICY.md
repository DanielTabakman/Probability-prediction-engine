# Commit policy (PPE)

**Default:** agents and automation **commit and push without asking** when work for the current task is done and the gate passes. Revert bad commits if needed; do not block routine shipping on human approval per commit.

**Scope:** This repository only. In other repos, commit only when the user explicitly asks.

**Test detail:** [`TESTING_TIERS_V1.md`](TESTING_TIERS_V1.md) — this doc covers *when* and *how* to commit; that doc covers *what* to run.

## Principles

- **Land continuity in git.** If it matters for the next agent or operator, commit it.
- **One plane per commit** when practical (see [`OPERATING_RULES.md`](OPERATING_RULES.md)); recovery commits may mix planes only to separate or repair.
- **One commit per task** by default; split only when changes are clearly unrelated (e.g. docs vs product).
- **Small commits are fine.** ~200 commits on this workflow without systemic breakage — prefer steady auto-ship over manual gatekeeping.

## When to commit (auto)

Commit and continue the ship path when **any** of these is true:

| Trigger | Action |
|---------|--------|
| IDE BUILD / steward slice work is complete | Gate → commit → push → open PR if missing |
| User asked for an implementation and it is done | Same |
| Operator fix (`ERROR`, `IDE_BUILD`, `FIX_PLAN`, etc.) is resolved | Same |
| Chartered closeout or relay decision artifact | Same |
| Docs/SOP edit that closes a chartered pass | Same (tier 0 if `docs/` only) |

Do **not** ask “may I commit?” or “may I push?” for the rows above.

## When to hold (no commit)

| Situation | Why |
|-----------|-----|
| Pure exploration, review, or planning — no implementation requested | Nothing to ship |
| User explicitly said “don’t commit yet” | Respect the pause |
| Recovery or scope change with no charter | Avoid parking unknown state on a branch |
| Would commit secrets or generated noise (see below) | Safety, not caution |

**Mid-slice WIP:** discouraged unless the user asks for an intermediate save. Finish the slice, then one commit.

## Gates

Run from repo root. Tier classification and layer audit are built into the gate script.

| Step | Command | Matches |
|------|---------|---------|
| **Commit** | `python scripts/run_pushable_gate.py` | Tier 0–2; scoped pytest when mappable, else fast markers |
| **Push** | `python scripts/run_pushable_gate.py --pre-push` | Full pytest on `upstream..HEAD` — same as **`CI / pytest`** |
| **Push (CI parity)** | `python scripts/run_pre_push_parity.py` | Same as push row; optional `--docker` adds **`CI / docker_entrypoint`** locally |
| **Viz PR / merge** | `python scripts/run_implied_lab_ui_smoke.py` (or dual when chartered) | Heavy smoke — **not** a commit gate; see [`TESTING_TIERS_V1.md`](TESTING_TIERS_V1.md) |

**Docs-only:** diff touches only `docs/` → tier 0 (no pytest). Ruff optional unless `src/` or `scripts/` also changed.

**After `git merge origin/main` or rebase** on a feature branch: run the gate, then **push** — syncing is not done until push succeeds.

**CI on merge:** GitHub **CI** requires **`CI / pytest`** and **`CI / docker_entrypoint`**. Local `--pre-push` covers pytest + ruff; add **`python scripts/run_pre_push_parity.py --docker`** (or `run_pre_push_parity.cmd --docker`) when you touched `Dockerfile`, deps, or Streamlit entry — otherwise docker smoke runs only on GitHub.

## Ship path (feature branches)

On any branch **other than** `main` / `master`, after gate + commit:

1. `git status`, `git diff`, `git log -1 --oneline` (summarize for the user).
2. `git push` (`git push -u origin HEAD` if no upstream).
3. If no open PR to `main`, `gh pr create --base main --head <branch>`.
4. Merge when CI is green per [`GITHUB_ZERO_TOUCH_MERGE.md`](GITHUB_ZERO_TOUCH_MERGE.md).

**`main`:** PR-only when branch protection applies — do not push product work directly to `main`.

## Commit shape

**Message:** slice or chapter ID + plane + intent.

Example: `MSOS-PublicLaunchV1-Platform-Slice002: Caddy route stub (platform-plane)`

**Branch placement:**

| Plane | Branch |
|-------|--------|
| Control-plane docs / relay | CONTROL or slice BUILD branch per charter |
| Product / evidence | Slice BUILD branch |

**Never commit:**

- `.env`, credentials, keys, tokens
- `artifacts/`, `.pytest_cache/`, `__pycache__/`, `*.sqlite*`, `*.db`, log dumps
- Other generated noise unless the task explicitly requires it

**Never** force-push, `git commit --amend`, or change git config unless the user explicitly asks.

## Cursor and global user rules

**Precedence:** For this workspace, [`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc) overrides generic Cursor user rules such as “commit only when asked.”

Optional: paste [`.cursor/USER_RULES_GIT_SNIPPET.md`](../../.cursor/USER_RULES_GIT_SNIPPET.md) into **Cursor Settings → User Rules** so global rules do not block auto-commit here.

## Related docs

- Tests: [`TESTING_TIERS_V1.md`](TESTING_TIERS_V1.md)
- Agent behavior: [`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc)
- Planes and branches: [`OPERATING_RULES.md`](OPERATING_RULES.md)
- PR merge: [`GITHUB_ZERO_TOUCH_MERGE.md`](GITHUB_ZERO_TOUCH_MERGE.md)
- Worktrees: [`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md)
