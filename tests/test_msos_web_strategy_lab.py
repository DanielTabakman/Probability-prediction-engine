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
    assert "fetchDisplayPayload" in text
    assert 'activeNavId="strategy-lab"' in text


def test_strategy_lab_belief_presets_interactive() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "beliefPresets.ts").read_text(encoding="utf-8")
    assert "BELIEF_PRESETS" in lib
    assert "higher" in lib
    assert "more_volatility" in lib
    assert "less_volatility" in lib

    builder = (MSOS_WEB / "src" / "components" / "BeliefBuilder.tsx").read_text(encoding="utf-8")
    assert '"use client"' in builder
    assert "belief-preset" in builder
    assert "aria-pressed" in builder

    panel = (MSOS_WEB / "src" / "components" / "StrategyLabInteractivePanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "StrategyLabInteractivePanel" in panel
    assert "buildOutcomeFromBelief" in panel

    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    assert "StrategyLabInteractivePanel" in content
    assert "Guided thesis draft — interactive belief controls ship in a follow-on slice." not in content

    styles = (MSOS_WEB / "src" / "app" / "globals.css").read_text(encoding="utf-8")
    assert ".belief-preset-grid" in styles


def test_strategy_lab_hierarchy_and_embed_boundary() -> None:
    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    assert "Strategy Lab · BTC options" in content
    assert "Live market data" in content
    assert "Demo data" in content
    assert "buildLabMetricsFromPayload" in content
    assert "StrategyLabInteractivePanel" in content
    assert "DEMO_FOOTER" in content

    panel = (MSOS_WEB / "src" / "components" / "StrategyLabInteractivePanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "Market vs your view" in panel
    assert "PpeEmbedBoundary" in panel
    assert 'className="legend"' in panel
    assert 'className="controls"' in panel

    lib = (MSOS_WEB / "src" / "lib" / "ppeDisplayPayload.ts").read_text(encoding="utf-8")
    assert "distribution_display_boundary" in lib
    assert "buildLabMetricsFromPayload" in lib

    embed = (MSOS_WEB / "src" / "components" / "PpeEmbedBoundary.tsx").read_text(encoding="utf-8")
    assert '"use client"' in embed
    assert "async function PpeEmbedBoundary" not in embed
    assert "ppeDisplayPayload" in embed
    assert "PPE_EMBED_ONLY_PARAM" in embed
    assert "iframe" in embed
    assert "degraded" in embed.lower() or "unavailable" in embed.lower()
    assert "prices_usd" in embed
    assert "ppe-summary-table" in embed
    assert "Deribit" in embed or "Live" in embed

    styles = (MSOS_WEB / "src" / "app" / "globals.css").read_text(encoding="utf-8")
    assert ".ppe-summary-table" in styles


def test_strategy_lab_fixtures_honest_lens_labels() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "strategyLabFixtures.ts").read_text(encoding="utf-8")
    assert "Live" in fixtures
    assert "Planned" in fixtures
    assert "Soon" in fixtures
    assert "BTC options" in fixtures


def test_thesis_confirmation_route_and_narrative() -> None:
    page = MSOS_WEB / "src" / "app" / "strategy-lab" / "confirm" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "ThesisConfirmationPanel" in text
    assert 'activeNavId="strategy-lab"' in text

    fixtures = (MSOS_WEB / "src" / "data" / "thesisConfirmFixtures.ts").read_text(encoding="utf-8")
    assert "Is this what you actually believe?" in fixtures

    panel = (MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx").read_text(encoding="utf-8")
    assert "thesisConfirmHeadline" in panel
    assert "Plan a paper trade" in panel
    assert "WORKSPACE_SAVED_LABEL" in panel
    assert "DEMO_FOOTER" in panel

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
    assert "Defined-risk range trade" in fixtures
    assert "Hyperliquid" in fixtures
    assert "Coming soon" in fixtures
    assert "Profit guarantee" in fixtures
    assert '"None"' in fixtures

    panel = (MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "Paper only" in panel
    assert "Save paper trade" in panel
    assert "DEMO_FOOTER" in panel
    assert "Why this structure" in panel
    assert "Structure types" in panel

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
    assert "DEMO_FOOTER" in monitor

    history = (MSOS_WEB / "src" / "components" / "HistoryContent.tsx").read_text(encoding="utf-8")
    assert "feed.entries" in history
    assert "Live trades" in history
    assert "not connected" in history

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
    assert "What did you take away?" in fixtures
    assert "nextSelectionRecommendation" in fixtures

    panel = (MSOS_WEB / "src" / "components" / "ConclusionContent.tsx").read_text(encoding="utf-8")
    assert "testerMetricsTemplate" in panel
    assert "Research preview" in panel

    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'href: "/learn"' in nav
