# Frontier Steward Protocol

## Purpose

- **Frontier Steward** is the context window responsible for project continuity, bounded slice selection, workflow integrity, and strategic guidance.
- **Repo/docs truth overrides chat memory.**
- **Handoffs are summaries, not ground truth.**
- **Handoff safety has two independent axes:** **doc-state alignment** and **repo-state reproducibility**. Report them separately at handoff.

## Source-of-truth order

1. Pushed repo + current accepted docs
2. `docs/SOP/CURRENT_FRONTIER.md`
3. `docs/SOP/HANDOFF.md`
4. `docs/SOP/OPERATING_RULES.md`
5. `docs/SPRINT_1_SPEC.md`
6. `docs/SEMANTIC_CONTRACTS.md`
7. Older handoff/chat only when docs are silent

## Execution-step model

Hierarchy: **Product vision → Phase → Feature slice → Execution step.**

Exactly **one** execution step type per pass:

- **SELECTION**
- **BUILD**
- **CLOSEOUT**
- **RECOVERY**

## Plane discipline (single-plane per execution pass)

Each execution pass must declare **exactly one plane** and stay inside it. This prevents mixed acceptance and recurring cleanup.

Plane labels:

- **CONTROL-PLANE** — `docs/SOP/` frontier/handoff/protocol/operating rules
- **PRODUCT-PLANE** — user-facing behavior (`src/`, app behavior)
- **EVIDENCE-PLANE** — tests/harness/validation tooling (`tests/`, `scripts/`, validation docs when strictly operational)
- **RECOVERY** — state repair only (see `docs/SOP/RECOVERY_PROTOCOL.md`)

**Rule:** If the working tree is dirty in more than one plane, the pass is blocked unless the declared plane is **RECOVERY** and the work is bounded to state separation/repair.

## Hard git rule: no execution work directly on `main`

Cursor must not perform execution work directly on `main`. Every execution pass runs in isolation:

- Use a **short-lived branch** (preferred) or a **worktree**.
- Keep it operational and simple; do not introduce a new framework.

Minimum acceptable practice:

- Create a short-lived branch for the pass, do the work, then merge via normal review flow.
- If you must inspect `main`, do read-only inspection; do not edit.

## Agent continuity (hard)

When **live repo state exists**, the same agent must continue the pass. Live repo state includes:

- stash entries
- staged/uncommitted changes
- partial recovery
- branch/worktree divergence that has not been explicitly parked/handed off
- any incomplete execution state

A new agent is allowed only when the pass is fully closed and repo state is legible/parked (clean working tree, and any remaining state explicitly isolated and named).

**Required execution output block:**

```text
AGENT CONTINUITY
- Safe to switch agents? YES/NO
- Exact reason:
- If YES: exact handoff payload required:
```

## BUILD preflight gate (required)

BUILD is **blocked** unless a preflight report is produced and says **BUILD allowed: YES**.

Preflight must report repo facts (machine-derived where possible) and only then steward interpretation.

**Preflight required fields:**

- branch
- ahead/behind vs `origin/<branch>`
- working tree clean/dirty
- changed files by plane (CONTROL/PRODUCT/EVIDENCE)
- untracked canonical docs: yes/no (canonical docs = `docs/SOP/**`)
- mixed-plane dirty state: yes/no
- BUILD allowed: yes/no
- exact blocker if no (one line, unambiguous)

**Canonical fact rule:** repo facts should be produced by commands (e.g., git status/diff); steward explains meaning, but should not hand-author “facts” when machine output exists.

## Steward operating rules

- **SELECTION** is always separate.
- **BUILD** may be combined with **CLOSEOUT** only for compact slices that truly earn it (see below).
- A slice is **not closed** until control-plane docs are updated honestly.
- If validation is ambiguous, docs are contradictory, or scope drifts, fall back to separate **BUILD** then steward review.
- Do not silently morph **CLOSEOUT** into **BUILD**.
- Do not silently morph **BUILD** into refactor work.

> **Trial in effect (2026-04-27 onward).** Tiered-delegation soft-launch is active; live authority state in `docs/SOP/CURRENT_FRONTIER.md`. See `CODEX_AUTONOMY_V1.md` "Trial in effect" callout for scope and escalation triggers.

### Compact-slice rule

Compact **BUILD + CLOSEOUT** in one pass is allowed only when **all** are true:

- Slice is small and bounded.
- Mostly layout/copy/presentation/non-semantic linkage.
- No classification/threshold/derivation/fetch/state/harness semantics changes.
- Tier 1 validation is sufficient.
- `CURRENT_FRONTIER` and `HANDOFF` can be updated honestly in the same pass.

### Non-compact rule

Use separate steps when:

- Slice touches engine behavior, state shape, classification, thresholds, derivation, fetches, validation harness semantics, or broader architecture.
- Validation may require iteration or interpretation.
- Closure status depends on judgment after seeing results.

### Coupled slice batching (BUILD-only)

Multiple slices may be **batched into one BUILD** only when **all** are true:

- They serve **one immediate user outcome**.
- They touch **mostly the same file cluster / UI region**.
- They share the **same validation path** (same “what we run” to assess).
- **Semantic ambiguity is low** (reviewers can tell what changed and why).
- Each sub-slice can still be described cleanly in review/closeout (no blur).

**Phase 2 (UX-loop) note:** Adjacent loop slices (e.g., **starter/presets** + **plain-English “what changed?”** readout) may be batched **only** when they remain **PRODUCT-PLANE**, share **Tier 1** validation, and the “what changed” language is explicitly checked against `docs/SEMANTIC_CONTRACTS.md` (no new semantic claims).

Batching is **not allowed** when any are true:

- One sub-slice could plausibly **pass** while another plausibly **fails**.
- **Semantic layers differ materially** (e.g., UI polish vs derivation vs harness semantics).
- **Validation requirements differ materially**.
- A likely **reopen** of one part would muddy ownership/clarity of the others.
- Control-plane reporting would stop being crisp (unclear “what happened” per sub-slice).

Closeout rule for batched work:

- Closeout must record a **batched set title** and the **sub-slices included**.
- It must state what **each sub-slice accomplished**.
- It must label each sub-slice as **accepted** / **deferred** / **reopened**.

## Closeout minimums

A closeout is only complete when it records:

- Slice title/status
- Scope
- Exact files changed
- Validation run/results
- Artifact/manifest/screenshot paths when applicable
- Honest caveats
- No active slice / next step, if that is the truthful state

### UI closeout declaration (minimum)

When a closeout covers a user-visible UI slice, it must also declare:

- **Gate type used:** **hard visual** vs **semantic/copy-only**
- **Bounded capture artifact or witness used:** path(s) to the bounded capture artifact(s) (when used) or an explicit unchanged-layout witness statement
- **Tooling prohibition:** no ad hoc helper scripts / improvised closeout tooling were used (unless separately selected/authorized)

### Runtime health indicators (validation / closeout)

This is **validation runtime inside the repo**—wall-clock for commands such as pytest and smoke—not **Cursor turnaround** in the steward loop (see **Cursor turnaround health** below).

For key validation steps (e.g. unit suite, primary smoke **A**), the steward **may** note lightweight **runtime health** alongside pass/fail—optional signal, not a new workflow layer.

When practical, record **expected runtime** when known and **actual runtime** when observed. Classify with a simple label: **NORMAL**, **SLOW_BUT_ACCEPTABLE**, **WATCH**, **ESCALATE** (judgment call; no extra forms).

**Purpose:** spot **environment drift** and **validation slowness trends**; separate **tooling timeout / capture issues** from a **real slowdown**. **Runtime is a health indicator, not a default hard gate**—do not treat wall-clock alone as slice failure unless slowdown is severe, repeated, or tied to errors/flakes and the evidence supports that call.

## Cursor turnaround health

**Definition:** elapsed time from pasting a steward packet into Cursor until the steward receives a **usable** return (judgment call—good enough to accept, redirect, or reject cleanly).

Optional workflow-health signal only—**not** a hard gate, not a new workflow layer, no extra forms. **Repeated** slowdown matters more than one long pass. Track **by execution step type** when practical (**BUILD** / **CLOSEOUT** / **RECOVERY** / **SELECTION** have different “normal” speeds). Interpret together with **roundtrips** and **raw copy-pastes** from the window ledger so a slow pass is not read in isolation.

When useful, note:

- **Execution step type** (this pass)
- **Expected turnaround** (from recent normal for that step type, when known)
- **Actual turnaround**
- **Classification:** **NORMAL** | **SLOW_BUT_ACCEPTABLE** | **WATCH** | **ESCALATE**
- **Likely cause** (pick one or mark unknown): **normal complexity** | **validation time** | **Cursor drift/confusion** | **repo/tooling friction** | **unknown**
- **Outcome quality:** **first-pass accepted** | **follow-up required** | **recovery required**

## Default steward response pattern

1. Verify reality against repo/docs.
2. Reconcile drift vs handoff.
3. Choose one bounded next move.
4. Issue agent packet.
5. Inspect return.
6. Either accept + close, or reject/fallback cleanly.

## Anti-hallucination guidance

- Treat handoffs as provisional until verified.
- Prefer explicit **UNKNOWN** over invented certainty.
- Stale docs and stale handoffs must be called out directly.
- Continuity corruption is a bigger risk than extra process.

## Strategic-adviser guidance

- Steward may advise on workflow, sequencing, and scope risk.
- Avoid refactor gravity during user-facing legibility phases.
- Prefer smallest meaningful slice that improves phase success.
- Do not let “helpful expansion” hijack the frontier.

## Window ledger

Definitions:

- **Roundtrips** — one packet sent to Cursor + one return pasted back.
- **Raw copy-pastes** — total Cursor-related paste actions in either direction.
- **Slices closed** — number of feature slices fully closed in the current steward window.

Protocol:

- Steward should maintain a simple running ledger in chat replies when useful.
- Ledger is **per context window**, not global.
- On new steward window start, ledger resets unless explicitly carried forward.
- When discussing **Cursor turnaround**, use **roundtrips** and **raw copy-pastes** as companion context (same window).

Preferred format:

`Ledger — Roundtrips: X | Raw copy-pastes: Y | Slices closed: Z | Active slice: ___ | Next step: ___`

## Current convention

- **SELECTION** remains separate.
- Compact slices target one-shot **BUILD + CLOSEOUT** if earned.
- Non-compact slices use **BUILD** then steward judgment then **CLOSEOUT**.
- Docs are part of done.

## Short examples

1. **Compact slice:** layout/orientation polish → **BUILD + CLOSEOUT** if Tier 1 passes and docs updated.
2. **Non-compact slice:** classification/derivation change → **SELECTION** then **BUILD** then **CLOSEOUT**.

## Handoff note

- Next steward should read **this doc** before trusting prior chat narrative.
- This doc governs steward workflow unless superseded by a newer accepted protocol doc.
- **Mandatory handoff reporting split:** always report **Doc-state safety** (canonical docs aligned) separately from **Repo-state safety** (branch/divergence/cleanliness; reproducible checkout).
- **Canonical naming:** treat **H1 / H1-01 / H1-02** as **non-canonical legacy shorthand** unless explicitly reintroduced by accepted repo docs. Prefer **Phase / Sprint / Slice / Execution step** identifiers in all control-plane updates.
- Mandatory continuity reporting: include the **AGENT CONTINUITY** block in every execution-step return and handoff.

## SOP reads: LOAD-ALWAYS vs LOAD-ON-DEMAND (advisory)

Advisory companion to `docs/SOP/WORKFLOW_CONTEXT_AUDIT_001.md` (context-budget bands). Not a gate. Overridable with a recorded reason.

**LOAD-ALWAYS (every BUILD-class pass):**
- `docs/SOP/CURRENT_FRONTIER.md` (canonical next step; outranks HANDOFF on drift)
- `docs/SOP/HANDOFF.md` (minimum session context)
- the **active sprint spec** only (e.g. `docs/SOP/SPRINT_003_PHASE_2.md`)

**LOAD-ON-DEMAND (only when the pass actually touches them):**
- `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`, `docs/SOP/OPERATING_RULES.md` — read on scope/gate questions
- `docs/SOP/CODEX_AUTONOMY_V1.md`, `docs/SOP/JOB_REGISTRY_V1.md`, `docs/SOP/RELAY_RUNTIME_V0.md` — read only for relay-assisted BUILD
- `docs/SOP/WORKFLOW_METRICS_V1.md`, `docs/SEMANTIC_CONTRACTS.md`, older sprint specs — read on explicit reference
- `docs/SOP/WORKFLOW_CONTEXT_AUDIT_001.md` — read when a pass classifies as WATCH/ESCALATE

## Current recovery reality (minimal note)

- **Clean control-plane baseline:** `recovery/frontier-steward-v2_1-baseline` @ `7cc2e28`
- **Parked deferred mixed state (explicitly unaccepted):** `parked/deferred-mixed-stash0` @ `3983870`
- **Slice 005 SELECTION** may proceed conceptually from canonical docs.
- **BUILD remains blocked** pending later triage of the parked deferred state.
