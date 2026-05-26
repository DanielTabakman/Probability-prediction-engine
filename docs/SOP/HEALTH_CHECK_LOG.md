# Health check log

Repeatable one-screen entries from the codebase health check procedure. Newest first.

**Template fields (viz layer):** `app_py_lines`, `app_bitcoin_implied_lab_lines`, `touch_set_violations` (see [`VIZ_LAYER_DISCIPLINE_V1.md`](VIZ_LAYER_DISCIPLINE_V1.md)).

---

## 2026-05-25 — viz layer discipline + page extraction

```text
Date: 2026-05-25
viz_layer_discipline: shipped (SOP + cursor rule + check_viz_layer_budget + check_touch_set)
app_py_lines: 86 (shell max 300)
app_bitcoin_implied_lab_lines: 1999
touch_set_violations: 0
pytest: PASS (212)
pushable_gate: PASS (tier product + viz budget + ruff + full pytest)
dual_smoke: local before merge — python scripts/run_mvp1_dual_implied_lab_smoke.py
ci_ui_smoke_compact: GitHub job ui_smoke_compact (MVP1_compact_verification)
touch_set_automation: write_slice_touch_set + verify_slice_touch_set + pushable gate
top_risks: (none viz-layer blockers)
```

---

## 2026-05-19 — post-plan implementation pass

```text
Date: 2026-05-19
SHA: bf262a49d15d576d4271658c7449ad2fa873924d
Branch: build/commercial-validation-v0 (aligned with origin/main)
pytest: PASS (165 passed after health-check cleanup; was 161)
dual_smoke: SKIPPED (manual: python scripts/run_mvp1_dual_implied_lab_smoke.py)
doc_precedence: DRIFT fixed this pass (relay + JOB_REGISTRY + steward protocol → MVP1_FRONTIER)
untracked_SOP: 0 (working tree clean)
app.py_lines: 1986
relay_runtime_v0.py_lines: 1203
src_py_modules: 37
docs_md_files: 105
tests_importing_app: 0
open_BUILD: none — await steward SELECTION (POST_MVP1_OPERATOR_HARDENING_SELECTION.md)
steward_parallel: VPS CTA pending; paid-interest N
top_risks: app.py monolith; UI smokes not in CI; deploy workflow does not re-run pytest
```

**Doc alignment:** `PPE_INTEGRATED_STATUS`, `MVP1_FRONTIER`, and `HANDOFF` agree — operator hardening COMPLETE; no active BUILD slice.
