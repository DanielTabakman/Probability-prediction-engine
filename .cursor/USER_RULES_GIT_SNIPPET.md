# Git rules for Cursor agents

**Installed in repo:** [`.cursor/rules/auto-commit.mdc`](rules/auto-commit.mdc) (`alwaysApply: true`).

Paste the block below into **Cursor Settings → User Rules** so global “commit only when asked” does not block this repo.

---

## Git commits (Probability Prediction Engine)

For the **Probability Prediction Engine** workspace, follow `.cursor/rules/auto-commit.mdc` and `docs/SOP/COMMIT_POLICY.md`.

When the task is done and `python scripts/run_pushable_gate.py` passes: **commit, push, and open a PR to `main` if needed — without asking.**

After merge/rebase `origin/main` on a feature branch: gate, then push.

Never commit secrets, `artifacts/`, or caches. Never force-push or `--amend` unless asked. On `main`, use PR-only delivery.

For **other repositories**, only commit when the user explicitly asks.
