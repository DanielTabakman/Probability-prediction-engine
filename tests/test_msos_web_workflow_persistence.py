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
    assert "Your workspace" in lib


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
    assert "requireProtectedIdentity" in thesis_route
    assert "upsertCurrentThesis" in thesis_route
    assert "identity.email" in thesis_route
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
    assert "savePaperTrade" in expression
    assert 'fetch("/api/theses/paper-trades"' in expression
    assert 'credentials: "include"' in expression


def test_paper_trades_api_route_exists() -> None:
    route = (
        MSOS_WEB / "src" / "app" / "api" / "theses" / "paper-trades" / "route.ts"
    ).read_text(encoding="utf-8")
    by_id = (
        MSOS_WEB / "src" / "app" / "api" / "theses" / "paper-trades" / "[id]" / "route.ts"
    ).read_text(encoding="utf-8")
    assert "appendPaperTrade" in route
    assert "clearPaperTrades" in route
    assert "listPaperTrades" in route
    assert "export async function POST" in route
    assert "export async function GET" in route
    assert "export async function DELETE" in route
    assert "deletePaperTrade" in by_id
    assert "closePaperTrade" in by_id
    assert "export async function PATCH" in by_id


def test_workflow_store_supports_paper_trade_manage() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosWorkflowStore.ts").read_text(encoding="utf-8")
    assert "deletePaperTrade" in lib
    assert "restorePaperTrade" in lib
    assert "clearPaperTrades" in lib
    assert "closePaperTrade" in lib
    assert "effectivePaperTradeStatus" in lib
    assert "paperTradeStatus" in lib


def test_workflow_store_supports_paper_trade_ledger() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosWorkflowStore.ts").read_text(encoding="utf-8")
    assert "appendPaperTrade" in lib
    assert "listPaperTrades" in lib
    assert "Paper trades" in lib


def test_monitor_history_feed_lists_paper_trades() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "monitorHistoryFeed.ts").read_text(encoding="utf-8")
    assert "listPaperTrades" in lib
    assert "paperTradeHistoryEntries" in lib
    assert "markLineForTrade" in lib
    assert "healthFromPaperTrades" in lib
    monitor = (MSOS_WEB / "src" / "components" / "MonitorContent.tsx").read_text(encoding="utf-8")
    watch_list = (MSOS_WEB / "src" / "components" / "MonitorWatchList.tsx").read_text(encoding="utf-8")
    history = (MSOS_WEB / "src" / "components" / "HistoryContent.tsx").read_text(encoding="utf-8")
    assert "PaperTradeManageActions" not in monitor
    assert "MonitorWatchList" in monitor
    assert "Delete" in watch_list
    assert "panel.tradeId" in watch_list
    assert "PaperTradeManageActions" in history


def test_confirm_page_uses_live_lab_context() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "buildThesisLabContext.ts").read_text(encoding="utf-8")
    panel = (MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "buildCompareColumnsFromLab" in lib
    assert "buildThesisDraftFromLab" in lib
    assert "buildGapDescription" in lib or "You expect a lower finish than options imply" in lib
    assert "buildThesisLabContext" in panel or "buildCompareColumnsFromLab" in panel
    assert "fetchDisplayPayloadClient" in panel
    assert "resolveDisplayAssetMeta" in panel
    assert "assetMeta" in panel


def test_paper_trade_detail_route_exists() -> None:
    page = (MSOS_WEB / "src" / "app" / "monitor" / "paper" / "[id]" / "page.tsx").read_text(
        encoding="utf-8"
    )
    assert "getPaperTradeById" in page
    assert "PaperTradeDetailContent" in page


def test_expression_save_returns_error_surface() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "expressionPersistence.ts").read_text(encoding="utf-8")
    panel = (MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "deletePaperTradeById" in lib
    assert "deletePaperTradeWithUndo" in lib
    assert "restorePaperTrade" in lib
    assert "saveError" in panel


def test_paper_trade_detail_redirects_when_missing() -> None:
    page = (MSOS_WEB / "src" / "app" / "monitor" / "paper" / "[id]" / "page.tsx").read_text(
        encoding="utf-8"
    )
    assert 'redirect("/monitor")' in page
    assert "notFound()" not in page


def test_delete_from_detail_hard_navigates_to_monitor() -> None:
    actions = (MSOS_WEB / "src" / "components" / "PaperTradeManageActions.tsx").read_text(encoding="utf-8")
    nav = (MSOS_WEB / "src" / "lib" / "monitorNav.ts").read_text(encoding="utf-8")
    assert "goToMonitorAfterDelete" in actions
    assert "window.location.assign" in nav


def test_workflow_session_scoping_exists() -> None:
    session = (MSOS_WEB / "src" / "lib" / "msosSession.ts").read_text(encoding="utf-8")
    middleware = (MSOS_WEB / "src" / "middleware.ts").read_text(encoding="utf-8")
    owner = (MSOS_WEB / "src" / "lib" / "msosWorkflowOwner.ts").read_text(encoding="utf-8")
    assert "msos_session" in session
    assert "MSOS_SESSION_COOKIE" in middleware
    assert "resolveWorkflowOwnerId" in owner


def test_display_currency_module_exists() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "displayCurrency.ts").read_text(encoding="utf-8")
    setup = (MSOS_WEB / "src" / "components" / "LabSetupRow.tsx").read_text(encoding="utf-8")
    sidebar = (MSOS_WEB / "src" / "components" / "AppSidebar.tsx").read_text(encoding="utf-8")
    assert "formatMoney" in lib
    assert "EUR" in lib
    assert "CurrencySelect" in setup
    assert "LabSetupRow" in setup
    assert "CurrencySelect" not in sidebar


def test_expression_chart_fullscreen_frame() -> None:
    frame = (MSOS_WEB / "src" / "components" / "ExpressionPayoffChartFrame.tsx").read_text(
        encoding="utf-8"
    )
    panel = (MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "chart-fullscreen-backdrop" in frame
    assert "Monitor paper trades" in panel
    assert 'credentials: "include"' in (
        MSOS_WEB / "src" / "lib" / "expressionPersistence.ts"
    ).read_text(encoding="utf-8")


def test_confirm_page_pending_lifecycle() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "thesisConfirmFixtures.ts").read_text(encoding="utf-8")
    panel = (MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "lifecycleDisplayId" in fixtures
    assert '"Pending"' in fixtures or "'Pending'" in fixtures
    assert "lifecycleDisplayId" in panel


def test_homepage_product_window_rich_preview() -> None:
    window = (MSOS_WEB / "src" / "components" / "ProductWindow.tsx").read_text(encoding="utf-8")
    assert "callout" in window
    assert "Thesis gap" in window
    assert "Demo" in window


def test_verify_msos_web_build_script_and_ci() -> None:
    import subprocess
    import sys

    repo = REPO_ROOT
    proc = subprocess.run(
        [sys.executable, "scripts/verify_msos_web_build.py", "--witness-only"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    ci = (repo / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "msos_web_build:" in ci
    assert "verify_msos_web_build.py" in ci
    gate = (repo / "scripts" / "run_pushable_gate.py").read_text(encoding="utf-8")
    assert "_msos_web_gate_commands" in gate


def test_middleware_edge_safe_session_cookie() -> None:
    """Middleware runs on Edge — must not import Node crypto (runtime 500 on every route)."""
    middleware = (MSOS_WEB / "src" / "middleware.ts").read_text(encoding="utf-8")
    assert 'from "crypto"' not in middleware
    assert "crypto.randomUUID()" in middleware
    assert "MSOS_SESSION_COOKIE" in middleware


def test_workflow_auth_split_avoids_import_cycle() -> None:
    """Route auth must not import next/headers; identity core must not import workflow owner."""
    auth = (MSOS_WEB / "src" / "lib" / "msosWorkflowAuth.ts").read_text(encoding="utf-8")
    core = (MSOS_WEB / "src" / "lib" / "msosIdentityCore.ts").read_text(encoding="utf-8")
    owner = (MSOS_WEB / "src" / "lib" / "msosWorkflowOwner.ts").read_text(encoding="utf-8")
    assert "next/headers" not in auth
    assert "next/headers" in owner
    assert "msosWorkflowOwner" not in core
    assert "msosIdentityCore" in auth


def test_command_center_uses_snapshot_summary() -> None:
    page = (MSOS_WEB / "src" / "app" / "command-center" / "page.tsx").read_text(encoding="utf-8")
    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert "loadCommandCenterSummary" in page
    assert "loadWorkflowSummary" in page
    assert "workflow" in content
    assert "summary.currentWork" in content
    lib = (MSOS_WEB / "src" / "lib" / "commandCenterSummary.ts").read_text(encoding="utf-8")
    assert "From your saved market snapshots" in lib


def test_workflow_store_json_shape_documented() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosWorkflowStore.ts").read_text(encoding="utf-8")
    assert "msos_workflow_v1.json" in lib
    assert "currentThesisId" in lib
    assert "upsertCurrentExpression" in lib
