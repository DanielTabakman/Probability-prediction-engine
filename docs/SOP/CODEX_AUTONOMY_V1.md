# CODEX_AUTONOMY_V1

Purpose: define a **bounded, safe autonomy protocol** for the **Codex** worker agent to execute **one selected slice** end-to-end with higher throughput, **without** destabilizing canonical steering truth, widening scope, or auto-crossing selection boundaries.

Status: **v1 — introduced before Sprint 003 BUILD.** Applies to workers running under the **Codex** execution role. Other workers (manual Cursor passes, etc.) may opt in by declaring this protocol at pass start.

This doc **does not supersede** existing control-plane rules. It **narrows** them for a specific autonomy mode. On any conflict, canonical docs win in this order:

1. `docs/SOP/CURRENT_FRONTIER.md`
2. `docs/SOP/HANDOFF.md`
3. `docs/SOP/OPERATING_RULES.md`
4. `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`
5. This doc (`CODEX_AUTONOMY_V1.md`)

## 1. Canonical slice loop (unchanged)

```
SELECTION  ->  PREFLIGHT  ->  BUILD  ->  BUILD-CLOSEOUT  ->  PROMOTION  ->  CONTROL-CLOSEOUT  ->  next SELECTION
```

- **SELECTION** and **CONTROL-CLOSEOUT** remain **high-judgment** steward work.
- **RECOVERY** is an **interrupt loop** that can fire from any stage; it is never part of routine autonomy flow.
- **PROMOTION** (e.g., fast-forwarding / merging the BUILD branch into the accepted baseline branch) remains **separate** from **CONTROL-CLOSEOUT** by default.

## 2. Authority boundary for Codex Autonomy v1

**Codex autonomy v1 covers exactly this sub-sequence:**

```
PREFLIGHT  ->  BUILD  ->  bounded REPAIR loop  ->  BUILD-CLOSEOUT  ->  PROMOTION
```

**Codex must stop before `CONTROL-CLOSEOUT` and must not touch `SELECTION`.**

Rationale:

- **SELECTION** is the highest-judgment step (phase/sprint framing, scope framing, deferral calls). Auto-selecting compounds risk.
- **CONTROL-CLOSEOUT** writes canonical steering truth (`CURRENT_FRONTIER.md`, `HANDOFF.md`). Errors there corrupt continuity for every future steward/agent.
- **PREFLIGHT -> PROMOTION** is the range where decisions are mostly **verifiable from repo facts and slice spec**. Autonomy there gives the largest throughput win at the smallest correctness cost.

This boundary is the **recommended default** for v1.

## 3. Scope (single-slice only)

- One Codex autonomy run = **exactly one already-selected slice**.
- The slice must be named in the active sprint spec (`docs/SOP/SPRINT_00X_PHASE_Y.md`) **before** the Codex run begins.
- Codex **may not** redefine slice scope, split the slice, merge in a second slice, or expand into adjacent work beyond what the slice spec already allows under `docs/SOP/OPERATING_RULES.md` **Adjacent supporting work**.

## 4. Plane discipline

- Codex must declare **exactly one plane** for the run, consistent with the slice spec:
  - **PRODUCT-PLANE** (default for Phase 2 BUILD slices)
  - **EVIDENCE-PLANE** (test/harness-only slices)
- Codex **must not** write to **CONTROL-PLANE** (`docs/SOP/**`, `docs/CONTROL_PLANE/**`) in an autonomy run — that is reserved for the separate CONTROL-CLOSEOUT pass.
- If the slice legitimately requires a tiny control-plane edit (e.g., a validation command update), Codex must **stop** and escalate; the steward decides whether to grant a scoped exception or re-scope the slice.

## 5. Allowed actions

Inside the declared plane and slice scope only:

- Create and use a **short-lived BUILD branch** off the accepted baseline (`recovery/frontier-steward-v2_1-baseline` or whatever baseline the current frontier names).
- Edit files inside the declared plane.
- Run required validation: unit tests (`python -m pytest -q`), primary UI smoke (`python scripts/run_implied_lab_ui_smoke.py`) and any **conditional** smokes the slice spec names (e.g., Smoke C for classification-sensitive slices).
- Produce UI smoke artifacts under `artifacts/ui_smoke/<timestamp>/`.
- Commit product-plane changes on the BUILD branch with clear messages.
- Run up to the slice's repair budget (see §7) to turn a failing validation into a passing one **when the failure is clearly caused by code written in this run** and the fix stays inside slice scope.
- Promote the BUILD branch into the accepted baseline branch when **all** BUILD-CLOSEOUT criteria are satisfied (see §8, §9).
- Write a structured **BUILD-CLOSEOUT REPORT** and **HANDBACK** payload for the steward (see §10).

## 6. Forbidden actions

Codex must **not**:

- Start, select, or "continue into" a **second slice**.
- Edit `docs/SOP/**` or `docs/CONTROL_PLANE/**` (CURRENT_FRONTIER, HANDOFF, OPERATING_RULES, etc.).
- Edit `docs/SEMANTIC_CONTRACTS.md`, phase charters, or sprint specs.
- Expand scope beyond the slice spec (no "while we're here" refactors outside the spec's adjacent-work envelope).
- Change user-visible semantics that are not in the slice spec.
- Cross plane lines (e.g., do PRODUCT edits **and** EVIDENCE harness edits in one run unless the slice spec explicitly names both).
- Commit or push to `main` or any protected branch directly.
- Rebase, force-push, amend, or rewrite any already-accepted commit.
- Delete, rename, or move parked branches (`parked/**`), accepted baselines, or tags.
- Silently downgrade canonical steering truth to match a messy repo state.
- Change retry budget, stop conditions, or authority boundary mid-run.
- Continue past a stop condition (§8) by re-interpreting it as benign.

## 7. Retry / repair budget (bounded)

Codex gets a **bounded repair loop** inside BUILD:

- **Max repair iterations per slice: 2.** One BUILD attempt + up to two corrective edits = hard cap of **three** code-change passes before stop.
- Each repair iteration must be a **targeted fix** (not a rewrite), **clearly caused** by the previous validation failure, and **must re-run the same validation** that failed.
- If validation still fails after the 2nd repair iteration, **stop** (see §8).
- If the same test file or the same assertion fails **twice in a row** after distinct repair attempts, treat that as "unclear test results" and stop.
- Cross-slice cleanup or refactor does **not** count against this budget because it is **not allowed** in the first place (§6).

The repair budget aligns with the existing `OPERATING_RULES.md` **RULE 5 (Stop-after-two)** spirit but applied to in-slice BUILD iterations.

## 8. Stop / escalation conditions (hard)

Codex must stop immediately and hand back to the steward on any of:

1. **Preflight fail** — `OPERATING_RULES.md` BUILD preflight gate returns `BUILD allowed: NO`, or the tree is mixed-plane dirty, or canonical docs are untracked.
2. **Max retries exceeded** — §7 repair budget is exhausted and validation is still not green.
3. **Scope ambiguity** — the slice spec is silent or contradictory on something the implementation needs; do not resolve silently.
4. **Unexpected contract change** — the implementation would require changing or implying a change to `docs/SEMANTIC_CONTRACTS.md`, a phase charter, or an accepted slice spec.
5. **Mixed-plane contamination** — any edit would touch CONTROL-PLANE or a second plane not named in the slice spec.
6. **Unclear test results** — validation passes/fails inconsistently, a smoke is inconclusive, an environment-sensitive error masks the signal, or the test output cannot be classified as **deterministic PASS**, **deterministic FAIL**, **environment-sensitive**, or **live-data-sensitive** per `OPERATING_RULES.md` RULE 4.
7. **Selection boundary reached** — the slice is closed (BUILD-CLOSEOUT complete, promotion done) and the "next obvious thing" is a new SELECTION. Do not cross it.
8. **Repo-state drift mid-run** — baseline branch moved under the run, another process pushed commits to the same BUILD branch, or the accepted baseline tip changed in a way the run did not cause.
9. **Control-plane closeout would be needed** — if finishing the slice requires updating `CURRENT_FRONTIER.md` / `HANDOFF.md` to be truthful, that is CONTROL-CLOSEOUT and belongs to the steward.

On stop, Codex must emit a **HANDBACK** (see §10) even if partial work exists; it must not "leave it running" or silently retry.

## 9. Required validation before PROMOTION

Codex may only promote the BUILD branch to the accepted baseline when **all** are true:

- **Unit tests**: `python -m pytest -q` → PASS (exact command + count recorded).
- **Primary UI smoke (Tier 1)**: `python scripts/run_implied_lab_ui_smoke.py` → PASS with a fresh manifest under `artifacts/ui_smoke/<timestamp>/`.
- **Conditional validation** named by the slice spec (e.g., Smoke C for classification-sensitive slices) → PASS.
- **One** screenshot or live inspection evidence of the **actual changed UI region** exists in the run's artifact folder (or the slice is non-UI and the spec explicitly says UI evidence is N/A).
- Working tree is clean on the BUILD branch, no untracked canonical docs, no mixed-plane residue.
- Promotion target is the branch named by `CURRENT_FRONTIER.md` as the accepted baseline (no guessing).
- Promotion method is **fast-forward or clean merge only**. No rebase, no force-push, no amend.

If any of these fail, Codex **must not** promote and **must** stop per §8.

## 10. Required outputs

Every Codex autonomy run must return **exactly** the following, in order:

### 10.1 PREFLIGHT REPORT

From repo facts (machine-derived), matching `OPERATING_RULES.md` BUILD preflight gate:

- branch, ahead/behind vs origin
- working tree clean/dirty
- changed files by plane
- untracked canonical docs (YES/NO)
- mixed-plane dirty state (YES/NO)
- BUILD allowed (YES/NO)
- if NO: exact blocker (one line)

### 10.2 BUILD SUMMARY

- Slice ID and title (verbatim from sprint spec)
- Declared plane
- BUILD branch name and starting SHA
- Files changed (grouped by plane; must be one plane only)
- What changed (short, honest; no marketing language)
- Repair iterations used (0, 1, or 2) and what each one fixed

### 10.3 VALIDATION EVIDENCE

- Exact commands run, results, and classification (deterministic / environment-sensitive / live-data-sensitive)
- Runtime health label if recorded (NORMAL / SLOW_BUT_ACCEPTABLE / WATCH / ESCALATE) per `FRONTIER_STEWARD_PROTOCOL.md`
- Artifact paths: manifest JSON, screenshot, any additional smokes
- UI inspection evidence (screenshot path or live-inspection note) for the **actual** changed region

### 10.4 PROMOTION RECORD (only if promotion occurred)

- Promotion target branch
- Promotion method (fast-forward / merge)
- BUILD branch SHA (pre-promotion)
- Accepted baseline SHA (post-promotion)
- `git merge-base --is-ancestor <product SHA> <baseline tip>` verification line

If promotion did **not** occur, this section must say `PROMOTION: NOT PERFORMED` with a one-line reason that matches a §8 stop condition.

### 10.5 AGENT CONTINUITY (required)

Exact block from `OPERATING_RULES.md`:

```text
AGENT CONTINUITY
- Safe to switch agents? YES/NO
- Exact reason:
- If YES: exact handoff payload required:
```

### 10.6 HANDBACK

One short block telling the steward the next step:

- `READY FOR CONTROL-CLOSEOUT: YES/NO`
- If YES: exact slice ID, product commit SHA, baseline branch, and artifact paths the steward will cite in CONTROL-CLOSEOUT.
- If NO: which §8 stop condition fired and what the steward needs to decide.

Then **STOP**. Do not begin CONTROL-CLOSEOUT. Do not begin the next SELECTION.

## 11. Relationship to existing rules

- **Plane discipline, BUILD preflight gate, RULE 5 stop-after-two, validation tiers, closeout runtime budget, preflight hygiene** — all inherited verbatim from `docs/SOP/OPERATING_RULES.md`. This doc narrows, never loosens, those rules.
- **Single-plane, no-main, agent continuity** — inherited verbatim from `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`.
- **Compact slice mode** — still allowed for qualifying slices, but **Codex autonomy v1 does not include integrated CONTROL-CLOSEOUT** even when a slice would technically qualify for compact mode. Compact mode stays with steward-driven runs until a future `v2` authority boundary extends Codex into CONTROL-CLOSEOUT.
- **Recovery protocol** — `docs/SOP/RECOVERY_PROTOCOL.md` still governs any state repair. Codex must not self-trigger RECOVERY; stop and escalate instead.

## 12. What v1 explicitly leaves to a later pass

- Auto-selection of the next slice (**SELECTION**).
- Writing/updating canonical steering docs (`CURRENT_FRONTIER.md`, `HANDOFF.md`) at CONTROL-CLOSEOUT.
- Cross-slice batching under autonomy (only manual batching per the existing coupled-slice rule is allowed, and it stays steward-driven).
- Multi-slice sprint autonomy (one-shot "drive the sprint"). Out of scope for v1.

These may be reconsidered in a future `CODEX_AUTONOMY_V2.md` once v1 has observable track record (roundtrips, slice closures, reopen rate) across at least Sprint 003.

## 13. Activation

- Codex Autonomy v1 is **opt-in per run**. A run activates it by declaring at the top of its opening message: `PROTOCOL: CODEX_AUTONOMY_V1`.
- The steward may pre-authorize v1 for an entire sprint by naming it in the sprint spec (e.g., `SPRINT_003_PHASE_2.md` §execution model).
- Absence of declaration → worker runs under the default `WORKER_EXECUTION_PROMPT.md` single-step rules (unchanged).

## 14. Last updated

2026-04-20 — introduced before **Sprint 003 SELECTION** as a control-plane process pass. No product code changed by this introduction.
