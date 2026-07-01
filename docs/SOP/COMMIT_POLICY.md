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

### Gate failed — recover, do not ask

A failed gate (layer audit, mixed plane, wrong branch, unrelated dirty paths) is **agent work**, not an operator decision.

| Thread role | Action |
|-------------|--------|
| **operator** / **ide_build** / **neutral** (implementation done) | Clean branch or split plane → stage task files only → fix layer audit → re-run gate → commit → push → PR. Operator line: **Nothing required from you.** |
| **charter** / **explore** | Park one line to operator thread ([`ppe-thread-roles.mdc`](../../.cursor/rules/ppe-thread-roles.mdc)). No commit questions. |

**Forbidden closers:** “unless you want this committed”, “I can stage if you want”, “commit when the branch is clean” without doing the cleanup yourself (when role allows).

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

### Delegation envelope (gate stderr)

| Gate output | Meaning | Ship? |
|-------------|---------|-------|
| `human_only` | Operator must authorize path or use `PPE_DELEGATION_OVERRIDE=1` on RECOVERY | **No** — gate exit 1 |
| `steward_packet` / `can_auto_ship=False` | Prefer steward decision packet before merge | **Yes** — WARN only; gate exit 0 → commit → push → PR |
| `auto` / `auto_notify` | Routine delegation | **Yes** |

Do **not** treat `can_auto_ship=False` alone as permission to ask the operator about commits.

**After `git merge origin/main` or rebase** on a feature branch: run the gate, then **push** — syncing is not done until push succeeds.

**CI on merge:** GitHub **CI** requires **`CI / pytest`** and **`CI / docker_entrypoint`**. Local `--pre-push` covers pytest + ruff; add **`python scripts/run_pre_push_parity.py --docker`** (or `run_pre_push_parity.cmd --docker`) when you touched `Dockerfile`, deps, or Streamlit entry — otherwise docker smoke runs only on GitHub.

## Ship path (feature branches)

On any branch **other than** `main` / `master`, after gate + commit:

1. `git status`, `git diff`, `git log -1 --oneline` (summarize for the user).
2. `git push` (`git push -u origin HEAD` if no upstream).
3. If no open PR to `main`, `gh pr create --base main --head <branch>`.
4. Merge when CI is green per [`GITHUB_ZERO_TOUCH_MERGE.md`](GITHUB_ZERO_TOUCH_MERGE.md).
5. **Production deploy:** every push to **`main`** runs **Deploy VPS** ([`deploy-vps.yml`](../../.github/workflows/deploy-vps.yml)). The **VPS deploy** job includes a required **msos_web ship verify** ([`verify_msos_web_ship.py`](../../scripts/verify_msos_web_ship.py)) so green deploys cannot serve stale Next.js client bundles. **CI** also runs [`verify_msos_web_build.py`](../../scripts/verify_msos_web_build.py) (`next build`) on every PR/push — catches Edge middleware and compile failures that string-only pytest witnesses miss. After merge (or when shipping MSOS/product to production), run  
   `python scripts/ensure_production_deploy.py --trigger --wait`  
   — waits for deploy and confirms ship verify (auto-redeploy once if workflow green but bundle stale).

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

## Rule precedence (agents)

Resolve conflicts in this order (top wins for this repo):

| Priority | Source | Commit behavior |
|----------|--------|-----------------|
| 1 | **Ask / read-only mode** | No writes — guidance only |
| 2 | User says **“don’t commit”** (this thread) | Hold until released |
| 3 | **[`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc)** (`alwaysApply: true`) | Auto-ship when task complete + gate passes |
| 4 | **Thread role** ([`ppe-thread-roles.mdc`](../../.cursor/rules/ppe-thread-roles.mdc)) | Operator / ide_build / neutral with implementation → ship; charter / explore with **no** implementation → hold; charter mixed-plane → park |
| 5 | Generic Cursor **user rule** (“commit only when asked”) | Applies to **other repos only** — must not block rows 3–4 here |

**Do not** ask “may I commit?” or “may I push?” when priority 3 applies and none of 1–2 block.

## Thread role vs ship

| Role | Auto-ship when done? | Mixed-plane / branch recovery |
|------|----------------------|-------------------------------|
| **operator** / **ide_build** | Yes | Operator thread — [`RECOVERY_PROTOCOL.md`](RECOVERY_PROTOCOL.md) |
| **charter** | Yes for docs/control-plane on clean gate | **Park** — do not stash/checkout in charter thread |
| **neutral** | Yes if user requested implementation | **Park** — operator thread |
| **explore** | Hold unless user asked to implement | **Park** |

Canon: [`.cursor/rules/ppe-thread-roles.mdc`](../../.cursor/rules/ppe-thread-roles.mdc) (`alwaysApply: true`).

## Cursor and global user rules

**Global user rules:** If agents still hesitate, paste [`.cursor/USER_RULES_GIT_SNIPPET.md`](../../.cursor/USER_RULES_GIT_SNIPPET.md) into **Cursor Settings → User Rules** (replace or augment the generic “commit only when asked” block with the PPE exception).

## Related docs

- Tests: [`TESTING_TIERS_V1.md`](TESTING_TIERS_V1.md)
- Agent behavior: [`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc)
- Planes and branches: [`OPERATING_RULES.md`](OPERATING_RULES.md)
- PR merge: [`GITHUB_ZERO_TOUCH_MERGE.md`](GITHUB_ZERO_TOUCH_MERGE.md)
- Worktrees: [`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md)
