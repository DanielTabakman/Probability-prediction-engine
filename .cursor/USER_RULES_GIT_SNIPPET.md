# Paste into Cursor Settings → User Rules

Copy the block under **“Git commits (Probability Prediction Engine)”** below into Cursor:

1. Open **Cursor Settings** (gear) → **Cursor Settings** (or **General**).
2. Open **Rules** (or **Rules for AI**).
3. Under **User rules** (global), paste the block — or add a **project** rule pointing at this file if your Cursor version supports `@file` includes.

This stops global “commit only when asked” from blocking this repo’s standing authorization in [`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc).

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
