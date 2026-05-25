# VIZ_LAYER_DISCIPLINE_V1

**Status:** canonical · **Plane:** PRODUCT + EVIDENCE guardrails  
**Extends:** [`OPERATING_RULES.md`](OPERATING_RULES.md) (single-plane passes), [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md) (handoffs)

## Philosophy

**Thin shell, fat modules, lowest layer first.** The Streamlit entry (`app.py`) routes screens only. Each major screen lives in a **page module**. Panels render regions; domain modules build payloads and math; data modules fetch. Every BUILD slice declares a **touch set** so parallel agents do not collide on the same files.

## Layer model

| Layer | Paths | Put new work here when… |
|-------|--------|-------------------------|
| **L0 Shell** | `src/viz/app.py`, `src/viz/app_shell.py` | `set_page_config`, hero/CTA, global tutorial, which page is visible |
| **L1 Page** | `src/viz/app_*_page.py` (e.g. `app_bitcoin_implied_lab.py`) | Screen layout, columns, expanders, session-state wiring for one screen |
| **L2 Panels** | `app_panels.py`, `app_sidebar.py`, `app_market_context.py`, `app_market_reference.py` | `st.*` for one UI region; preserve widget keys |
| **L3 Domain** | `implied_lab_*`, `belief_*`, `frozen_evaluation_*`, `src/engine/*` | Payloads, classification, copy templates, math (**unit-test here first**) |
| **L4 Data** | `src/data/*` | HTTP/API, parsing, caching adapters |

### Decision tree (lowest layer first)

1. Can this be pure Python without Streamlit? → **L3** (+ `tests/test_*.py`).
2. Is it one panel/region? → **L2** (+ panel tests if logic is non-trivial).
3. Is it screen layout or wiring panels? → **L1** (one page module per screen).
4. Is it global shell or routing? → **L0** only when the sprint charters it.

**Do not** default new features to `app.py`. Historical sprints that say "`app.py` only" are historical; new work uses touch sets below.

## BUILD packet fields (required for PRODUCT slices)

```text
LAYER: <L0 | L1 | L2 | L3 | L4>   # primary layer of this slice
PRIMARY_MODULE: <repo-relative path>   # main file steward expects diffs in
TOUCH_SET: <comma-separated path prefixes; all changed files must match one>
FORBIDDEN_TOUCH: <prefixes that must not appear in the diff; default includes src/viz/app.py unless L0 Extract/Shell slice>
```

Example (panel-only slice):

```text
LAYER: L2
PRIMARY_MODULE: src/viz/app_panels.py
TOUCH_SET: src/viz/implied_lab_provenance.py, src/viz/app_panels.py, tests/test_trust_strip.py
FORBIDDEN_TOUCH: src/viz/app.py, src/viz/app_bitcoin_implied_lab.py
```

## Parallel multi-agent rules

- **One active slice per file** — if two slices need the same file, serialize in the phase plan or run an **Extract/REFACTOR** slice first.
- **Disjoint `TOUCH_SET`** — parallel BUILD branches only when changed paths do not overlap.
- **`dependsOnSliceId`** — when slice B wires UI that calls APIs added in slice A, A merges first (see [`PHASE_PLAN_CONTRACT_V1.md`](PHASE_PLANS/PHASE_PLAN_CONTRACT_V1.md)).
- **Roles (Streamlit stack):** data agent → L4; engine/domain → L3; panels → L2; page wiring → L1 (at most one agent on `app_bitcoin_implied_lab.py`); shell → L0 (rare).

## REFACTOR slices

Charter explicitly as **REFACTOR** (PRODUCT or EVIDENCE plane):

- **Zero** user-visible behavior change.
- Move code across layers; preserve Streamlit widget keys and session-state names.
- Evidence: `python -m pytest -q` + at least one implied-lab smoke scenario (see [`IMPLIED_LAB_SMOKE.md`](../IMPLIED_LAB_SMOKE.md)).

## Line budgets (enforced by `scripts/check_viz_layer_budget.py`)

Constants live in `scripts/check_viz_layer_budget.py`:

| Symbol | Meaning |
|--------|---------|
| `APP_PY_SHELL_MAX_LINES` | After page extraction: max lines in `app.py` (shell) |
| `APP_PY_BASELINE_LINES` | Before extraction: max lines; **no net increase** vs baseline |

| Phase | `app.py` rule | Page module |
|-------|----------------|-------------|
| **Before PR2 extract** | Line count ≤ `APP_PY_BASELINE_LINES` (frozen baseline) | N/A |
| **After PR2 extract** | Line count ≤ `APP_PY_SHELL_MAX_LINES` | `app_bitcoin_implied_lab.py` may be large; prefer L2/L3 for new logic |

Doc/code alignment: cite symbol names in this doc; tests assert script constants match (pattern (b) in [`CODE_DOCS_DRIFT_POLICY_V1.md`](CODE_DOCS_DRIFT_POLICY_V1.md)).

## Touch-set checker (optional per slice)

```bash
python scripts/check_touch_set.py --allowed-prefixes src/viz/app_panels.py --allowed-prefixes tests/ --paths $(git diff --name-only HEAD)
```

Not run on every commit by default; steward uses for parallel slice review.

## Steward rhythm

- **Chapter closeout:** record `app_py_lines`, `app_bitcoin_implied_lab_lines`, `touch_set_violations` in [`HEALTH_CHECK_LOG.md`](HEALTH_CHECK_LOG.md).
- **Before SELECTION:** if `app.py` is at baseline budget, charter an **Extract** slice before feature slices that would grow the shell.
- **Pushable gate:** PRODUCT diffs under `src/viz/` run `check_viz_layer_budget.py` (see [`COMMIT_POLICY_V1.md`](COMMIT_POLICY_V1.md)).

## References

- [`ARCHITECT_NOTES.md`](../ARCHITECT_NOTES.md) — product order and acceptance mindset
- [`README.md`](../../README.md) — do not import `src.viz.app` in unit tests
- [`IMPLIED_LAB_OPERATOR_RUNBOOK.md`](IMPLIED_LAB_OPERATOR_RUNBOOK.md) — operator procedures
