"""Map changed repo paths to targeted pytest files for the fast scoped gate."""

from __future__ import annotations

from pathlib import Path

# Always run with scoped selection (safety net).
CORE_SCOPE_TESTS: tuple[str, ...] = (
    "tests/test_run_pushable_gate.py",
    "tests/test_manifest_schema_drift.py",
    "tests/test_repo_layer_map.py",
)

# Prefix -> test path globs (relative to repo root).
_PREFIX_TEST_GLOBS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("scripts/relay", ("tests/test_relay_runtime_v0.py",)),
    ("scripts/ppe_auto_select.py", ("tests/test_ppe_auto_select.py",)),
    ("scripts/ppe_", ("tests/test_ppe_*.py",)),
    ("scripts/research_", ("tests/test_research_*.py",)),
    ("scripts/founder_portfolio", ("tests/test_founder_portfolio.py", "tests/test_founder_portfolio_registry.py")),
    ("scripts/validate_founder_pipeline_registry.py", ("tests/test_founder_portfolio_registry.py",)),
    ("scripts/validate_research_pipeline_registry.py", ("tests/test_validate_research_pipeline_registry.py",)),
    ("config/founder_pipeline_registry.json", ("tests/test_founder_portfolio.py", "tests/test_founder_portfolio_registry.py")),
    ("scripts/run_cross_venue_tradeability_backtest.py", ("tests/test_cross_venue_tradeability_backtest.py",)),
    ("scripts/run_research_daily.py", ("tests/test_run_research_daily.py", "tests/test_research_pipeline_integration.py")),
    ("scripts/run_cross_venue_tradeability.py", ("tests/test_cross_venue_tradeability.py",)),
    ("scripts/run_cross_venue_collector_dev.py", ("tests/test_research_pipeline_integration.py",)),
    ("scripts/post_relay", ("tests/test_apply_control_closeout.py", "tests/test_write_last_run_report.py")),
    ("scripts/phase_orchestrator", ("tests/test_phase_orchestrator_worktree.py",)),
    (
        "scripts/implied_lab",
        (
            "tests/test_implied_lab_*.py",
            "tests/test_ui_smoke_*.py",
            "tests/test_scenario_timeout_defaults.py",
        ),
    ),
    ("scripts/run_implied_lab", ("tests/test_ui_smoke_*.py", "tests/test_scenario_timeout_defaults.py")),
    ("scripts/run_mvp1_dual", ("tests/test_ui_smoke_*.py", "tests/test_scenario_timeout_defaults.py")),
    ("scripts/run_pushable_gate", ("tests/test_run_pushable_gate.py", "tests/test_gate_pytest_scope.py")),
    ("scripts/verify_msos_web_build", ("tests/test_msos_web_workflow_persistence.py",)),
    (
        "scripts/run_codebase_health_gate",
        ("tests/test_codebase_health_gate.py", "tests/test_relay_runtime_v0.py"),
    ),
    ("scripts/gate_pytest_scope", ("tests/test_gate_pytest_scope.py",)),
    ("config/research_pipeline_registry.json", ("tests/test_research_pipeline_registry.py", "tests/test_research_archive_health.py", "tests/test_validate_research_pipeline_registry.py")),
    (
        "src/viz/",
        (
            "tests/test_mvp1_*.py",
            "tests/test_implied_lab_*.py",
            "tests/test_*candidate*.py",
            "tests/test_trust_strip.py",
            "tests/test_width_vol_*.py",
            "tests/test_directional_*.py",
            "tests/test_signup_*.py",
            "tests/test_commercial_*.py",
            "tests/test_ui_smoke_*.py",
            "tests/test_belief_*.py",
            "tests/test_app_entrypoint_import.py",
            "tests/test_cross_venue_*.py",
            "tests/test_research_summary.py",
        ),
    ),
    (
        "src/engine/",
        (
            "tests/test_belief_*.py",
            "tests/test_implied_lab_legibility.py",
            "tests/test_mvp1_decision_surface.py",
            "tests/test_reviewed_class_summary.py",
        ),
    ),
    (
        "src/models/",
        (
            "tests/test_belief_*.py",
            "tests/test_frozen_*.py",
        ),
    ),
    (
        "src/data/",
        (
            "tests/test_frozen_*.py",
        ),
    ),
    ("apps/msos-web/", ("tests/test_msos_web_homepage.py", "tests/test_msos_web_strategy_lab.py", "tests/test_msos_web_feedback.py", "tests/test_msos_web_cross_venue_panel.py")),
    (
        ".github/workflows/",
        ("tests/test_run_pushable_gate.py", "tests/test_codebase_health_gate.py"),
    ),
    ("pyproject.toml", ("tests/test_run_pushable_gate.py", "tests/conftest.py")),
    ("pytest.ini", ("tests/test_run_pushable_gate.py",)),
)

# If diff touches these, fall back to marker-fast (not scoped).
_FALLBACK_PREFIXES: tuple[str, ...] = (
    "docs/SOP/PHASE_QUEUE.json",
    "docs/SOP/PHASE_CHAPTER_BACKLOG.json",
    "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
    "docs/SOP/PHASE_PLANS/",
)

_MAX_SCOPED_FILES = 45


def _glob_tests(repo: Path, pattern: str) -> list[str]:
    return sorted(p.relative_to(repo).as_posix() for p in repo.glob(pattern))


def resolve_scoped_tests(changed_files: list[str], repo: Path) -> list[str] | None:
    """Return deduped test paths for a scoped run, or None to use marker-fast/full."""
    if not changed_files:
        return None

    norms = [p.replace("\\", "/") for p in changed_files]

    for prefix in _FALLBACK_PREFIXES:
        if any(n == prefix or n.startswith(prefix) for n in norms):
            return None

    selected: set[str] = set(CORE_SCOPE_TESTS)
    unmatched: list[str] = []

    for path in norms:
        matched = False
        if path.startswith("tests/") and path.endswith(".py"):
            selected.add(path)
            matched = True
            continue

        for prefix, globs in _PREFIX_TEST_GLOBS:
            if path.startswith(prefix) or path == prefix.rstrip("/"):
                for g in globs:
                    selected.update(_glob_tests(repo, g))
                matched = True
                break

        if not matched and not path.startswith("docs/"):
            unmatched.append(path)

    if unmatched:
        return None

    if len(selected) > _MAX_SCOPED_FILES:
        return None

    existing = [p for p in sorted(selected) if (repo / p).is_file()]
    return existing if existing else None
