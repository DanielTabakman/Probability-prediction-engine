# VIZ_LAYER_DISCIPLINE_V1

**Status:** canonical · **Plane:** PRODUCT + EVIDENCE guardrails  
**Extends:** [`OPERATING_RULES.md`](OPERATING_RULES.md) (single-plane passes), [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md) (handoffs)

## Philosophy

**Thin shell, fat modules, lowest layer first.** The Streamlit entry (`app.py`) routes screens only. Each major screen lives in a **page module**. Panels render regions; domain modules build payloads and math; data modules fetch. Every BUILD slice declares a **touch set** in the phase plan so parallel agents do not collide on the same files.

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

Must match the active phase plan slice JSON (`touchSet` / `forbiddenTouch`).

```text
LAYER: <L0 | L1 | L2 | L3 | L4>
PRIMARY_MODULE: <repo-relative path>
TOUCH_SET: <comma-separated path prefixes>
FORBIDDEN_TOUCH: <prefixes; default src/viz/app.py for PRODUCT unless L0 shell slice>
```

## Phase plan JSON (required for PRODUCT slices)

Each `PRODUCT-PLANE` slice in `docs/SOP/PHASE_PLANS/*.json` must include:

```json
"touchSet": ["src/viz/app_panels.py", "tests/"],
"forbiddenTouch": ["src/viz/app.py", "src/viz/app_bitcoin_implied_lab.py"]
```

Validated by [`scripts/ppe_manifest.py`](../../scripts/ppe_manifest.py) when the manifest references the plan.

## Automatic enforcement (relay + gate + CI)

| When | What runs |
|------|-----------|
| **`run_slice.cmd` with phase plan** | [`scripts/relay/write_slice_touch_set.py`](../../scripts/relay/write_slice_touch_set.py) → `artifacts/control_plane/active_slice_touch_set.json` (gitignored) |
| **`python scripts/run_pushable_gate.py`** | If artifact exists (or env `PPE_SLICE_TOUCH_SET` / `PPE_SLICE_FORBIDDEN_TOUCH`) → [`check_touch_set.py`](../../scripts/check_touch_set.py); if `src/viz/` changed → [`check_viz_layer_budget.py`](../../scripts/check_viz_layer_budget.py) |
| **`post_relay_continue` on CONTINUE** | [`verify_slice_touch_set.py`](../../scripts/relay/verify_slice_touch_set.py) vs `baselineBranch` before CONTROL closeout |
| **GitHub CI** | Job **`ui_smoke_compact`**: [`run_mvp1_compact_ui_smoke_ci.py`](../../scripts/run_mvp1_compact_ui_smoke_ci.py) (`MVP1_compact_verification`) |
| **Health report** | `codebase_health_report` includes `viz_layer.app_py_lines`, `app_bitcoin_implied_lab_lines`, `budget_ok` |

**Local / steward before merge (stricter than CI):** `python scripts/run_mvp1_dual_implied_lab_smoke.py` when implied-lab behavior changes.

## Parallel multi-agent rules

- **One active slice per file** — serialize or REFACTOR first when two slices need the same file.
- **Disjoint `touchSet`** in phase plan — parallel BUILD branches only when paths do not overlap.
- **`dependsOnSliceId`** — merge order when APIs must land first ([`PHASE_PLAN_CONTRACT_V1.md`](PHASE_PLANS/PHASE_PLAN_CONTRACT_V1.md)).

## REFACTOR slices

Zero user-visible change; preserve widget keys; evidence: pytest + one smoke scenario ([`IMPLIED_LAB_SMOKE.md`](../IMPLIED_LAB_SMOKE.md)).

## Line budgets (`check_viz_layer_budget.py`)

| Symbol | Value | Rule |
|--------|-------|------|
| `APP_PY_SHELL_MAX_LINES` | 300 | `app.py` shell max (auto when page module exists) |
| `APP_PY_BASELINE_LINES` | 2109 | legacy baseline if page module absent |

Prefer new logic in L2/L3 — not unbounded growth of `app_bitcoin_implied_lab.py`.

## Manual override (tests / debugging)

```bash
export PPE_SLICE_TOUCH_SET=src/viz/app_panels.py,tests/
export PPE_SLICE_FORBIDDEN_TOUCH=src/viz/app.py
python scripts/run_pushable_gate.py
```

## Steward rhythm

- Chapter closeout: record viz fields in [`HEALTH_CHECK_LOG.md`](HEALTH_CHECK_LOG.md).
- SELECTION: every new PRODUCT slice gets concrete `touchSet` prefixes (not "`app.py` only").

## References

- [`COMMIT_POLICY_V1.md`](COMMIT_POLICY_V1.md) — gates and CI
- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md) — slice hooks
- [`IMPLIED_LAB_OPERATOR_RUNBOOK.md`](IMPLIED_LAB_OPERATOR_RUNBOOK.md) — smoke matrix
