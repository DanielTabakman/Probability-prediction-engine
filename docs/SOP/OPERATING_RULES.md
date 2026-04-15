# OPERATING_RULES

Purpose: lightweight rules for how work gets done in this repo.

## Default workflow
1. Read the active feature slice doc (`docs/SOP/SPRINT_00X.md`), `HANDOFF.md`, and directly relevant code/docs.
2. Write a short pre-edit plan (still required; keep it proportional to scope).
3. Prefer **meaningful progress** inside the current frontier: broader local passes and coherent chunks over micro-steps, when verification can still bite.
4. Validate with **automated tests**, **app launch/inspection** when UI changes, and **targeted cleanup**—that stack is the safety system, not hesitation.
5. End with a short factual closeout report.

## Default response conventions (agent/steward)
- Default to **SLIM MODE** unless **AUDIT MODE** is explicitly requested.
- Each execution-step return should include a short **REPO-SENSOR REPORT** (what changed in the working tree: modified/untracked files).

## Execution step discipline (anti-thrash rules)

*An **execution step** is one bounded operational pass; we formerly called this a **transaction**.*

Every work pass is an **execution step** and must declare **exactly one** execution step type up front. Agents must obey the allowed-scope boundary of the declared type.

## Plane discipline (hard rule)

Each execution pass must be **single-plane**. Declare exactly one plane up front and do not mix planes inside the same execution pass.

Plane labels:

- **CONTROL-PLANE**: `docs/SOP/` frontier/handoff/protocol/operating rules
- **PRODUCT-PLANE**: user-facing behavior (`src/`, app behavior)
- **EVIDENCE-PLANE**: tests/harness/validation tooling (`tests/`, `scripts/`, validation tooling)
- **RECOVERY**: state repair only (see `docs/SOP/RECOVERY_PROTOCOL.md`)

**Mixed-plane guardrail:** if the working tree is dirty across multiple planes, BUILD is blocked. Only a **RECOVERY** pass may touch multiple planes, and only to **separate/undo** mixed state (not to advance product work).

## Hard git rule: no execution work directly on `main`

Cursor must not do execution work directly on `main`. Each execution pass must use:

- a short-lived **branch**, or
- a **worktree**.

This is an operational safety rule to prevent “dirty main” cleanup cycles.

## Agent continuity rule (hard)

When **live repo state exists**, the same agent must continue the pass. Live repo state includes:

- stash entries
- staged/uncommitted changes
- partial recovery
- branch/worktree divergence that has not been explicitly parked/handed off
- any incomplete execution state

A new agent is allowed only after the pass is fully closed and repo state is legible/parked (clean working tree, and any remaining state explicitly isolated and named).

Do not switch agents just because the next action is docs-only, closeout, or “easy to explain.”

## Required execution output: Agent continuity

Include this block in every execution-step return (including docs-only passes):

```text
AGENT CONTINUITY
- Safe to switch agents? YES/NO
- Exact reason:
- If YES: exact handoff payload required:
```

### RULE 1 — Execution step types are mandatory
Choose exactly one:
- **BUILD**: Code changes allowed. Goal: implement a bounded feature slice / user story.
- **CLOSEOUT**: No code changes allowed. Goal: capture evidence, update docs, and mark status honestly.
- **RECOVERY**: Only stabilization / revert / separation of mixed state allowed. Goal: restore a trustworthy baseline after boundary leakage or partial failure.
- **SELECTION**: No code changes allowed. Goal: choose exactly one next frontier / story / feature slice.

### RULE 2 — CLOSEOUT cannot silently turn into BUILD
A CLOSEOUT execution step is evidence-and-docs only. If a CLOSEOUT step requires code edits, repeated retries, or bug-chasing, stop immediately, wrap up current evidence, and open a separate RECOVERY or BUILD execution step.

### RULE 3 — Feature slice close rule
A feature slice is closeable when:
- unit tests are green, and
- each **required** smoke path (per **Validation tiers** below and any feature slice / frontier / spec override) has at least one clean green evidence run within the implementation or cleanup window.

If the feature slice changed **user-visible** UI, also satisfy **Tier 1** manual evidence: at least one live inspection or screenshot review of the **actual changed UI region** (see **Validation tiers**).

Later failures reopen a feature slice only if they show:
- a deterministic code regression,
- a repeated reproducible failure with data available, or
- a semantic break in acceptance criteria.

Later failures do NOT automatically reopen a feature slice if they are caused by:
- live-data flakiness,
- external data unavailability,
- environment-sensitive one-off failures,
- reruns outside the implementation/cleanup window that do not demonstrate regression.

### RULE 4 — Validation should be classified
When reporting validation, label steps (where relevant) as:
- deterministic
- environment-sensitive
- live-data-sensitive

Purpose: prevent live-data/environment failures from being confused with product regressions.

### RULE 5 — Stop-after-two rule for non-BUILD execution steps
If an agent makes two consecutive nontrivial corrective edits inside a CLOSEOUT, RECOVERY, or SELECTION execution step, it must stop and return a wrap-up/reassessment instead of continuing to iterate.

## Compact slice mode (low-risk feature slices)

**Use for** low-risk feature slices that mainly touch:

- presentation, copy, layout, visibility / scanability
- non-semantic UI linkage
- provenance display

**Do not** rely on compact combined handling when the slice materially changes:

- classification logic
- disagreement thresholds
- math / derivation
- live-data fetch paths
- harness / scenario semantics

### Default loop (compact)

May be **two** execution steps:

1. **SELECTION** — choose exactly one next feature slice (no code).
2. **BUILD** — implement the slice **and** satisfy **Tier 1** closeout obligations **in the same execution step** (integrated closeout).

Treat this as **Build + Closeout combined** in workflow terms, but declare the execution step type as **BUILD** so scope stays honest (code changes allowed; evidence and docs are part of the same pass).

### When combined Build + Closeout in one BUILD step is allowed

Only when **all** of the following hold:

- **Tier 1** validation passes (see **Validation tiers**).
- At least **one** screenshot or live/manual inspection confirms the **actual changed UI region** (not a generic “app opened” tick).
- `HANDOFF.md` and other doc/state updates can be completed **honestly** in the same pass.
- **No** code-fix / retry loop is needed (first pass is clean enough to close).

### When to fall back to the full loop

Use separate **BUILD** then **CLOSEOUT** (or **BUILD** with retries then **CLOSEOUT**) when:

- any required validation fails or stays inconclusive after the compact attempt,
- the slice touches high-risk areas above,
- ambiguity appears (semantics, contracts, or acceptance unclear), or
- a fix/retry cycle is required.

Higher-risk slices keep the **full** workflow: **SELECTION** → **BUILD** → **CLOSEOUT** (plus extra **BUILD** passes if needed), without assuming integrated closeout.

## Validation tiers (closeout)

**Purpose:** separate universal closeout evidence from layer-specific work so closeout stays fast, cheap, and less thrashy. Unless the frontier/spec explicitly overrides, use these tiers.

### Tier 1 — Universal closeout requirements
Default required validation for closing a feature slice:
- **Unit tests** (`pytest` / project test suite)
- **Primary UI smoke path A** (`A_width_target_payoff` via `python scripts/run_implied_lab_ui_smoke.py` or equivalent documented primary path)
- **One** live/manual inspection **or** screenshot review of the **actual changed UI region** (not a generic “app opened” tick)

### Tier 2 — Conditional validation
Required **only when the feature slice materially touches** the corresponding layer. Examples:
- **Smoke C** (`C_directional_peak_disagreement`) is **required** when the feature slice materially changes: disagreement **classification**; width/peak **scenario** behavior; belief/disagreement **derivation**; scenario/**harness** logic tied to those semantics.
- **Smoke C** is **supporting / optional** for closeout dominance when the feature slice mainly changes: **presentation**; review **legibility**; **layout/copy**; non-classification **UI linkage**—unless the feature slice spec names **C** as a gate.

**Declare conditional validation in the feature slice spec or execution step** when it applies (what you ran and why), so reviewers do not assume every path ran.

### Smoke C is not a universal tax
**Smoke C is not** an automatic universal required closeout gate for every feature slice. It is a **conditional** gate for **classification-sensitive** work and otherwise a **supporting signal**, unless the feature slice spec explicitly requires it.

## Closeout runtime budget / stop rule

Non-deterministic steps (live smoke, headless browser, data-dependent scenarios) must not **dominate** the whole closeout.

- If a step is **slow**, **hangs**, or stays **inconclusive** without **decisive new evidence**, **stop** and **classify** the outcome instead of feeding it more time.
- After **one or two** inconclusive or long-running attempts on the same step, **stop and report**: what was tried, outcome, and classification.
- Use **environment-sensitive**, **live-data-sensitive**, or **scenario-sensitive** when the evidence fits; do not relabel product bugs as operational noise without cause.
- Open **RECOVERY** or **BUILD** **only** when evidence actually points to a **product/code** issue—not to “run smoke until green.”

This complements **RULE 4** (validation labels) and **RULE 5** (stop-after-two for non-BUILD **edits**): here the cap is on **validation spend**, not only on doc/code thrash.

## Preflight hygiene before smoke or closeout

Short operational checklist **before** smoke or live closeout (reduces stale-process thrash):

- Prefer **no** stale/orphan **Python**, **Streamlit**, or **browser** processes that could bind ports or confuse a headless run; clear stuck workers when symptoms match.
- Use **one** clean app instance for the run; avoid two controllers fighting the same server.
- Prefer a **fresh ephemeral port** when the harness allows it.
- Avoid **simultaneous** manual Streamlit run and automated smoke against the same port when you can separate them in time or by port.

Keep this lightweight—checklist, not a new procedure tree.

## BUILD preflight gate (hard requirement)

Before any **BUILD** execution pass, produce a preflight report. **BUILD is blocked** unless the report says **BUILD allowed: YES**.

Preflight must include (machine-derived where possible):

- branch
- ahead/behind vs `origin/<branch>`
- clean/dirty
- changed files by plane (CONTROL/PRODUCT/EVIDENCE)
- untracked canonical docs: yes/no (canonical docs = `docs/SOP/**`)
- mixed-plane dirty state: yes/no
- BUILD allowed: yes/no
- exact blocker if no (one line)

Steward/agent may interpret meaning after listing facts, but should not hand-author repo facts that can be generated.

## Default posture
- Prefer **substantive feature slices** that are still testable over the smallest possible diff for its own sake.
- Preserve current behavior unless the feature slice says to change it.
- Do not silently turn ambiguity into product decisions—**escalate real uncertainty**, not normal engineering judgment.
- Be honest about **verified vs inferred** (Confirmed / High-confidence inference / Speculation).

## Git
**Stay conservative:** do not commit, push, or create branches unless explicitly requested. Local edits are fine.

## Pre-edit plan
Before editing, briefly state:
- understanding of the task
- files to inspect / likely to change
- implementation path (can be a fuller pass if still one feature slice)
- tests and manual checks to run
- cleanup you may do in touched areas
- anything needing human attention

## Testing
After meaningful changes, run validation that actually covers the change, aligned with **Validation tiers** above (universal vs conditional). Always report:
- exact commands run
- pass/fail
- what was actually verified
- what remains unverified

## Cleanup
In touched areas, when **confidence is high** and verification stays solid:
- do the usual safe cleanup (unused imports, dead locals, stale comments, trivial duplication, misleading names)
- allow **stronger local refactors** (structure within a module, unify duplicated paths) if they clearly support the feature slice and tests/inspection still pass

## Escalate instead of guessing
Flag for human attention when **risk or ambiguity is real**, for example:
- product intent or semantics are unclear, or docs clearly conflict
- cleanup/deletion or interface change confidence is low
- a fix wants **structural rewrite** across many boundaries
- tests are too weak to verify the change safely
- scope is **creeping into a new initiative** (not the same feature slice objective)

## Closeout report
End each work pass with:
- objective
- files changed
- what changed
- tests run
- results
- cleanup performed
- risks / caveats
- needs human attention
- recommended next step
- agent continuity block (required; use exact template above)
