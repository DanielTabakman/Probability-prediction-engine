# TESTING_TIERS_V1

Purpose: keep **real** validation (unit tests, docker entry, Playwright smoke + screenshots) while cutting redundant work during iteration.

## Three speeds

| Speed | When | Command | What runs |
|-------|------|---------|-----------|
| **Fast** | WIP commits, control-plane tweaks | `python scripts/run_pushable_gate.py` | ruff + `pytest -m "not witness and not slow"` |
| **Full** | Before push / PR merge path | `python scripts/run_pushable_gate.py --pre-push` | ruff + full `pytest -q` (matches CI) |
| **Heavy** | Viz slice closeout only | smoke scripts (below) | Playwright + Streamlit + live data + PNGs |

**CI** (`.github/workflows/ci.yml`) always runs **full pytest** + **docker_entrypoint**. Local fast gate does not replace CI.

## Pytest markers

Auto-applied in `tests/conftest.py` (no per-test boilerplate required):

| Marker | Files / tests | Why excluded from fast gate |
|--------|---------------|----------------------------|
| `witness` | `*witness*`, `*charter*`, `test_msos_web_homepage` | Chapter closeout evidence; file-exists / queue JSON checks |
| `slow` | `test_phase_orchestrator_worktree`, `test_app_entrypoint_import` | Git subprocess / isolated import subprocess |

Run subsets manually:

```bash
# Fast (default local gate)
python -m pytest -q -m "not witness and not slow"

# Full (pre-push / debug parity with CI)
python -m pytest -q

# Witness only (after charter/queue doc changes)
python -m pytest -q -m witness
```

## Pushable gate

`scripts/run_pushable_gate.py`:

- **Default** — tier 0/1/2 with **fast pytest** (excludes `witness` + `slow`).
- **`--pre-push`** — same tier rules, **full pytest** on commits ahead of upstream. **Required before `git push`.**
- **`--full`** — force full pytest without pre-push scope (local debug).

Tier 0 (docs-only under `docs/`) unchanged: no ruff/pytest.

## UI smoke (heavy — not in pytest)

Playwright smoke stays **outside** default pytest (live Deribit/Yahoo; flaky in CI).

| Change | Run |
|--------|-----|
| Most viz slices | `python scripts/run_implied_lab_ui_smoke.py` (scenario **A** only) |
| Disagreement classification / harness semantics | Add scenario **C** when slice spec requires it (`OPERATING_RULES.md` Tier 2) |
| Harness-wide or dual MVP1/full-lab chrome | `python scripts/run_mvp1_dual_implied_lab_smoke.py` |
| Control-plane / relay only | **No smoke** |

Record `artifacts/ui_smoke/<run_id>/` manifest + PNG in PR or closeout evidence.

**Stop rule:** after 1–2 inconclusive smoke attempts, classify and report — do not infinite-retry (`OPERATING_RULES.md` → Closeout runtime budget).

## Agent / relay testing

- **In pytest:** `test_relay_runtime_v0.py`, steward/queue tests — fast, deterministic.
- **Not in pytest:** spinning up Cursor/ACP workers — use relay artifacts + slice closeout witnesses.

## What we removed (fat)

- `test_mvp1_sprint003_pytest_witness.py` — nested ruff + pinned pytest count (brittle; duplicated gate + CI).
- Full pytest on every intermediate commit — replaced by fast marker subset; full runs at pre-push + CI.

## Related docs

- Commit gates: [`COMMIT_POLICY_V1.md`](COMMIT_POLICY_V1.md)
- Closeout tiers: [`OPERATING_RULES.md`](OPERATING_RULES.md) → Validation tiers
- Implied lab smoke: [`IMPLIED_LAB_OPERATOR_RUNBOOK.md`](IMPLIED_LAB_OPERATOR_RUNBOOK.md)
