"""Tests for the founder portfolio registry."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_founder_pipeline_registry_validates() -> None:
    from scripts.founder_portfolio_registry import pipeline_by_id, validate_registry

    assert validate_registry(REPO) == []
    ppe = pipeline_by_id("ppe", REPO)
    autobuilder = pipeline_by_id("autobuilder", REPO)
    assert ppe is not None
    assert autobuilder is not None
    assert ppe["build_adapter"]["dispatch_commands_enabled"] is True
    assert ppe["scheduling"]["build_next_eligible"] is True
    assert ppe["scheduling"]["continuous_refill_eligible"] is False
    assert autobuilder["build_adapter"]["dispatch_commands_enabled"] is False
    assert autobuilder["scheduling"]["build_next_eligible"] is False
    assert autobuilder["scheduling"]["continuous_refill_eligible"] is False


def test_txline_is_not_registered_execution_ready_without_charter() -> None:
    from scripts.founder_portfolio_registry import pipeline_by_id

    assert pipeline_by_id("txline", REPO) is None


def test_dispatch_enablement_false_or_missing_remains_distinguishable_from_true(tmp_path: Path) -> None:
    from scripts.founder_portfolio_registry import _load_registry_cached, pipeline_by_id, validate_registry

    shutil.copytree(REPO / "docs", tmp_path / "docs")
    (tmp_path / "config").mkdir()
    registry = json.loads((REPO / "config/founder_pipeline_registry.json").read_text(encoding="utf-8"))
    ppe = next(item for item in registry["pipelines"] if item["pipeline_id"] == "ppe")

    false_registry = json.loads(json.dumps(registry))
    next(item for item in false_registry["pipelines"] if item["pipeline_id"] == "ppe")["build_adapter"][
        "dispatch_commands_enabled"
    ] = False
    (tmp_path / "config/founder_pipeline_registry.json").write_text(
        json.dumps(false_registry, indent=2) + "\n",
        encoding="utf-8",
    )
    assert validate_registry(tmp_path) == []
    assert pipeline_by_id("ppe", tmp_path)["build_adapter"]["dispatch_commands_enabled"] is False

    missing_registry = json.loads(json.dumps(registry))
    next(item for item in missing_registry["pipelines"] if item["pipeline_id"] == "ppe")["build_adapter"].pop(
        "dispatch_commands_enabled"
    )
    (tmp_path / "config/founder_pipeline_registry.json").write_text(
        json.dumps(missing_registry, indent=2) + "\n",
        encoding="utf-8",
    )
    _load_registry_cached.cache_clear()
    assert validate_registry(tmp_path) == []
    assert "dispatch_commands_enabled" not in pipeline_by_id("ppe", tmp_path)["build_adapter"]

    (tmp_path / "config/founder_pipeline_registry.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    _load_registry_cached.cache_clear()
    assert validate_registry(tmp_path) == []
    assert ppe["build_adapter"]["dispatch_commands_enabled"] is True


def test_non_ppe_dispatch_and_continuous_refill_remain_disabled(tmp_path: Path) -> None:
    from scripts.founder_portfolio_registry import validate_registry

    shutil.copytree(REPO / "docs", tmp_path / "docs")
    (tmp_path / "config").mkdir()
    registry = json.loads((REPO / "config/founder_pipeline_registry.json").read_text(encoding="utf-8"))
    autobuilder = next(item for item in registry["pipelines"] if item["pipeline_id"] == "autobuilder")
    autobuilder["build_adapter"]["dispatch_commands_enabled"] = True
    autobuilder["build_adapter"]["accepted_dispatcher_dependency"] = "msos_autobuilder_build_next_dispatcher"
    autobuilder["scheduling"]["continuous_refill_eligible"] = True
    (tmp_path / "config/founder_pipeline_registry.json").write_text(
        json.dumps(registry, indent=2) + "\n",
        encoding="utf-8",
    )

    errors = validate_registry(tmp_path)
    assert any("only ppe may enable one-shot dispatch" in error for error in errors)
    assert any("continuous_refill_eligible must remain false" in error for error in errors)
