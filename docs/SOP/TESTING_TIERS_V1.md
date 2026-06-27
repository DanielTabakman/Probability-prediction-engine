# TESTING_TIERS_V1

Purpose: keep **real** validation (unit tests, docker entry, Playwright smoke + screenshots) while cutting redundant work during iteration.

## Three speeds

| Speed | When | Command | What runs |
|-------|------|---------|-----------|
| **Scoped** | WIP commit with mappable diff | `python scripts/run_pushable_gate.py` | ruff + targeted test files + core safety net |
| **Fast** | WIP when scope unmapped | same | ruff + `pytest -m "not witness and not slow"` |
| **Full** | Before push / PR merge path | `python scripts/run_pushable_gate.py --pre-push` | ruff + full pytest (parallel + slow serial) |
| **Full + docker** | Before push when runtime/deps changed | `python scripts/run_pre_push_parity.py --docker` | full gate + **`CI / docker_entrypoint`** parity (build, import, Streamlit health) |
| **Heavy** | Viz slice closeout only | smoke scripts (below) | Playwright + Streamlit + live data + PNGs |

**CI** (`.github/workflows/ci.yml`) runs **full pytest** (parallel + slow serial), **`msos_web_build`** (`python scripts/verify_msos_web_build.py` — `next build` + Edge middleware witness), and **docker_entrypoint**. PRs labeled **`viz-change`** also run **CI / ui_smoke** (scenario A).

**Scheduled codebase health** (`.github/workflows/codebase-health.yml`) runs **Monday 14:30 UTC** on `main`:

```bash
python scripts/run_codebase_health_gate.py --repo-root .
```

Read-only: queue audit, `codebase_health_report`, `control_plane_consistency_check`. Fails on queue issues or consistency **errors** (warnings are logged only). Local dry-run before changing control-plane docs:

```bash
python scripts/run_codebase_health_gate.py --repo-root .
```

**Module coverage map:** [`MODULE_TEST_COVERAGE_V1.md`](MODULE_TEST_COVERAGE_V1.md) (regenerate via `python scripts/generate_module_test_coverage_map.py --write`).

## Pytest markers

Auto-applied in `tests/conftest.py`:

| Marker | Files / tests | Why excluded from fast gate |
|--------|---------------|----------------------------|
| `witness` | `*witness*`, `*charter*`, `test_msos_web_homepage`, `test_program_charter_invariants` | Chapter closeout evidence |
| `slow` | `test_phase_orchestrator_worktree`, `test_app_entrypoint_import` | Git subprocess / isolated import |

Manual subsets:

```bash
python -m pytest -q -m "not witness and not slow"    # fast
python -m pytest -q -n auto -m "not slow"            # parallel (then slow serial)
python -m pytest -q -m witness                         # witness only
```

Set `PPE_PYTEST_PARALLEL=0` to disable `-n auto` locally.

## Path-scoped pytest

`scripts/gate_pytest_scope.py` maps changed paths → test files. Used automatically on **fast** WIP gate when mapping succeeds.

Examples:

- `scripts/ppe_*.py` → `tests/test_ppe_*.py`
- `src/viz/**` → viz/UI test glob set
- `docs/SOP/PHASE_QUEUE.json` → falls back to marker-fast (queue witnesses)

Force scoped: `python scripts/run_pushable_gate.py --scoped`

## Pushable gate

- **Default** — tier 0/1/2; **scoped** when mappable else **fast** pytest.
- **`--pre-push`** — **full** pytest on commits ahead of upstream; when `apps/msos-web/` changed, also runs **`python scripts/verify_msos_web_build.py`** (full `next build`). **Required before `git push`.**
- **WIP MSOS commits** — `verify_msos_web_build.py --witness-only` (middleware Edge safety; no npm required locally).
- **`--full`** — force full pytest without pre-push scope.

## UI smoke (heavy — not in pytest)

| Change | Run |
|--------|-----|
| Most viz slices | `python scripts/run_implied_lab_ui_smoke.py` (scenario **A**) |
| Harness-wide / dual chrome | `python scripts/run_mvp1_dual_implied_lab_smoke.py` or slice `smokeMode: dual` |
| Control-plane / relay only | **No smoke** |

Deterministic worker (`ppe_slice_worker.py`): smoke slices default to **A**; set `smokeMode: dual` on slice or `PPE_DUAL_SMOKE=1` for dual.

Label PR **`viz-change`** to run CI Playwright smoke (scenario A).

## Witness consolidation

Closed chapter witnesses live in **`tests/test_program_charter_invariants.py`**. Active chapter witnesses remain separate (`test_msos_p3_charter_witness.py`, etc.).

## Related docs

- [`COMMIT_POLICY.md`](COMMIT_POLICY.md)
- [`OPERATING_RULES.md`](OPERATING_RULES.md) → Validation tiers
- [`IMPLIED_LAB_OPERATOR_RUNBOOK.md`](IMPLIED_LAB_OPERATOR_RUNBOOK.md)
