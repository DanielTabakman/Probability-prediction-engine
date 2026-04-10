# OPERATING_RULES

Purpose: lightweight rules for how work gets done in this repo.

## Default workflow
1. Read the active sprint doc, `HANDOFF.md`, and directly relevant code/docs.
2. Write a short pre-edit plan (still required; keep it proportional to scope).
3. Prefer **meaningful progress** inside the current frontier: broader local passes and coherent chunks over micro-steps, when verification can still bite.
4. Validate with **automated tests**, **app launch/inspection** when UI changes, and **targeted cleanup**—that stack is the safety system, not hesitation.
5. End with a short factual closeout report.

## Transaction discipline (anti-thrash rules)
Every work pass is a **transaction** and must declare **exactly one** transaction type up front. Agents must obey the allowed-scope boundary of the declared type.

### RULE 1 — Transaction types are mandatory
Choose exactly one:
- **BUILD**: Code changes allowed. Goal: implement a bounded sprint/story.
- **CLOSEOUT**: No code changes allowed. Goal: capture evidence, update docs, and mark status honestly.
- **RECOVERY**: Only stabilization / revert / separation of mixed state allowed. Goal: restore a trustworthy baseline after boundary leakage or partial failure.
- **SELECTION**: No code changes allowed. Goal: choose exactly one next frontier/story/sprint.

### RULE 2 — CLOSEOUT cannot silently turn into BUILD
A CLOSEOUT transaction is evidence-and-docs only. If a CLOSEOUT step requires code edits, repeated retries, or bug-chasing, stop immediately, wrap up current evidence, and open a separate RECOVERY or BUILD transaction.

### RULE 3 — Sprint close rule
A sprint is closeable when:
- unit tests are green, and
- each **required** smoke path (per **Validation tiers** below and any sprint/frontier/spec override) has at least one clean green evidence run within the implementation or cleanup window.

If the sprint changed **user-visible** UI, also satisfy **Tier 1** manual evidence: at least one live inspection or screenshot review of the **actual changed UI region** (see **Validation tiers**).

Later failures reopen a sprint only if they show:
- a deterministic code regression,
- a repeated reproducible failure with data available, or
- a semantic break in acceptance criteria.

Later failures do NOT automatically reopen a sprint if they are caused by:
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

### RULE 5 — Stop-after-two rule for non-BUILD transactions
If an agent makes two consecutive nontrivial corrective edits inside a CLOSEOUT, RECOVERY, or SELECTION transaction, it must stop and return a wrap-up/reassessment instead of continuing to iterate.

## Validation tiers (closeout)

**Purpose:** separate universal closeout evidence from layer-specific work so closeout stays fast, cheap, and less thrashy. Unless the frontier/spec explicitly overrides, use these tiers.

### Tier 1 — Universal closeout requirements
Default required validation for closing a sprint:
- **Unit tests** (`pytest` / project test suite)
- **Primary UI smoke path A** (`A_width_target_payoff` via `python scripts/run_implied_lab_ui_smoke.py` or equivalent documented primary path)
- **One** live/manual inspection **or** screenshot review of the **actual changed UI region** (not a generic “app opened” tick)

### Tier 2 — Conditional validation
Required **only when the sprint materially touches** the corresponding layer. Examples:
- **Smoke C** (`C_directional_peak_disagreement`) is **required** when the sprint materially changes: disagreement **classification**; width/peak **scenario** behavior; belief/disagreement **derivation**; scenario/**harness** logic tied to those semantics.
- **Smoke C** is **supporting / optional** for closeout dominance when the sprint mainly changes: **presentation**; review **legibility**; **layout/copy**; non-classification **UI linkage**—unless the sprint spec names **C** as a gate.

**Declare conditional validation in the sprint or transaction** when it applies (what you ran and why), so reviewers do not assume every path ran.

### Smoke C is not a universal tax
**Smoke C is not** an automatic universal required closeout gate for every sprint. It is a **conditional** gate for **classification-sensitive** work and otherwise a **supporting signal**, unless the sprint spec explicitly requires it.

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

## Default posture
- Prefer **substantive sprints** that are still testable over the smallest possible diff for its own sake.
- Preserve current behavior unless the sprint says to change it.
- Do not silently turn ambiguity into product decisions—**escalate real uncertainty**, not normal engineering judgment.
- Be honest about **verified vs inferred** (Confirmed / High-confidence inference / Speculation).

## Git
**Stay conservative:** do not commit, push, or create branches unless explicitly requested. Local edits are fine.

## Pre-edit plan
Before editing, briefly state:
- understanding of the task
- files to inspect / likely to change
- implementation path (can be a fuller pass if still one sprint)
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
- allow **stronger local refactors** (structure within a module, unify duplicated paths) if they clearly support the sprint and tests/inspection still pass

## Escalate instead of guessing
Flag for human attention when **risk or ambiguity is real**, for example:
- product intent or semantics are unclear, or docs clearly conflict
- cleanup/deletion or interface change confidence is low
- a fix wants **structural rewrite** across many boundaries
- tests are too weak to verify the change safely
- scope is **creeping into a new initiative** (not the same sprint objective)

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
