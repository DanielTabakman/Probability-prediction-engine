## COMMIT_POLICY_V1

Purpose: remove “should we commit?” ambiguity by defining a small default policy for commits during execution steps.

### Principles

- **Repo/docs truth overrides chat memory**. If it matters for continuity, it should land in the repo as a commit.
- **Single-plane per execution step** still applies (see `OPERATING_RULES.md`).
- Prefer **small, reviewable commits** that preserve recovery paths over one huge “everything” commit.

### Default policy (when in doubt)

1. **Do not commit automatically without an explicit instruction** from the steward/user.\n+   - Exception: if a toolchain (e.g. pre-commit) modifies files in a way required to proceed, treat that as “must include” and ask for commit authorization at the next safe checkpoint.\n+2. If work must proceed through a tool that enforces a clean tree (e.g. relay stage on the *same* checkout), prefer one of:\n+   - run in an isolated **worktree** so execution is not blocked by uncommitted state\n+   - or park the state explicitly (branch + commit) once authorized\n+3. After any execution step that produces a decision artifact (relay decision, closeout evidence), default to **capturing that continuity in a commit** on the relevant branch once authorized.

### Commit placement

- **CONTROL-PLANE** docs changes: commit on a CONTROL-PLANE branch.\n- **PRODUCT-PLANE** changes: commit on the slice BUILD branch.\n- **EVIDENCE-PLANE** changes: commit on the slice BUILD branch (or an evidence-only branch when chartered).\n- Avoid mixing planes in one commit unless the declared execution step is **RECOVERY** and the purpose is separation/repair.

### Minimal commit message standard

- Include: slice ID (or hardening slice ID), plane, and intent.\n- Example: `Sprint004-Slice004: directional strip closeout witness (product-plane)`.

### Relationship to other SOPs

- Branch/worktree isolation: `FRONTIER_STEWARD_PROTOCOL.md`.\n- Execution step types + plane discipline: `OPERATING_RULES.md`.\n- Relay protocol gates: `CODEX_AUTONOMY_V1.md` and `RELAY_RUNTIME_V0.md`.

