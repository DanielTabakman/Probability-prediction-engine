"""Pytest hooks for PPE test tiers (see docs/SOP/TESTING_TIERS_V1.md)."""

from __future__ import annotations

from pathlib import Path

import pytest

_WITNESS_STEMS = frozenset({"test_msos_web_homepage", "test_program_charter_invariants"})
_SLOW_STEMS = frozenset(
    {
        "test_phase_orchestrator_worktree",
        "test_app_entrypoint_import",
    }
)


def _stem(path: Path) -> str:
    return path.stem


@pytest.fixture(autouse=True)
def _ppe_test_loop_host(monkeypatch: pytest.MonkeyPatch) -> None:
    """CI has no VM env; allow stack helpers to start in unit tests."""
    monkeypatch.setenv("PPE_LOOP_HOST", "1")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "witness: charter/closeout evidence (CI + pre-push full gate)",
    )
    config.addinivalue_line(
        "markers",
        "slow: subprocess/git-heavy tests (CI + pre-push full gate)",
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        path = Path(str(getattr(item, "path", item.fspath)))
        stem = _stem(path)
        if "witness" in stem or "charter" in stem or stem in _WITNESS_STEMS:
            item.add_marker(pytest.mark.witness)
        if stem in _SLOW_STEMS:
            item.add_marker(pytest.mark.slow)
