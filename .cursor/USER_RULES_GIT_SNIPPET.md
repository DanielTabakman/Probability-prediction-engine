# Git rules for Cursor agents

**Repo (always on):** [`.cursor/rules/auto-ship.mdc`](rules/auto-ship.mdc) · [`.cursor/rules/ppe-roles.mdc`](rules/ppe-roles.mdc) — both `alwaysApply: true`.

**Canon:** [`docs/SOP/COMMIT_POLICY.md`](../docs/SOP/COMMIT_POLICY.md) § Rule precedence.

## Optional: align global User Rules

If Cursor **User Rules** still say “only commit when asked” with **no** PPE exception, agents may conflict with repo policy. Fix once:

1. Open **Cursor Settings → Rules → User Rules**.
2. **Replace** the generic git-commit block **or** add the section below **after** it (the PPE block must not be contradicted by an unqualified “ask first” rule above it).
3. Save — new chats pick it up immediately.

---

## Git commits (Probability Prediction Engine)

**Exception to generic “commit only when asked”:** for workspace **`Probability-prediction-engine`**, follow `.cursor/rules/auto-ship.mdc` and `docs/SOP/COMMIT_POLICY.md`.

When the task is done and `python scripts/run_pushable_gate.py` passes: **commit, push, and open a PR to `main` if needed — without asking.**

**Never ask** “may I commit?”, “want me to commit?”, “unless you want this committed”, or “I can stage if you want”. If the gate fails on branch/layer audit, **fix the branch and ship** (split plane, stage task files, re-run gate) — do not punt to the operator.

Hold (do not commit): Ask/read-only mode; explore/review with no implementation; user said “don’t commit”; charter mixed-plane park; unchartered recovery.

After merge/rebase `origin/main` on a feature branch: gate, then push.

Never commit secrets, `artifacts/`, or caches. Never force-push or `--amend` unless asked. On `main`, use PR-only delivery.

For **all other repositories**, only commit when the user explicitly asks.
