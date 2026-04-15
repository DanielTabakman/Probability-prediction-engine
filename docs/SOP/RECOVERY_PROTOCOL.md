# RECOVERY_PROTOCOL

Purpose: a **bounded** protocol to repair repo state when boundaries were breached (mixed planes, dirty `main`, ambiguous baseline). RECOVERY is not a default working style.

## When RECOVERY is triggered

Enter **RECOVERY** when any of the following are true:

- Mixed-plane dirty state exists (changes span multiple planes and cannot be safely accepted as one pass).
- Execution work happened directly on `main` (dirty `main` or unreviewed local deltas on `main`).
- Baseline is ambiguous (untracked canonical docs, unknown divergence, or unclear “what is real” vs “local leftovers”).
- A previous pass leaked scope (e.g., CLOSEOUT or SELECTION accidentally made code edits).

## What RECOVERY is allowed to do

RECOVERY may perform **state repair only**, such as:

- Split mixed changes into plane-pure groups (or revert/undo the accidental portion).
- Move work off `main` into a short-lived branch/worktree.
- Restore a reproducible baseline (clean tree or clearly-classified deltas).
- Produce a factual preflight-style report of what is dirty/untracked and why BUILD is blocked/unblocked.

## What RECOVERY must not do

RECOVERY must not:

- Advance product scope (no “while we’re here” improvements).
- Perform new BUILD work under the guise of cleanup.
- Rewrite or “smooth over” **canonical steering truth** just to regain reproducibility.
  - Explicitly: do not change Phase/Sprint/Slice steering claims to match a messy repo state.
  - Steering truth lives in canonical docs; repo-state gate is reported separately.

## Required output artifact

Every RECOVERY pass must return a short **RECOVERY REPORT** containing:

- Trigger (why RECOVERY was entered)
- Actions taken (state repair only)
- Resulting repo-state (branch, ahead/behind, clean/dirty)
- Changed files by plane after recovery
- Untracked canonical docs present? yes/no
- Mixed-plane dirty state? yes/no
- BUILD allowed? yes/no
- If BUILD blocked: exact blocker (one line)

RECOVERY ends when the repo reaches a state where a steward can safely start the next single-plane pass (or can safely hand off with an explicit “blocked” gate and a crisp blocker).

# RECOVERY_PROTOCOL

Purpose: a **bounded** protocol to repair repo state when boundaries were breached (mixed planes, dirty `main`, ambiguous baseline). RECOVERY is not a default working style.

## When RECOVERY is triggered

Enter **RECOVERY** when any of the following are true:

- Mixed-plane dirty state exists (changes span multiple planes and cannot be safely accepted as one pass).
- Execution work happened directly on `main` (dirty `main` or unreviewed local deltas on `main`).
- Baseline is ambiguous (untracked canonical docs, unknown divergence, or unclear “what is real” vs “local leftovers”).
- A previous pass leaked scope (e.g., CLOSEOUT or SELECTION accidentally made code edits).

## What RECOVERY is allowed to do

RECOVERY may perform **state repair only**, such as:

- Split mixed changes into plane-pure groups (or revert/undo the accidental portion).
- Move work off `main` into a short-lived branch/worktree.
- Restore a reproducible baseline (clean tree or clearly-classified deltas).
- Produce a factual preflight-style report of what is dirty/untracked and why BUILD is blocked/unblocked.

## What RECOVERY must not do

RECOVERY must not:

- Advance product scope (no “while we’re here” improvements).
- Perform new BUILD work under the guise of cleanup.
- Rewrite or “smooth over” **canonical steering truth** just to regain reproducibility.
  - Explicitly: do not change Phase/Sprint/Slice steering claims to match a messy repo state.
  - Steering truth lives in canonical docs; repo-state gate is reported separately.

## Required output artifact

Every RECOVERY pass must return a short **RECOVERY REPORT** containing:

- Trigger (why RECOVERY was entered)
- Actions taken (state repair only)
- Resulting repo-state (branch, ahead/behind, clean/dirty)
- Changed files by plane after recovery
- Untracked canonical docs present? yes/no
- Mixed-plane dirty state? yes/no
- BUILD allowed? yes/no
- If BUILD blocked: exact blocker (one line)

RECOVERY ends when the repo reaches a state where a steward can safely start the next single-plane pass (or can safely hand off with an explicit “blocked” gate and a crisp blocker).
