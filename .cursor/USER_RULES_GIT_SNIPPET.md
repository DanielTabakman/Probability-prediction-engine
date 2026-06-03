# Git rules for Cursor agents

**Installed in repo:** [`.cursor/rules/ppe-git-commits.mdc`](rules/ppe-git-commits.mdc) (`alwaysApply: true`).

**Optional global copy:** `%USERPROFILE%\.cursor\rules\ppe-probability-engine-git.mdc` (user-level rule file).

To paste into **Cursor Settings → User Rules** manually, use the block below. This stops global “commit only when asked” from blocking [`.cursor/rules/auto-commit.mdc`](rules/auto-commit.mdc).

---

## Git commits (Probability Prediction Engine)

For the **Probability Prediction Engine** workspace, follow `.cursor/rules/auto-commit.mdc` and `docs/SOP/COMMIT_POLICY_V1.md`. Do **not** ask “may I commit?” when authorized work is complete.

After **`python scripts/run_pushable_gate.py`** passes (or docs-only exception per `COMMIT_POLICY_V1.md`), automatically:

1. Run `git status`, `git diff`, and `git log -1 --oneline` (summarize for the user).
2. **Commit** on the current branch with a policy-style message (slice/chapter + plane + intent).
3. On a **feature branch**: **push** (`git push -u origin HEAD` if no upstream), then **open a PR to `main`** if none exists (see `docs/SOP/GITHUB_ZERO_TOUCH_MERGE.md`).

After **merge/rebase `origin/main`** on a feature branch: run the gate, then **push** — do not stop at “merge succeeded” or wait for the user to ask.

**Never** commit: `.env`, credentials, `artifacts/`, caches, local DBs, or other generated noise listed in `auto-commit.mdc`. **Never** force-push or `git commit --amend` unless the user explicitly asks. On **`main`**, use PR-only delivery when branch protection applies.

For **other repositories**, only commit when the user explicitly asks.
