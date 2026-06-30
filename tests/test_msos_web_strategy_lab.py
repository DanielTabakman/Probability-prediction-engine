"""MSOS P4 Strategy Lab scaffold witness."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
SOP = REPO_ROOT / "docs" / "SOP"


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
    assert "ExpiryPicker" in builder

    panel = (MSOS_WEB / "src" / "components" / "StrategyLabInteractivePanel.tsx").read_text(
        encoding="utf-8"
    )
    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    assert "StrategyLabInteractivePanel" in panel
    assert "PpeEmbedBoundary" in panel
    assert "beliefPdfPct" in panel
    assert "selectedExpiry" in panel
    assert "BeliefBuilder" in panel
    assert "belief-axis-pair" in builder
    assert "Higher" in builder
    assert "More vol" in builder
    assert "PpeEmbedBoundary" not in content
    assert "buildOutcomeFromTuning" in panel
    assert "Guided thesis draft — interactive belief controls ship in a follow-on slice." not in content

    tuning = (MSOS_WEB / "src" / "lib" / "beliefTuning.ts").read_text(encoding="utf-8")
    assert "fetchBeliefOverlayPdf" in tuning
    assert "nudgeTuning" in tuning
    assert "loadStoredBeliefTuning" in tuning

    fine = (MSOS_WEB / "src" / "components" / "BeliefFineTuning.tsx").read_text(encoding="utf-8")
    assert "slider-input" in fine

    presets = (MSOS_WEB / "src" / "lib" / "beliefPresets.ts").read_text(encoding="utf-8")
    assert "buildOutcomeFromTuning" in presets

    styles = (MSOS_WEB / "src" / "app" / "globals.css").read_text(encoding="utf-8")
    assert ".belief-axis-pair" in styles
    assert ".belief-preset" in styles
    assert ".slider-input" in styles
    assert "Reset to market" in builder


def test_strategy_lab_hierarchy_and_embed_boundary() -> None:
    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    shell = (MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx").read_text(encoding="utf-8")
    work = (MSOS_WEB / "src" / "components" / "StrategyLabWorkSection.tsx").read_text(encoding="utf-8")
    picker = (MSOS_WEB / "src" / "components" / "ExpiryPicker.tsx").read_text(encoding="utf-8")
    copy = (MSOS_WEB / "src" / "lib" / "strategyLabCopy.ts").read_text(encoding="utf-8")
    assert "StrategyLabClientShell" in content
    assert "fetchDisplayPayloadClient" in shell
    assert "Sample mode" in copy
    assert "LabSetupRow" in work

    panel = (MSOS_WEB / "src" / "components" / "StrategyLabInteractivePanel.tsx").read_text(
        encoding="utf-8"
    )
    builder = (MSOS_WEB / "src" / "components" / "BeliefBuilder.tsx").read_text(encoding="utf-8")
    assert "Market vs your view" in panel
    assert "PpeEmbedBoundary" in panel
    assert "beliefPdfPct" in panel
    assert "selectedExpiry" in panel
    assert 'className="legend chart-curve-legend"' in panel or 'className="legend"' in panel
    assert "BeliefFineTuning" in panel
    assert "belief-axis-pair" in builder

    lib = (MSOS_WEB / "src" / "lib" / "ppeDisplayPayload.ts").read_text(encoding="utf-8")
    assert "distribution_display_boundary" in lib
    assert "buildLabMetricsFromPayload" in lib

    embed = (MSOS_WEB / "src" / "components" / "PpeEmbedBoundary.tsx").read_text(encoding="utf-8")
    assert '"use client"' in embed
    assert "LabeledDistributionChart" in embed
    assert "resolveCurveLabels" in embed
    assert "Black–Scholes lognormal" in embed or "curve_labels" in embed
    assert "beliefPdfPct" in embed
    assert "dataMode" in embed
    assert "ppeDisplayPayload" in embed
    assert "degraded" in embed.lower() or "unavailable" in embed.lower()
    assert "prices_usd" in embed
    assert "ppe-summary-table" in embed
    assert "Deribit" in embed or "Live" in embed
    labeled = (MSOS_WEB / "src" / "components" / "LabeledDistributionChart.tsx").read_text(
        encoding="utf-8"
    )
    assert "BTC price at expiry" in labeled
    assert "graph-labeled" in labeled
    assert "ChartCurveLegend" in labeled
    assert "Black–Scholes lognormal" in labeled

    curve_labels = (MSOS_WEB / "src" / "lib" / "chartCurveLabels.ts").read_text(encoding="utf-8")
    assert "Market view [Black–Scholes lognormal]" in curve_labels

    styles = (MSOS_WEB / "src" / "app" / "globals.css").read_text(encoding="utf-8")
    assert ".ppe-summary-table" in styles
    assert ".expiry-picker" in styles
    assert ".lab-data-banner" in styles


def test_strategy_lab_fixtures_honest_lens_labels() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "strategyLabFixtures.ts").read_text(encoding="utf-8")
    assert "Live" in fixtures
    assert "Planned" in fixtures
    assert "Soon" in fixtures
    assert "BTC options" in fixtures


def test_strategy_lab_asset_switcher_and_eth_copy() -> None:
    shell = (MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx").read_text(encoding="utf-8")
    payload_lib = (MSOS_WEB / "src" / "lib" / "ppeDisplayPayload.ts").read_text(encoding="utf-8")
    catalog_lib = (MSOS_WEB / "src" / "lib" / "ppeAssetCatalog.ts").read_text(encoding="utf-8")
    picker = (MSOS_WEB / "src" / "components" / "LabAssetPicker.tsx").read_text(encoding="utf-8")
    thesis_ctx = (MSOS_WEB / "src" / "lib" / "buildThesisLabContext.ts").read_text(encoding="utf-8")
    fixtures = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")

    assert 'LAB_ASSET_QUERY_PARAM = "asset"' in payload_lib
    assert "KNOWN_LAB_ASSET_IDS" in payload_lib
    assert "normalizeLabAssetId" in payload_lib
    assert "buildDisplayApiUrl" in payload_lib
    assert "price_axis_label" in payload_lib
    assert "ETH price at expiry" in payload_lib
    assert "NVDA price at expiry" in payload_lib
    assert '"NVDA"' in payload_lib
    assert "fetchDisplayPayloadClient(" in shell
    assert "LabAssetPicker" in shell
    assert "fetchAssetCatalog" in shell
    assert "catalog.json" in catalog_lib
    assert "asset_catalog" in catalog_lib
    assert "lab-asset-picker" in picker
    assert 'data-tour="lab-asset"' in picker
    assert "switchable" in picker
    assert "active && assets.length <= 1" in picker
    assert "buildStrategyLabPath" in payload_lib
    assert "assetMeta.label" in shell

    assert "resolveDisplayAssetMeta" in thesis_ctx
    assert "I think ${asset.id} will" in thesis_ctx

    assert '"ETH"' in payload_lib
    assert '"NVDA"' in catalog_lib or '"NVDA"' in payload_lib
    assert "KNOWN_LAB_ASSET_IDS" in payload_lib


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

    lab = (MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx").read_text(encoding="utf-8")
    assert 'buildWorkflowStepHref("confirm"' in lab


def test_confirm_page_propagates_selected_asset() -> None:
    """Confirm must honor ?asset= for any catalog id (SOL, NVDA, …), not BTC fixtures."""
    panel = (MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx").read_text(
        encoding="utf-8"
    )
    lib = (MSOS_WEB / "src" / "lib" / "buildThesisLabContext.ts").read_text(encoding="utf-8")
    payload_lib = (MSOS_WEB / "src" / "lib" / "ppeDisplayPayload.ts").read_text(encoding="utf-8")
    asset_lib = (MSOS_WEB / "src" / "lib" / "strategyLabAsset.ts").read_text(encoding="utf-8")

    assert "useResolvedLabAssetId" in panel
    assert "resolveDisplayAssetMeta(displayPayload, assetId)" in panel
    assert "buildThesisRestatement(" in panel
    assert "buildConfirmChecklist(expiry, Boolean(displayPayload), assetMeta)" in panel
    assert "buildThesisDraftFromLab(payload, storedTuning, storedExpiry, assetMeta)" in panel
    assert "fetchDisplayPayloadClient(assetId)" in panel
    assert "buildWorkflowStepHref(\"plan\", assetId)" in panel

    assert "resolveLabAssetId" in asset_lib
    assert "STRATEGY_LAB_ASSET_STORAGE_KEY" in asset_lib
    assert "ABSOLUTE_FALLBACK_ASSET_ID" in asset_lib

    assert "I think ${asset.id} will" in lib
    assert "buildGapDescription" in lib
    assert "assetId: asset.id" in lib
    assert "optionsVenueReferenceLabel" in lib
    assert "optionsTrustSourceLabel" in lib

    assert "optionsVenueReferenceLabel" in payload_lib
    assert "fallbackMetaForAsset" in payload_lib


def test_nav_enables_strategy_lab() -> None:
    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'id: "strategy-lab"' in nav
    assert 'href: "/strategy-lab"' in nav
    assert "disabled: true" not in nav.split("strategy-lab")[1].split("monitor")[0]

    cc = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert "moduleCards" in cc
    assert "MSOS_ROUTES.strategyLab" in cc


def test_expression_plan_propagates_selected_asset() -> None:
    panel = (MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx").read_text(
        encoding="utf-8"
    )
    tooltips = (MSOS_WEB / "src" / "lib" / "planLegTooltips.ts").read_text(encoding="utf-8")
    review = (MSOS_WEB / "src" / "lib" / "tradeReviewCopy.ts").read_text(encoding="utf-8")
    chart = (MSOS_WEB / "src" / "components" / "ExpressionPayoffChart.tsx").read_text(encoding="utf-8")

    assert "resolveDisplayAssetMeta(null, assetId)" in panel
    assert "buildWorkflowStepHref(\"confirm\", assetId)" in panel
    assert "useResolvedLabAssetId" in panel
    assert "priceAxisLabel={assetMeta.price_axis_label" in panel
    assert "assetTicker={assetMeta.id}" in panel
    assert "buildTradeProsCons(" in panel and "assetMeta.id" in panel
    assert "fetchStrategySuggestion(resolvedExpiry, tuning, assetId)" in panel
    assert "relabelPlanLegsForAsset" in panel
    assert "assetId," in panel or "assetId:" in panel

    suggestion_lib = (MSOS_WEB / "src" / "lib" / "ppeStrategySuggestion.ts").read_text(
        encoding="utf-8"
    )
    assert "LAB_ASSET_QUERY_PARAM" in suggestion_lib
    assert "buildStrategySuggestionFetchUrl" in suggestion_lib

    leg_display = (MSOS_WEB / "src" / "lib" / "planLegDisplay.ts").read_text(encoding="utf-8")
    assert "relabelPlanLegsForAsset" in leg_display

    assert "assetTicker: string = ABSOLUTE_FALLBACK_ASSET_ID" in tooltips
    assert "${ticker} rises" in tooltips

    assert "assetTicker: string = ABSOLUTE_FALLBACK_ASSET_ID" in review
    assert "${ticker} lands in your range" in review

    assert "priceAxisLabel" in chart
    assert "BTC price at expiry" not in chart


def test_session_lab_asset_resolution() -> None:
    asset_lib = (MSOS_WEB / "src" / "lib" / "strategyLabAsset.ts").read_text(encoding="utf-8")
    payload_lib = (MSOS_WEB / "src" / "lib" / "ppeDisplayPayload.ts").read_text(encoding="utf-8")
    hook = (MSOS_WEB / "src" / "lib" / "useResolvedLabAssetId.ts").read_text(encoding="utf-8")
    page = (MSOS_WEB / "src" / "app" / "strategy-lab" / "page.tsx").read_text(encoding="utf-8")
    workflow = (MSOS_WEB / "src" / "lib" / "strategyLabWorkflow.ts").read_text(encoding="utf-8")

    assert "resolveLabAssetId" in asset_lib
    assert "loadStoredLabAssetId" in asset_lib
    assert 'ABSOLUTE_FALLBACK_ASSET_ID = SYSTEM_DEFAULT_ASSET_ID' in asset_lib
    assert 'SYSTEM_DEFAULT_ASSET_ID = "ETH"' in payload_lib
    assert "thesisAssetId" in asset_lib
    assert "useResolvedLabAssetId" in hook
    assert "resolveLabAssetId" in page
    assert "useStored: false" in page
    assert "DEFAULT_LAB_ASSET_ID" not in workflow
    assert (
        "buildWorkflowStepHref(step, assetId)" in workflow
        or "assetId: LabAssetId" in workflow
        or "assetId?: LabAssetId" in workflow
    )


def test_monitor_propagates_thesis_asset() -> None:
    feed = (MSOS_WEB / "src" / "lib" / "monitorHistoryFeed.ts").read_text(encoding="utf-8")
    monitor = (MSOS_WEB / "src" / "components" / "MonitorContent.tsx").read_text(encoding="utf-8")
    empty = (MSOS_WEB / "src" / "components" / "MonitorEmptyState.tsx").read_text(encoding="utf-8")
    welcome = (MSOS_WEB / "src" / "components" / "MonitorWelcomeCard.tsx").read_text(encoding="utf-8")

    assert "assetTicker: string" in feed
    assert "resolveDisplayAssetMeta(null, displayAssetId).id" in feed
    assert "assetTicker={feed.assetTicker}" in monitor
    assert "assetTicker?: string" in empty
    assert "live ${ticker}" in empty or "live ${ticker}" in welcome
    assert "assetTicker?: string" in welcome


def test_expression_planning_route_and_narrative() -> None:
    page = MSOS_WEB / "src" / "app" / "strategy-lab" / "expression" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "ExpressionPlanningPanel" in text
    assert 'activeNavId="strategy-lab"' in text

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
    assert "ExpressionPayoffChart" in panel
    assert "fetchStrategySuggestion" in panel
    assert "resolveCurveLabels" in panel
    assert "Suggested trade vs market" in (
        MSOS_WEB / "src" / "components" / "ExpressionPayoffChart.tsx"
    ).read_text(encoding="utf-8")
    assert "priceAxisLabel" in (
        MSOS_WEB / "src" / "components" / "ExpressionPayoffChart.tsx"
    ).read_text(encoding="utf-8")

    suggestion_lib = (MSOS_WEB / "src" / "lib" / "ppeStrategySuggestion.ts").read_text(
        encoding="utf-8"
    )
    assert "strategy-suggestion.json" in suggestion_lib

    persistence = (MSOS_WEB / "src" / "lib" / "expressionPersistence.ts").read_text(encoding="utf-8")
    assert "msos.expression.preview.v1" in persistence
    assert "simulated" in persistence

    thesis_panel = (MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "buildWorkflowStepHref" in thesis_panel
    assert '"plan"' in thesis_panel


def test_strategy_lab_workflow_stepper_not_primary_nav() -> None:
    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'id: "expression"' not in nav.split("secondaryNavItems")[0]

    workflow = (MSOS_WEB / "src" / "lib" / "strategyLabWorkflow.ts").read_text(encoding="utf-8")
    assert '"/strategy-lab/expression"' in workflow
    assert "buildWorkflowStepHref" in workflow
    assert "Plan paper trade" in workflow

    stepper = (MSOS_WEB / "src" / "components" / "WorkflowStepper.tsx").read_text(encoding="utf-8")
    assert "workflow-stepper" in stepper
    assert "ContextRail" in (
        MSOS_WEB / "src" / "components" / "StrategyLabInteractivePanel.tsx"
    ).read_text(encoding="utf-8")
    assert "ContextRail" in (
        MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx"
    ).read_text(encoding="utf-8")
    assert "ContextRail" in (
        MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx"
    ).read_text(encoding="utf-8")
    rail = (MSOS_WEB / "src" / "components" / "ContextRail.tsx").read_text(encoding="utf-8")
    assert "context-rail-mobile" in rail
    assert "context-rail-sheet-toggle" in rail


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
    assert "MSOS_ROUTES.history" in cc


def test_conclusion_learn_loop_route() -> None:
    page = MSOS_WEB / "src" / "app" / "learn" / "page.tsx"
    assert page.is_file()
    learn_page = page.read_text(encoding="utf-8")
    assert "ConclusionContent" in learn_page
    assert 'activeNavId="learn"' in learn_page
    assert "searchParams: Promise" in learn_page
    assert "await searchParams" in learn_page

    fixtures = (MSOS_WEB / "src" / "data" / "conclusionFixtures.ts").read_text(encoding="utf-8")
    assert "What did you take away?" in fixtures
    assert "nextSelectionRecommendation" in fixtures

    panel = (MSOS_WEB / "src" / "components" / "ConclusionContent.tsx").read_text(encoding="utf-8")
    assert "testerMetricsTemplate" in panel
    assert "Research preview" in panel

    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'href: "/learn"' in nav
    assert "secondaryNavItems" in nav


def test_onboarding_polish_wiring() -> None:
    monitor = (MSOS_WEB / "src" / "components" / "MonitorContent.tsx").read_text(encoding="utf-8")
    layout = (MSOS_WEB / "src" / "app" / "layout.tsx").read_text(encoding="utf-8")
    planner = (MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx").read_text(
        encoding="utf-8"
    )
    assert "MonitorWelcomeCard" in monitor
    assert "MonitorEmptyState" in monitor
    assert "PostAuthReturnHandler" in layout
    assert "PlanLegRow" in planner
    assert "welcome=1" in planner
    assert "stashPostAuthReturnPath" in (
        MSOS_WEB / "src" / "lib" / "msosPublicUrls.ts"
    ).read_text(encoding="utf-8")
    assert "planLegTooltip" in (MSOS_WEB / "src" / "lib" / "planLegTooltips.ts").read_text(
        encoding="utf-8"
    )


def test_strategy_lab_forward_consistency_panel() -> None:
    work = (MSOS_WEB / "src" / "components" / "StrategyLabWorkSection.tsx").read_text(encoding="utf-8")
    panel = (MSOS_WEB / "src" / "components" / "ForwardConsistencyPanel.tsx").read_text(encoding="utf-8")
    lib = (MSOS_WEB / "src" / "lib" / "forwardConsistency.ts").read_text(encoding="utf-8")
    styles = (MSOS_WEB / "src" / "app" / "globals.css").read_text(encoding="utf-8")
    assert "ForwardConsistencyPanel" in work
    assert "No-Arbitrage Check" in panel
    assert "fetchForwardConsistencyPayload" in lib
    assert "isForwardConsistencyPayload" in lib
    assert ".forward-consistency" in styles


# --- MSOS workflow asset parity v1 (Witness-Slice003) ---

_LAB_ASSET_QUERY_PARAM = "asset"
_WORKFLOW_STEPS = {
    "compare": "/strategy-lab",
    "confirm": "/strategy-lab/confirm",
    "plan": "/strategy-lab/expression",
}
_NON_BTC_ASSETS = ("NVDA", "SOL")


def _build_workflow_step_href(step: str, asset_id: str) -> str:
    path = _WORKFLOW_STEPS[step]
    normalized = asset_id.strip().upper()
    if not normalized:
        return path
    return f"{path}?{_LAB_ASSET_QUERY_PARAM}={normalized}"


def _relabel_plan_legs_for_asset(legs: list[dict[str, str]], asset_id: str) -> list[dict[str, str]]:
    ticker = asset_id.strip().upper()
    if not ticker or ticker == "BTC":
        return legs
    out: list[dict[str, str]] = []
    for leg in legs:
        instrument = leg["instrument"]
        if re.match(r"^BTC\b", instrument, re.IGNORECASE):
            instrument = re.sub(r"^BTC\b", ticker, instrument, count=1, flags=re.IGNORECASE)
        out.append({**leg, "instrument": instrument})
    return out


def test_workflow_asset_parity_hrefs_preserve_nvda_and_sol() -> None:
    for asset in _NON_BTC_ASSETS:
        for step in _WORKFLOW_STEPS:
            href = _build_workflow_step_href(step, asset)
            parsed = urlparse(href)
            params = parse_qs(parsed.query)
            assert params.get(_LAB_ASSET_QUERY_PARAM) == [asset], href


def test_workflow_asset_parity_p4_lab_resolves_url_asset() -> None:
    page = (MSOS_WEB / "src" / "app" / "strategy-lab" / "page.tsx").read_text(encoding="utf-8")
    shell = (MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx").read_text(encoding="utf-8")
    payload_lib = (MSOS_WEB / "src" / "lib" / "ppeDisplayPayload.ts").read_text(encoding="utf-8")

    assert "resolveLabAssetId" in page
    assert "fetchDisplayPayload" in page or "fetchDisplayPayloadServer" in page
    assert "resolveLabAssetId" in shell
    assert 'buildWorkflowStepHref("confirm"' in shell
    assert "buildDisplayApiUrl" in payload_lib
    assert "LAB_ASSET_QUERY_PARAM" in payload_lib


def test_workflow_asset_parity_p5_confirm_venue_copy() -> None:
    panel = (MSOS_WEB / "src" / "components" / "ThesisConfirmationPanel.tsx").read_text(encoding="utf-8")
    ctx = (MSOS_WEB / "src" / "lib" / "buildThesisLabContext.ts").read_text(encoding="utf-8")
    payload_lib = (MSOS_WEB / "src" / "lib" / "ppeDisplayPayload.ts").read_text(encoding="utf-8")

    assert "buildThesisDraftFromLab(payload, storedTuning, storedExpiry, assetMeta)" in panel
    assert "optionsVenueReferenceLabel" in ctx
    assert 'id === "NVDA"' in payload_lib
    assert 'id === "SOL"' in payload_lib
    assert "Bybit" in payload_lib


def test_workflow_asset_parity_p6_expression_urls_include_asset() -> None:
    panel = (MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx").read_text(encoding="utf-8")
    suggestion = (MSOS_WEB / "src" / "lib" / "ppeStrategySuggestion.ts").read_text(encoding="utf-8")
    tuning = (MSOS_WEB / "src" / "lib" / "beliefTuning.ts").read_text(encoding="utf-8")

    assert "fetchStrategySuggestion(resolvedExpiry, tuning, assetId)" in panel
    assert "relabelPlanLegsForAsset" in panel
    assert "LAB_ASSET_QUERY_PARAM" in suggestion
    assert "LAB_ASSET_QUERY_PARAM" in tuning


def test_workflow_asset_parity_p6_plan_leg_relabel_non_btc() -> None:
    sample_legs = [
        {"side": "BUY", "instrument": "BTC Put", "strike": "Strike 90k", "tenor": "30d"},
        {"side": "SELL", "instrument": "BTC Call", "strike": "Strike 110k", "tenor": "30d"},
    ]
    for asset in _NON_BTC_ASSETS:
        relabeled = _relabel_plan_legs_for_asset(sample_legs, asset)
        assert relabeled[0]["instrument"] == f"{asset} Put"
        assert "BTC" not in relabeled[0]["instrument"]


def test_workflow_asset_parity_p7_monitor_resolves_thesis_asset() -> None:
    feed = (MSOS_WEB / "src" / "lib" / "monitorHistoryFeed.ts").read_text(encoding="utf-8")
    monitor = (MSOS_WEB / "src" / "components" / "MonitorContent.tsx").read_text(encoding="utf-8")

    assert "thesisAssetId: thesis?.assetId" in feed
    assert "fetchDisplayPayload(displayAssetId)" in feed
    assert "assetTicker={feed.assetTicker}" in monitor


def test_trust_surface_product_slice_lab_trust_ui() -> None:
    shell = (MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx").read_text(encoding="utf-8")
    picker = (MSOS_WEB / "src" / "components" / "LabAssetPicker.tsx").read_text(encoding="utf-8")
    catalog_lib = (MSOS_WEB / "src" / "lib" / "ppeAssetCatalog.ts").read_text(encoding="utf-8")
    copy = (MSOS_WEB / "src" / "lib" / "strategyLabCopy.ts").read_text(encoding="utf-8")
    css = (MSOS_WEB / "src" / "app" / "globals.css").read_text(encoding="utf-8")

    assert "trust_state" in shell
    assert 'lab-data-banner thin-chain"' in shell
    assert 'lab-data-banner degraded"' in shell
    assert "LAB_THIN_CHAIN_BANNER_TITLE" in shell
    assert 'tag amber">Sample</span>' in shell
    assert "lab-trust-notes" in picker
    assert "trustNotesForAsset" in picker
    assert "trust_notes" in catalog_lib
    assert "findCatalogAsset" in catalog_lib
    assert "labThinChainBannerBody" in copy
    assert ".lab-data-banner.thin-chain" in css
    assert ".lab-trust-notes" in css


def test_workflow_asset_parity_witness_evidence_and_plan() -> None:
    evidence = (SOP / "MSOS_WORKFLOW_ASSET_PARITY_V1_EVIDENCE_STATUS.md").read_text(encoding="utf-8")
    plan = (SOP / "PHASE_PLANS" / "msos_workflow_asset_parity_v1_relay.json").read_text(encoding="utf-8")
    assert "MSOS-WfAsset-Witness-Slice003" in evidence
    assert "**COMPLETE**" in evidence
    assert "Monitor" in evidence
    assert "MSOS-WfAsset-Witness-Slice003" in plan


# --- PPE Exposure menu v1 (Product-Slice005) ---


def test_exposure_menu_route_and_shell() -> None:
    page = MSOS_WEB / "src" / "app" / "exposure" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "AppShell" in text
    assert "ExposureMenuClient" in text
    assert 'activeNavId="exposure"' in text
    assert "fetchExposureMenu" in text
    assert "searchParams: Promise" in text


def test_exposure_menu_boundary_proxy_no_ts_math() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "ppeExposureMenu.ts").read_text(encoding="utf-8")
    client = (MSOS_WEB / "src" / "components" / "ExposureMenuClient.tsx").read_text(encoding="utf-8")
    card = (MSOS_WEB / "src" / "components" / "ExposurePathCard.tsx").read_text(encoding="utf-8")

    assert "exposure-menu.json" in lib
    assert "fetchExposureMenuClient" in lib
    assert "isExposureMenuPayload" in lib
    assert "buildExposureMenuFetchUrl" in lib
    assert "path_not_recommendation" not in client
    assert "Math." not in lib
    assert "Math." not in client
    assert "Math." not in card
    assert "fetchExposureMenuClient" in client
    assert "exposure-path-grid" in client
    assert "not trade recommendations" in client.lower() or "comparison only" in client.lower()


def test_exposure_menu_fixtures_and_deep_links() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "exposureMenuFixtures.ts").read_text(encoding="utf-8")
    assert "DEMO_EXPOSURE_MENU_NVDA_LONG" in fixtures
    assert "DEMO_EXPOSURE_MENU_BTC_LONG" in fixtures
    assert "path_not_recommendation" in fixtures
    assert "Paths for comparison only" in fixtures
    assert "/strategy-lab?asset=NVDA" in fixtures
    assert "/strategy-lab?asset=BTC" in fixtures

    nvda_block = fixtures.split("DEMO_EXPOSURE_MENU_NVDA_LONG")[1].split("DEMO_EXPOSURE_MENU_BTC_LONG")[0]
    assert nvda_block.index("long_stock") < nvda_block.index("long_otm_call")

    card = (MSOS_WEB / "src" / "components" / "ExposurePathCard.tsx").read_text(encoding="utf-8")
    assert "Open in Strategy Lab" in card
    assert "deep_link" in card


def test_exposure_menu_secondary_nav() -> None:
    nav = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'id: "exposure"' in nav
    assert 'href: "/exposure"' in nav
    assert "secondaryNavItems" in nav

    urls = (MSOS_WEB / "src" / "lib" / "msosPublicUrls.ts").read_text(encoding="utf-8")
    assert "exposure:" in urls or 'exposure: "/exposure"' in urls

    styles = (MSOS_WEB / "src" / "app" / "globals.css").read_text(encoding="utf-8")
    assert ".exposure-path-grid" in styles
    assert ".exposure-menu-work" in styles

