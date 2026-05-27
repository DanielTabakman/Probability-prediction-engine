# Scripts layout

Operational CLIs and automation. Run from repo root: `python scripts/<name>.py`.

## Logical groups

| Group | Scripts | Notes |
|-------|---------|-------|
| **Smoke (UI)** | `implied_lab_ui_smoke_harness.py`, `run_implied_lab_ui_smoke.py`, `run_mvp1_dual_implied_lab_smoke.py` | Playwright + Streamlit; see [`docs/IMPLIED_LAB_SMOKE.md`](../docs/IMPLIED_LAB_SMOKE.md) |
| **Relay** | `relay_runtime_v0.py`, [`relay/canonical_docs.py`](relay/canonical_docs.py) | Codex autonomy runtime; canonical paths in `relay/` |
| **Orchestration** | `ppe_run.py`, `ppe_auto_select.py`, `ppe_auto_chain.py`, `ppe_google_docs_refresh.py`, `post_relay_continue.py`, `phase_orchestrator_v0.py` | Unified entry: `run_ppe.cmd` — see [`docs/SOP/PPE_UNIFIED_AUTO_RUN_V1.md`](../docs/SOP/PPE_UNIFIED_AUTO_RUN_V1.md) |
| **MSOS mirror** | `sync_msos_repo_truth.py`, `google_docs_sync.py`, `ppe_google_docs_refresh.py` | Local snapshot + optional Google Doc push (idle + CI) |
| **Evidence / logbook** | `log_event.py`, `write_last_run_report.py`, `count_validation_evidence.py`, `seed_validation_evidence_clock.py` | `artifacts/logbook/`, validation clocks |
| **Deploy (PowerShell)** | `*.ps1` | VPS, GitHub secrets, notifications |

See [`docs/SOP/JOB_REGISTRY_V1.md`](../docs/SOP/JOB_REGISTRY_V1.md) for relay job names.

## Subpackages

- [`relay/`](relay/) — shared relay constants (canonical doc paths).
- [`smoke/`](smoke/) — reserved namespace; smoke entry points remain at `scripts/` root for stable paths in docs and CI.
