# Paste into Cursor Settings → User Rules

Copy the block below into your global Cursor user rules so it does not override this repo’s auto-commit policy.

---

## Git commits (Probability Prediction Engine)

For the **Probability Prediction Engine** workspace, follow `.cursor/rules/auto-commit.mdc` and `docs/SOP/COMMIT_POLICY_V1.md`. Do **not** ask “may I commit?” when authorized work is complete.

After the **pushable gate** passes (`python -m ruff check src tests scripts` and `python -m pytest -q`, or docs-only exception per `COMMIT_POLICY_V1.md`), automatically:

1. Run `git status`, `git diff`, and `git log -1 --oneline` (summarize for the user).
2. **Commit** on the current branch with a policy-style message (slice/chapter + plane + intent).
3. On a **feature branch**: **push** (`git push -u origin HEAD` if no upstream), then **open a PR to `main`** if none exists (see `docs/SOP/GITHUB_ZERO_TOUCH_MERGE.md`).

**Never** commit: `.env`, credentials, `artifacts/`, caches, local DBs, or other generated noise listed in `auto-commit.mdc`. **Never** force-push or `git commit --amend` unless the user explicitly asks. On **`main`**, use PR-only delivery when branch protection applies.

For **other repositories**, only commit when the user explicitly asks.
