# PROMPT_TRANSACTION_RULES

Purpose: keep **control-plane prompts transactional** (one prompt = one bounded operation) and prevent **role leakage** (manager vs worker).

## Core rule: one prompt = one transaction
- **One prompt = one transaction** with one clearly defined role and output.
- Each transaction must have a **hard stop condition** and must **stop immediately** after producing the required output.
- **No silent chaining**: do not continue into another role’s prompt or “helpfully” begin the next step unless explicitly instructed by the user.

## Role boundaries (hard)
- **Manager-start**: steering only. **Does not execute sprint work** (no implementation, no tests, no app runs, no code changes).
- **Worker**: execution only. **Does not choose the next sprint** and does not update frontier as source-of-truth.
- **Manager-review**: evidence review + decisions only. **Does not execute sprint work** except when explicitly required to resolve contradictory/missing evidence.

## Output discipline
- When the required output is produced, **stop**. Do not add “next steps” that begin another transaction.
- Do not continue operating “in the background” (no extra exploration, no extra edits) after satisfying the prompt.

## Conservative git posture (default)
- **Do not commit, push, branch, rebase, reset, or amend** unless explicitly asked.
- Avoid destructive commands.
- If a prompt requires work that would normally include git actions, **request explicit user instruction** first.

