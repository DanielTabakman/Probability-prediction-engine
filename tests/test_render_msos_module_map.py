"""Tests for MSOS module map renderer."""

from __future__ import annotations

from pathlib import Path

from scripts.render_msos_module_map import (
    check_html_fresh,
    load_registry,
    render_html,
    write_html,
)


def test_registry_json_loads() -> None:
    repo = Path(__file__).resolve().parents[1]
    data = load_registry(repo / "docs/SOP/PPE_MODULE_REGISTRY.json")
    assert data["schema_version"] == 1
    assert len(data["modules"]) >= 4


def test_render_includes_module_display_names() -> None:
    repo = Path(__file__).resolve().parents[1]
    data = load_registry(repo / "docs/SOP/PPE_MODULE_REGISTRY.json")
    html = render_html(data, repo_root=repo)
    assert "Implied distribution" in html
    assert "Options Horizon" in html
    assert "Forward consistency" in html
    assert "Expression planner" in html
    assert "MSOS development dashboard" in html
    assert "Your work" in html
    assert "Can do now" in html


def test_html_matches_registry_ssot() -> None:
    repo = Path(__file__).resolve().parents[1]
    registry = repo / "docs/SOP/PPE_MODULE_REGISTRY.json"
    output = repo / "docs/SOP/assets/msos_module_map.html"
    assert output.is_file()
    assert check_html_fresh(registry_path=registry, output_path=output, repo_root=repo)


def test_write_html_roundtrip(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    registry = repo / "docs/SOP/PPE_MODULE_REGISTRY.json"
    out = tmp_path / "map.html"
    write_html(registry_path=registry, output_path=out, repo_root=repo)
    assert out.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")
