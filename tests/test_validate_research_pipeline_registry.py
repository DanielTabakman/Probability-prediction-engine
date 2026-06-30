"""Tests for registry validation."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_validate_registry_ok() -> None:
    from scripts.validate_research_pipeline_registry import validate_registry

    assert validate_registry(REPO) == []


def test_validate_registry_catches_bad_test_reference(tmp_path: Path) -> None:
    from scripts.validate_research_pipeline_registry import validate_registry

    (tmp_path / "config").mkdir()
    bad = {
        "version": 1,
        "collectors": [],
        "tests": [{"id": "x", "reads_collectors": ["missing"], "script": "nope.py"}],
    }
    (tmp_path / "config" / "research_pipeline_registry.json").write_text(
        __import__("json").dumps(bad),
        encoding="utf-8",
    )
    errors = validate_registry(tmp_path)
    assert any("unknown collector" in e for e in errors)
