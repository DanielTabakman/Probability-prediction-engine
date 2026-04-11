# Frontier Steward Protocol

## Purpose

- **Frontier Steward** is the context window responsible for project continuity, bounded slice selection, workflow integrity, and strategic guidance.
- **Repo/docs truth overrides chat memory.**
- **Handoffs are summaries, not ground truth.**

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

## Steward operating rules

- **SELECTION** is always separate.
- **BUILD** may be combined with **CLOSEOUT** only for compact slices that truly earn it (see below).
- A slice is **not closed** until control-plane docs are updated honestly.
- If validation is ambiguous, docs are contradictory, or scope drifts, fall back to separate **BUILD** then steward review.
- Do not silently morph **CLOSEOUT** into **BUILD**.
- Do not silently morph **BUILD** into refactor work.

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

## Closeout minimums

A closeout is only complete when it records:

- Slice title/status
- Scope
- Exact files changed
- Validation run/results
- Artifact/manifest/screenshot paths when applicable
- Honest caveats
- No active slice / next step, if that is the truthful state

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
