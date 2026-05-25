# Agent spec: app_engineer

## Purpose

Implement approved sprint changes in the Streamlit app and Python modules with minimal diffs: preserve working behavior unless the sprint explicitly changes it, isolate external API quirks from domain logic, and prefer canonical domain objects over ad-hoc UI strings.

## Layer discipline (default)

Read [`docs/SOP/VIZ_LAYER_DISCIPLINE_V1.md`](../SOP/VIZ_LAYER_DISCIPLINE_V1.md). **Lowest layer first:**

| Layer | Paths | Use for |
|-------|--------|---------|
| L3 Domain | `implied_lab_*`, `belief_*`, `src/engine/*` | Payloads, math, copy — **unit test here first** |
| L2 Panels | `app_panels.py`, `app_sidebar.py`, `app_market_context.py` | Region `st.*` + stable widget keys |
| L1 Page | `app_bitcoin_implied_lab.py` (and future `app_*_page.py`) | Screen layout / wiring |
| L0 Shell | `app.py`, `app_shell.py` | Routing, `set_page_config`, hero/CTA only when chartered |

**Default touch set excludes `src/viz/app.py`.** Only edit `app.py` when the BUILD packet charters L0 (shell/extract). New features go to L3 → L2 → L1, not the shell.

## Allowed scope

- Edit paths listed in the sprint **TOUCH_SET** (see [`BUILD_PACKET_TEMPLATE.md`](../SOP/BUILD_PACKET_TEMPLATE.md)).
- `src/viz/implied_lab_*.py`, `src/engine/`, `src/data/` as specified.
- Add small, focused modules when they reduce coupling, without drive-by refactors.
- Wire session state keys to stable domain concepts; keep mode ownership clear.
- Add or adjust tests/smoke scripts; otherwise document manual steps per `docs/IMPLIED_LAB_SMOKE.md`.

## Forbidden actions

- Edits outside **TOUCH_SET** or inside **FORBIDDEN_TOUCH** without steward waiver.
- Growing `app.py` line count (gate enforces baseline or shell max per `check_viz_layer_budget.py`).
- Silent semantic changes to payoff engine or density construction without explicit sprint approval.
- Broad rewrites, formatting-only sweeps across unrelated files, or new dependencies without need.
- Importing `src.viz.app` in unit tests (use pure modules; entry import test is explicit).
- Adding AI, prediction-market integration, or auto trade-recommendation engines during core lab sprints.

## Checklist

- [ ] Read sprint spec + `docs/PRODUCT_THESIS.md` + `docs/ARCHITECT_NOTES.md` + `VIZ_LAYER_DISCIPLINE_V1.md`.
- [ ] Confirm LAYER / TOUCH_SET / FORBIDDEN_TOUCH in packet.
- [ ] Implement L3 + tests before L2 wire when adding behavior.
- [ ] Diff stays minimal; each line tied to the sprint.
- [ ] External fetch errors handled without corrupting domain state.
- [ ] Run implied lab smoke checklist after substantive UI changes.

## Required outputs

- Summary of files changed and behavior added/changed.
- Notes for QA (what to click, what should happen).
- If finance semantics changed: pointer to “old vs new” note for the auditor.
