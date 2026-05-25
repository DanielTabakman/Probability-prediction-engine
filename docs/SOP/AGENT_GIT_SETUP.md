# Agent git setup (one-time operator)

Purpose: stop Cursor agents from asking “may I commit?” on every BUILD closeout while keeping safe, diff-aware test gates.

## 1. Fix global Cursor user rules (required)

Repo rules ([`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc)) authorize auto-commit, but **global** user rules that say “only commit when explicitly asked” often win.

1. Open **Cursor Settings → Rules → User rules**.
2. **Remove or replace** the global block that requires explicit commit permission each time.
3. Paste the **“Git commits (Probability Prediction Engine)”** block from [`.cursor/USER_RULES_GIT_SNIPPET.md`](../../.cursor/USER_RULES_GIT_SNIPPET.md).

For other repositories, keep “commit only when asked.”

## 2. Local pushable gate (agents run this)

From repo root before commit / push on an authorized, complete task:

```bash
python scripts/run_pushable_gate.py
```

Dry-run (tier + commands only):

```bash
python scripts/run_pushable_gate.py --dry-run
```

Canonical tiers: [`COMMIT_POLICY_V1.md`](COMMIT_POLICY_V1.md).

## 3. Expected agent behavior (PPE only)

| After gate | Agent should |
|------------|----------------|
| Pass | Show `git status`, `git diff`, `git log -1 --oneline`; **commit**; on feature branch **push** and open PR to `main` if none exists |
| Fail | Fix and re-run gate; do not commit |
| Ambiguous scope / recovery | Do **not** auto-commit; escalate |

Never auto-commit: `.env`, credentials, `artifacts/`, caches, local DB files (see `auto-commit.mdc`).

## 4. CI vs local gate

- **Local:** tiered gate (docs-only / targeted pytest / full pytest) via `run_pushable_gate.py`.
- **PR merge:** GitHub **CI** still runs full ruff + pytest + docker entrypoint — unchanged.

## 5. When network works (e.g. home Wi‑Fi)

Library Wi‑Fi often blocks Git HTTPS (port 443) even when the browser can open GitHub.

**Check what still needs pushing:**

```powershell
cd "d:\Users\User\Desktop\Probability prediction engine"
git fetch origin
git status
git branch -vv
```

**If `build/msos-live-mirror-title` is up to date with `origin/...`:** tiered gate commit `2776dbb` is already on the remote for that branch — open or refresh the PR to `main` if needed.

**If `build/ppe-unified-run-v1` shows `ahead` of origin** (optional cleanup branch from an earlier session):

```powershell
git checkout build/ppe-unified-run-v1
git push origin HEAD
```

**After any push:** tell the agent “home — push done” or paste `git status` so it can help with PR / merge-on-green.

## References

- [`COMMIT_POLICY_V1.md`](COMMIT_POLICY_V1.md)
- [`GITHUB_ZERO_TOUCH_MERGE.md`](GITHUB_ZERO_TOUCH_MERGE.md)
- [`OPERATING_RULES.md`](OPERATING_RULES.md) § Git
