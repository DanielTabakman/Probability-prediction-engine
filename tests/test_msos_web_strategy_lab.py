"""MSOS P4 Strategy Lab scaffold witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_strategy_lab_route_and_shell() -> None:
    page = MSOS_WEB / "src" / "app" / "strategy-lab" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "AppShell" in text
    assert "StrategyLabContent" in text
    assert 'activeNavId="strategy-lab"' in text


def test_strategy_lab_hierarchy_and_embed_boundary() -> None:
    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    assert "Strategy Lab / PPE / Distribution summary" in content
    assert "Strategy Lab — research demo" in content
    assert "Live via PPE when embed wired" in content
    assert "Distribution summary (live PPE)" in content
    assert "PpeEmbedBoundary" in content
    assert "no live order transmitted" in content

    embed = (MSOS_WEB / "src" / "components" / "PpeEmbedBoundary.tsx").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_PPE_EMBED_URL" in embed
    assert "iframe" in embed
    assert "degraded" in embed.lower() or "Embed pending" in embed
    assert "distribution-summary" in embed
    assert "Live via PPE" in embed


def test_strategy_lab_fixtures_honest_lens_labels() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "strategyLabFixtures.ts").read_text(encoding="utf-8")
    assert "LIVE" in fixtures
    assert "Planned" in fixtures
    assert "Soon" in fixtures
    assert "BTC / Options" in fixtures


def test_thesis_confirmation_route_and_narrative() -> None:
    page = MSOS_WEB / "src" / "app" / "strategy-lab" / "confirm" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "ThesisConfirmationPanel" in text
    assert 'activeNavId="strategy-lab"' in text

    fixtures = (MSOS_WEB / "src" / "data" / "thesisConfirmFixtures.ts").read_text(encoding="utf-8")
    assert "Is this what you think is true?" in fixtures

    panel = (MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx").read_text(encoding="utf-8")
    assert "thesisConfirmHeadline" in panel
    assert "Proceed to expression planning" in panel
    assert "MSOS workflow store" in panel
    assert "no live order transmitted" in panel

    persistence = (MSOS_WEB / "src" / "lib" / "thesisPersistence.ts").read_text(encoding="utf-8")
    assert "msos.thesis.preview.v1" in persistence
    assert "exploring" in persistence
    assert "confirmed" in persistence

    lab = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    assert 'href="/strategy-lab/confirm"' in lab


def test_nav_enables_strategy_lab() -> None:
    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'id: "strategy-lab"' in nav
    assert 'href: "/strategy-lab"' in nav
    assert "disabled: true" not in nav.split("strategy-lab")[1].split("theses")[0]

    cc = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert 'href="/strategy-lab"' in cc


def test_expression_planning_route_and_narrative() -> None:
    page = MSOS_WEB / "src" / "app" / "strategy-lab" / "expression" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "ExpressionPlanningPanel" in text
    assert 'activeNavId="expression"' in text

    fixtures = (MSOS_WEB / "src" / "data" / "expressionPlanningFixtures.ts").read_text(
        encoding="utf-8"
    )
    assert "Defined-risk range structure" in fixtures
    assert "Hyperliquid" in fixtures
    assert "Pending" in fixtures
    assert "Profit guarantee" in fixtures
    assert '"None"' in fixtures

    panel = (MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "Order not transmitted" in panel
    assert "Simulate expression" in panel
    assert "no live order transmitted" in panel
    assert "Optimization basis" in panel
    assert "Expression families" in panel

    persistence = (MSOS_WEB / "src" / "lib" / "expressionPersistence.ts").read_text(encoding="utf-8")
    assert "msos.expression.preview.v1" in persistence
    assert "simulated" in persistence

    thesis_panel = (MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert 'href="/strategy-lab/expression"' in thesis_panel


def test_nav_enables_expression_planning() -> None:
    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'id: "expression"' in nav
    assert 'href: "/strategy-lab/expression"' in nav
    expression_block = nav.split('id: "expression"')[1].split("monitor")[0]
    assert "disabled: true" not in expression_block


def test_monitoring_history_routes_and_panels() -> None:
    monitor_page = MSOS_WEB / "src" / "app" / "monitor" / "page.tsx"
    history_page = MSOS_WEB / "src" / "app" / "history" / "page.tsx"
    assert monitor_page.is_file()
    assert history_page.is_file()
    monitor_page_text = monitor_page.read_text(encoding="utf-8")
    history_page_text = history_page.read_text(encoding="utf-8")
    assert "MonitorContent" in monitor_page_text
    assert "HistoryContent" in history_page_text
    assert "loadMonitorFeed" in monitor_page_text
    assert "loadHistoryFeed" in history_page_text

    monitor = (MSOS_WEB / "src" / "components" / "MonitorContent.tsx").read_text(encoding="utf-8")
    assert "feed.watchPanels" in monitor
    assert "no live order transmitted" in monitor

    history = (MSOS_WEB / "src" / "components" / "HistoryContent.tsx").read_text(encoding="utf-8")
    assert "feed.entries" in history
    assert "Executed" in history
    assert "no live positions connected" in history

    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'href: "/monitor"' in nav
    assert 'href: "/history"' in nav

    cc = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert "calibrationStrip" in cc
    assert 'href="/history"' in cc


def test_conclusion_learn_loop_route() -> None:
    page = MSOS_WEB / "src" / "app" / "learn" / "page.tsx"
    assert page.is_file()
    assert "ConclusionContent" in page.read_text(encoding="utf-8")
    assert 'activeNavId="learn"' in page.read_text(encoding="utf-8")

    fixtures = (MSOS_WEB / "src" / "data" / "conclusionFixtures.ts").read_text(encoding="utf-8")
    assert "What did you learn from this run?" in fixtures
    assert "VALIDATION_REALITY_CHECKS" in fixtures
    assert "nextSelectionRecommendation" in fixtures

    panel = (MSOS_WEB / "src" / "components" / "ConclusionContent.tsx").read_text(encoding="utf-8")
    assert "testerMetricsTemplate" in panel
    assert "Friends-first preview" in panel

    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'href: "/learn"' in nav
