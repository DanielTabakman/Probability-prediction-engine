# Paste into Cursor Settings → User Rules

Copy the block under **“Git commits (Probability Prediction Engine)”** below into Cursor:

1. Open **Cursor Settings** (gear) → **Cursor Settings** (or **General**).
2. Open **Rules** (or **Rules for AI**).
3. Under **User rules** (global), paste the block — or add a **project** rule pointing at this file if your Cursor version supports `@file` includes.

This stops global “commit only when asked” from blocking this repo’s standing authorization in [`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc).

Operator checklist: [`docs/SOP/AGENT_GIT_SETUP.md`](../../docs/SOP/AGENT_GIT_SETUP.md).

---

## Git commits (Probability Prediction Engine)

For the **Probability Prediction Engine** workspace, follow `.cursor/rules/auto-commit.mdc` and `docs/SOP/COMMIT_POLICY_V1.md`. **This workspace overrides** global “commit only when asked” when authorized work is complete.

Do **not** ask “may I commit?” when the task is done and the pushable gate passes.

After authorized work is complete, run the **tiered pushable gate** from repo root:

```bash
python scripts/run_pushable_gate.py
```

When it exits 0, automatically:

1. Run `git status`, `git diff`, and `git log -1 --oneline` (summarize for the user).
2. **Commit** on the current branch with a policy-style message (slice/chapter + plane + intent).
3. On a **feature branch**: **push** (`git push -u origin HEAD` if no upstream), then **open a PR to `main`** if none exists (see `docs/SOP/GITHUB_ZERO_TOUCH_MERGE.md`).

Gate tiers (local only; PR CI still runs full pytest):

- **Tier 0 — docs only:** no pytest/ruff required.
- **Tier 1 — control plane** (`scripts/`, `tests/`, `.cursor/`, config; no `src/`): ruff + targeted pytest on resolved test files.
- **Tier 2 — product** (any `src/`): ruff + full `pytest -q`.

**Never** commit: `.env`, credentials, `artifacts/`, caches, local DBs, or other generated noise listed in `auto-commit.mdc`. **Never** force-push or `git commit --amend` unless the user explicitly asks. On **`main`**, use PR-only delivery when branch protection applies.

For **other repositories**, only commit when the user explicitly asks.
