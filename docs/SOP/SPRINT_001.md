# Sprint ID
SPRINT_001

## Title
Sprint 1 layout + summary closure (implied lab one-screen)

## Objective
Deliver a coherent **one-screen implied lab** experience aligned to `docs/SPRINT_1_SPEC.md`: chart high on the page, two-column layout (controls left; chart + summary right), and a complete summary card with stable semantics. Keep visible outputs consistent by reducing/avoiding duplicated widget-driven derivations in touched areas.

## Vision constraints
- Phase: **one-screen implied lab** — chart high, two columns, summary visible within one screen’s story (`docs/VISION/PHASE_VISION_CURRENT.md`).
- Semantic: market-implied = **priced / risk-neutral distribution**, not “true belief” (`docs/SEMANTIC_CONTRACTS.md`).
- Semantic: strategy families = **fit / explore**, not “recommended trade” (`docs/SEMANTIC_CONTRACTS.md`).
- Deferred: new AI features, prediction-market integration, framework migration, major engine/DB refactors (`docs/SPRINT_1_SPEC.md`, `docs/SOP/CURRENT_FRONTIER.md`).

## Scope in
- Rework `src/viz/app.py` implied lab layout so:
  - chart is visible near the top with minimal scroll
  - two-column structure: controls left; chart + summary right
- Ensure summary card is visible and includes (when available):
  - strategy name
  - net debit/credit (sign conventions preserved)
  - max gain / max loss
  - breakevens
  - fit quality if available
- Move advanced math/calculation details behind expanders by default (where currently visible by default in the implied lab section).
- Tighten UI labels/copy in touched areas to conform to `docs/SEMANTIC_CONTRACTS.md` (especially market-implied vs belief; fit vs recommendation).
- Localized refactor allowed **only** to support layout/summary coherence and reduce duplicated derivation in touched areas (e.g., a single “derived outputs” bundle used by chart + summary).

## Scope out
- Full “single session/state layer across all widgets” refactor (frontier candidate #2) unless it is the smallest safe change needed to eliminate obvious duplicated visible-output derivations in the implied lab section.
- New strategy logic beyond what is needed to surface existing summary fields coherently.
- Any new external integrations (Polymarket, new data providers).
- Broad refactors across unrelated modules.

## Files likely to change
- `src/viz/app.py` (primary)
- Potentially (only as needed for consistent summary wiring / labels):
  - `src/viz/implied_lab_derive.py`
  - `src/viz/implied_lab_provenance.py`
  - `src/viz/implied_lab_smoke_harness.py` (only if the harness must track UI relocation without loosening checks)
  - `src/viz/belief_disagreement_hints.py`
  - `src/viz/disagreement_thresholds.py`
- Tests (only if logic changes require it):
  - `tests/test_*.py`

## Current behavior to preserve
- App still launches via Streamlit and renders the implied lab without requiring a separate “run” button (spinners acceptable).
- Primary automated UI smoke remains meaningful (do not weaken checks to “make it pass”).
- Sign conventions remain consistent across chart and summary:
  - net debit = positive total cost; net credit = negative total cost (`docs/SEMANTIC_CONTRACTS.md`).
- “Belief off” does not show belief curve; “Belief on” shows belief curve (per smoke checklist).
- Verification section still renders and remains traceable (do not hide breakage with generic try/except).

## Desired behavior
- The implied lab reads as one story: controls clearly on the left, chart and summary clearly on the right, with the chart visible near the top.
- The summary card provides the key trade stats without requiring scrolling into advanced sections.
- Labels consistently distinguish:
  - market-implied priced distribution vs user belief
  - disagreement as descriptive
  - fit/exploration vs recommendation

## Acceptance criteria
- [ ] Chart is visible near the top and the implied lab is clearly two-column (controls left; chart+summary right)
- [ ] Summary card is visible and includes the Sprint 1 required fields (or explicitly shows “not available” for any legitimately missing field)
- [ ] UI copy/labels in touched areas comply with `docs/SEMANTIC_CONTRACTS.md` (no disallowed phrases)
- [ ] Unit tests run and pass
- [ ] Automated UI smoke run and passes (primary scenario)
- [ ] App launch-and-inspect completed with the manual smoke checklist items relevant to layout/summary/verification
- [ ] Touched-area cleanup performed (imports, dead code, obvious duplication) without expanding scope
- [ ] Risks/caveats and any unverified items are explicitly reported

## Test plan
Run from repo root.

1. **Unit tests**
   - `python -m unittest discover -s tests -p "test_*.py" -v`

2. **Primary automated UI smoke**
   - `python scripts/run_implied_lab_ui_smoke.py`

3. **Local app launch (headless ready)**
   - `python -m streamlit run src/viz/app.py --server.headless true --server.port 8515`
   - Confirm readiness (HTTP 200 at `http://127.0.0.1:8515/` and/or Streamlit log showing local URL).

4. **Local visual inspection (manual checklist)**
   - Use `docs/IMPLIED_LAB_SMOKE.md` items: 0, 1, 2, 8, 9 (and any others impacted by the layout/summary change).

## Cleanup expectations
- Allowed:
  - reduce duplicated derivation in the implied lab section if it improves chart/summary consistency
  - small local reorganizations to keep `app.py` readable around the implied lab layout blocks
  - remove unused imports/locals and stale UI text in touched sections
- Not allowed:
  - sweeping refactors across multiple subsystems
  - changing semantics to “make it nicer” without matching `docs/SEMANTIC_CONTRACTS.md`

## Escalation triggers
Escalate to manager instead of guessing if:
- The layout/summary change requires a broad session-state rewrite to avoid regressions.
- The smoke harness begins failing due to external network/data instability and it is unclear what is “acceptable” for local verification.
- Copy/semantics decisions are ambiguous (market-implied vs belief, fit vs recommendation wording).
- The implied lab’s summary fields can’t be produced without introducing new strategy logic.

## Definition of done
Done means:
- acceptance criteria met
- test plan executed with recorded results
- launch-and-inspect completed for changed UI
- touched-area cleanup complete
- unresolved risks / unverified items clearly reported

## Pre-edit plan template
### Understanding
### Files to inspect
### Files expected to change
### Smallest viable implementation path
### Tests to run
### Cleanup candidates
### Human attention needed

## Closeout report template
### Objective
### Files changed
### What changed
### Exact commands run
### Tests/results
### App launch/inspection evidence
### What was confirmed
### What remains unverified
### Cleanup performed
### Risks / caveats
### Proposed next sprint options
