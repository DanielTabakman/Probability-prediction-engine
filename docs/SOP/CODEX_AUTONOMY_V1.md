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

## 14. Relay result contract (machine-readable)

Purpose: give a relay (process supervising a Codex autonomy run) a **single, machine-readable payload** it can parse **without rereading** §§1–13 to decide whether the run may continue, must stop, may retry, or is hard-blocked.

The relay result is emitted **once per run**, **after** the worker's §10 textual outputs are produced, and **in addition** to them — never in place of them. The §10 blocks remain the human-readable record; this section is the structured form a relay reads.

File location: emitted to stdout by the worker **and** written to a run-scoped path the worker names in §10.3 (`artifacts/ui_smoke/<timestamp>/relay_result.json` is a reasonable default; the slice spec may name another path).

### 14.1 Field definitions

All fields are required unless marked optional. Enum values are case-sensitive. Unknown values are a **schema violation** and must cause the relay to treat the run as `BLOCKED` (see §15).

```json
{
  "protocol": "CODEX_AUTONOMY_V1",
  "schema_version": "1",
  "slice_id": "<SprintNNN-SliceNNN verbatim from sprint spec>",
  "run_id": "<timestamp or uuid; must match the run's artifact folder>",

  "declared_plane": "PRODUCT-PLANE | EVIDENCE-PLANE",
  "build_branch": "<branch name created for this run>",
  "baseline_branch": "<accepted baseline named by CURRENT_FRONTIER.md>",
  "baseline_tip_before": "<SHA at run start>",
  "baseline_tip_after":  "<SHA at run end; equal to baseline_tip_before if no promotion>",
  "product_commit_sha":  "<SHA of the product commit, or null if none>",

  "preflight": {
    "build_allowed": true,
    "tree_clean": true,
    "untracked_canonical_docs": false,
    "mixed_plane_dirty": false,
    "blocker": null
  },

  "retry_count": 0,
  "retry_budget_max": 2,
  "retry_budget_exhausted": false,

  "tests": {
    "pytest_status": "PASS | FAIL | INCONCLUSIVE | NOT_RUN",
    "pytest_count": 55,
    "ui_smoke_primary_status": "PASS | FAIL | INCONCLUSIVE | NOT_RUN",
    "ui_smoke_conditional_status": "PASS | FAIL | INCONCLUSIVE | NOT_RUN | NOT_REQUIRED",
    "ui_inspection_evidence_present": true,
    "validation_classification": "deterministic | environment-sensitive | live-data-sensitive | mixed"
  },

  "tree_cleanliness": {
    "build_branch_clean": true,
    "mixed_plane_residue": false,
    "untracked_canonical_docs": false
  },

  "promotion": {
    "attempted": true,
    "performed": true,
    "method": "fast-forward | merge | null",
    "ancestor_check_pass": true
  },

  "stop_condition": null,

  "ready_for_control_closeout": true,
  "safe_to_continue": true,

  "artifacts": {
    "ui_smoke_manifest":   "<path or null>",
    "ui_smoke_screenshot": "<path or null>",
    "run_log":             "<path or null>"
  },

  "notes": "<short, factual; no marketing language; ≤ 280 chars>"
}
```

### 14.2 Enum: `stop_condition`

Exactly one of the following, or `null` if no §8 condition fired:

- `null`
- `"PREFLIGHT_FAIL"` — §8.1
- `"MAX_RETRIES_EXCEEDED"` — §8.2
- `"SCOPE_AMBIGUITY"` — §8.3
- `"UNEXPECTED_CONTRACT_CHANGE"` — §8.4
- `"MIXED_PLANE_CONTAMINATION"` — §8.5
- `"UNCLEAR_TEST_RESULTS"` — §8.6
- `"SELECTION_BOUNDARY_REACHED"` — §8.7
- `"REPO_STATE_DRIFT"` — §8.8
- `"CONTROL_PLANE_CLOSEOUT_NEEDED"` — §8.9

### 14.3 Invariants the relay may rely on

These are hard worker obligations; violating them is itself a relay-visible defect:

- `protocol` is always the literal string `"CODEX_AUTONOMY_V1"`.
- `schema_version` is `"1"` for this doc.
- `retry_count` is an integer in `[0, retry_budget_max]`; never exceeds `retry_budget_max` (= 2 per §7).
- `retry_budget_exhausted == true` **iff** `retry_count == retry_budget_max` **and** validation is still not green.
- `promotion.performed == true` requires **all** §9 gates green **and** `tree_cleanliness.build_branch_clean == true` **and** `tree_cleanliness.mixed_plane_residue == false` **and** `tree_cleanliness.untracked_canonical_docs == false`.
- `ready_for_control_closeout == true` requires `promotion.performed == true` **and** `stop_condition == null`.
- `safe_to_continue == true` requires `stop_condition == null` **and** `tree_cleanliness.mixed_plane_residue == false` **and** `tree_cleanliness.untracked_canonical_docs == false`.
- `declared_plane` must match the plane actually touched; any cross-plane edit forces `stop_condition = "MIXED_PLANE_CONTAMINATION"` and `safe_to_continue = false`.

If any invariant is violated, the worker must set `stop_condition` to the corresponding §8 value and `safe_to_continue = false`, **not** silently repair the payload.

## 15. Relay decision policy

The relay consumes §14.1 and emits **exactly one** decision, in this precedence order. The first matching rule wins; later rules are not evaluated.

### 15.1 Decisions (enum)

- `CONTINUE` — slice is cleanly closed through PROMOTION; relay hands the §10.6 HANDBACK payload to the steward for **CONTROL-CLOSEOUT**. The relay **does not** run CONTROL-CLOSEOUT itself and **does not** start the next SELECTION.
- `RETRY_ALLOWED` — an in-slice corrective repair iteration is permitted under §7.
- `STOP_FOR_REVIEW` — run is paused for steward judgment; not a hard block, but the relay must not auto-advance.
- `BLOCKED` — hard stop; no retry, no continue. Steward intervention required before any further action on this slice.

### 15.2 Decision rules (evaluate top-down; first match wins)

1. **Schema / invariant violation** (any field missing, unknown enum value, invariant in §14.3 violated, or `protocol != "CODEX_AUTONOMY_V1"`)  
   → `BLOCKED`.

2. **Hard §8 conditions**  
   If `stop_condition` ∈ {`PREFLIGHT_FAIL`, `MIXED_PLANE_CONTAMINATION`, `UNEXPECTED_CONTRACT_CHANGE`, `REPO_STATE_DRIFT`, `SELECTION_BOUNDARY_REACHED`, `CONTROL_PLANE_CLOSEOUT_NEEDED`}  
   → `BLOCKED`.

3. **Retry budget exhausted**  
   If `stop_condition == "MAX_RETRIES_EXCEEDED"` **or** `retry_budget_exhausted == true`  
   → `STOP_FOR_REVIEW`.

4. **Judgment-required stop**  
   If `stop_condition` ∈ {`SCOPE_AMBIGUITY`, `UNCLEAR_TEST_RESULTS`}  
   → `STOP_FOR_REVIEW`.

5. **In-slice repair eligible**  
   If `stop_condition == null` **and** any of `tests.pytest_status`, `tests.ui_smoke_primary_status`, `tests.ui_smoke_conditional_status` is `FAIL` **and** `retry_count < retry_budget_max` **and** `tree_cleanliness.mixed_plane_residue == false` **and** `tests.validation_classification == "deterministic"`  
   → `RETRY_ALLOWED`.

6. **Inconclusive / non-deterministic validation without hard stop**  
   If `stop_condition == null` **and** any of the three test statuses is `INCONCLUSIVE`, or `tests.validation_classification` ∈ {`environment-sensitive`, `live-data-sensitive`, `mixed`} with a non-PASS test status  
   → `STOP_FOR_REVIEW`.  
   *(This aligns with OPERATING_RULES.md RULE 4 and the closeout runtime budget — the relay never spends more retries on non-deterministic failures.)*

7. **Clean closure**  
   If `stop_condition == null` **and** `promotion.performed == true` **and** `ready_for_control_closeout == true` **and** `safe_to_continue == true` **and** `tests.pytest_status == "PASS"` **and** `tests.ui_smoke_primary_status == "PASS"` **and** `tests.ui_smoke_conditional_status` ∈ {`PASS`, `NOT_REQUIRED`} **and** `tests.ui_inspection_evidence_present == true` **and** `tree_cleanliness.build_branch_clean == true`  
   → `CONTINUE`.

8. **Default / unclassified**  
   Anything that reaches this rule → `STOP_FOR_REVIEW`.  
   *(Safe default: the relay must not guess; the steward decides.)*

### 15.3 What the relay must never do

- Auto-run **CONTROL-CLOSEOUT**. `CONTINUE` means *hand back to steward for CONTROL-CLOSEOUT*, not *perform it*.
- Auto-start the next **SELECTION**. V1 never crosses the selection boundary (§2, §8.7).
- Extend `retry_budget_max` beyond 2, or grant retries after `stop_condition != null`.
- Reinterpret a `BLOCKED` decision as `STOP_FOR_REVIEW` to keep the run alive.
- Edit canonical steering docs (`docs/SOP/**`) or the slice spec to make a failing payload pass.
- Promote, rebase, force-push, or amend on behalf of the worker.
- Downgrade `schema_version` or translate between schema versions silently.

### 15.4 What the relay may do

- Record the decision, the input payload, and a one-line reason keyed to the triggering rule (e.g., `"rule 2: stop_condition=MIXED_PLANE_CONTAMINATION"`).
- On `RETRY_ALLOWED`, re-invoke the worker **once** for the same slice with `retry_count += 1` and the same slice spec; it must **not** expand scope, change plane, or edit the slice spec.
- On `CONTINUE`, surface the §10.6 HANDBACK payload (slice id, product commit SHA, baseline branch, artifact paths) to the steward and stop.
- On `STOP_FOR_REVIEW` or `BLOCKED`, surface the §10.6 HANDBACK payload and the fired §8 condition (if any) and stop.

### 15.5 Authority boundary reminder

The relay's authority is **strictly a subset** of Codex Autonomy v1's authority boundary (§2): `PREFLIGHT → BUILD → bounded REPAIR → BUILD-CLOSEOUT → PROMOTION` for **one** already-selected slice. A relay running outside that boundary is itself a §8.5 / §8.9 violation and must stop.

## 16. Last updated

2026-04-20 — §§14–15 added: machine-readable relay result schema and relay decision policy for Codex Autonomy v1. Control-plane / process-only pass; no product code changed, no orchestrator code changed, no sprint chartered. Prior: 2026-04-20 introduction of this protocol before **Sprint 003 SELECTION**.
