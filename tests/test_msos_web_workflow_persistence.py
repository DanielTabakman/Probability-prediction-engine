"""MSOS workflow persistence v1 — product slice witness (server store + Command Center)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_workflow_store_module_exists() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosWorkflowStore.ts").read_text(encoding="utf-8")
    assert "loadWorkflowSummary" in lib
    assert "upsertCurrentThesis" in lib
    assert "MSOS_WORKFLOW_STORE_PATH" in lib
    assert "From MSOS workflow store" in lib


def test_thesis_api_routes_exist() -> None:
    thesis_route = (MSOS_WEB / "src" / "app" / "api" / "theses" / "route.ts").read_text(encoding="utf-8")
    expression_route = (
        MSOS_WEB / "src" / "app" / "api" / "theses" / "expression" / "route.ts"
    ).read_text(encoding="utf-8")
    summary_route = (
        MSOS_WEB / "src" / "app" / "api" / "theses" / "summary" / "route.ts"
    ).read_text(encoding="utf-8")
    assert "export async function GET" in thesis_route
    assert "export async function PUT" in thesis_route
    assert "upsertCurrentThesis" in thesis_route
    assert "upsertCurrentExpression" in expression_route
    assert "loadWorkflowSummary" in summary_route


def test_persistence_libs_call_server_api() -> None:
    thesis = (MSOS_WEB / "src" / "lib" / "thesisPersistence.ts").read_text(encoding="utf-8")
    expression = (MSOS_WEB / "src" / "lib" / "expressionPersistence.ts").read_text(encoding="utf-8")
    assert "fetchThesisRecord" in thesis
    assert 'fetch("/api/theses"' in thesis
    assert "persistThesisRecord" in thesis
    assert "fetchExpressionRecord" in expression
    assert 'fetch("/api/theses/expression"' in expression


def test_command_center_uses_snapshot_summary() -> None:
    page = (MSOS_WEB / "src" / "app" / "command-center" / "page.tsx").read_text(encoding="utf-8")
    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert "loadCommandCenterSummary" in page
    assert "summary.kpis" in content
    assert "summary.currentWork" in content
    assert "From PPE snapshots" in content
    assert "Preview data healthy" not in content


def test_workflow_store_json_shape_documented() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosWorkflowStore.ts").read_text(encoding="utf-8")
    assert "msos_workflow_v1.json" in lib
    assert "currentThesisId" in lib
    assert "upsertCurrentExpression" in lib
