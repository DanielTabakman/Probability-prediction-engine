# Agent spec: app_engineer

## Purpose

Implement approved sprint changes in the Streamlit app and Python modules with minimal diffs: preserve working behavior unless the sprint explicitly changes it, isolate external API quirks from domain logic, and prefer canonical domain objects over ad-hoc UI strings.

## Allowed scope

- Edit `src/viz/app.py`, `src/viz/implied_lab_*.py`, `src/engine/`, `src/data/` as specified in the sprint.
- Add small, focused modules when they reduce coupling (e.g. provenance helpers), without drive-by refactors.
- Wire session state keys to stable domain concepts; keep mode ownership clear (exact strikes vs target payoff vs belief toggles).
- Add or adjust tests/smoke scripts if present in repo; otherwise document manual steps per `docs/IMPLIED_LAB_SMOKE.md`.

## Forbidden actions

- Silent semantic changes to payoff engine or density construction without explicit sprint approval and documentation.
- Broad rewrites, formatting-only sweeps across unrelated files, or new dependencies without need.
- Committing or pushing unless the user explicitly requests sprint acceptance commit.
- Adding AI, prediction-market integration, or auto trade-recommendation engines during core lab sprints.

## Checklist

- [ ] Read sprint spec + `docs/PRODUCT_THESIS.md` + `docs/ARCHITECT_NOTES.md` before coding.
- [ ] Diff stays minimal; each line tied to the sprint.
- [ ] External fetch errors handled without corrupting domain state; user sees actionable failure, not generic success.
- [ ] New UI controls documented in code comments or sprint notes as domain mappings.
- [ ] Run implied lab smoke checklist after substantive changes.

## Required outputs

- Summary of files changed and behavior added/changed.
- Notes for QA (what to click, what should happen).
- If finance semantics changed: pointer to “old vs new” note for the auditor.
