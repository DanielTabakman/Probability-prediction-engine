# WORKER_LOOP

Purpose: define the worker agent's role for executing **one** feature slice at a time.

## Worker responsibilities
- Read `OPERATING_RULES.md`, active `SPRINT_00X.md`, `HANDOFF.md`, and relevant code/docs
- Produce a short pre-edit plan
- Execute **one feature slice**, but **one feature slice may be a fuller pass**: multiple related files, a coherent sub-feature, or a broader local sweep **inside** the feature slice objective
- Run required tests/checks; **launch and inspect** the app when user-visible behavior changes
- Perform cleanup in touched areas—including **stronger local refactors** when verification stays solid and scope stays the same feature slice
- Update `HANDOFF.md`
- Propose useful updates to `CURRENT_FRONTIER.md`
- Return a closeout report to the manager

## Adjacent work inside the same feature slice
You may complete **obvious adjacent sub-work** if it **clearly supports the same feature slice objective** (e.g. same screen, same state flow, same test surface) and does not become a new initiative. If it would, stop and report expansion instead of silently absorbing it.

## Worker boundaries
- Do not invent a new roadmap
- Do not silently change product semantics (see `docs/SEMANTIC_CONTRACTS.md` and the active feature slice spec)
- **Do not chain into the next feature slice automatically**—close out, hand off, let the manager choose
- Do not perform risky cleanup **across unrelated areas** or when tests/inspection do not cover it

## Compact slice mode (optional)

For slices that qualify under **Compact slice mode** in `OPERATING_RULES.md`, you may complete **integrated closeout** (Tier 1 evidence, `HANDOFF.md`, structured closeout report) **inside** the same **BUILD** execution step when those rules are satisfied. Otherwise complete **BUILD**, stop, and let the manager run a separate **CLOSEOUT**.

## Required closeout report
### Objective
### Files changed
### What changed
### Tests run
### Results
### App launch/inspection
### Cleanup performed
### Risks / caveats
### Needs human / manager attention
### Proposed next feature slice options
