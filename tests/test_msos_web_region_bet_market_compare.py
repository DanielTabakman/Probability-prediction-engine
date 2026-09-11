"""Region Bet market-compare bridge v1 product-slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_region_bet_guided_shell_exposes_compare_step_before_review() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "regionBetGuidedShell.ts").read_text(
        encoding="utf-8"
    )
    assert 'export type RegionBetGuidedShellStep = "asset" | "window" | "region" | "compare" | "review"' in lib
    assert '{ id: "region", label: "Region" }' in lib
    assert '{ id: "compare", label: "Compare" }' in lib
    assert '{ id: "review", label: "Review" }' in lib
    assert lib.index('{ id: "region", label: "Region" }') < lib.index(
        '{ id: "compare", label: "Compare" }'
    ) < lib.index('{ id: "review", label: "Review" }')


def test_region_bet_market_compare_bridge_reuses_options_horizon_comparison() -> None:
    bridge = (MSOS_WEB / "src" / "lib" / "regionBetMarketCompare.ts").read_text(
        encoding="utf-8"
    )
    assert "buildOptionsHorizonComparisonFromChart" in bridge
    assert "comparison: buildOptionsHorizonComparisonFromChart(mappedPayload)" in bridge
    assert "selectedBuckets" not in bridge
    assert "TARGET_BUCKET_DAYS" not in bridge
    assert "Math.abs" not in bridge


def test_region_bet_market_compare_panel_embeds_existing_table_read_only() -> None:
    panel = (
        MSOS_WEB / "src" / "components" / "RegionBetMarketComparePanel.tsx"
    ).read_text(encoding="utf-8")
    assert "OptionsHorizonComparisonPanel" in panel
    assert "fetchHorizonChartPayload(fetchParams)" in panel
    assert "buildRegionBetMarketCompareFromChart(snapshot, payload)" in panel
    assert "data-testid=\"region-bet-market-compare-panel\"" in panel
    assert "not financial advice" in panel
    assert "not a recommendation" in panel
    assert "not order execution" in panel
    assert "button" not in panel.lower()
    assert "order ticket" not in panel.lower()


def test_region_bet_guided_panel_preserves_context_through_compare() -> None:
    panel = (
        MSOS_WEB / "src" / "components" / "RegionBetGuidedShellPanel.tsx"
    ).read_text(encoding="utf-8")
    assert 'if (step === "compare")' in panel
    assert "<RegionBetMarketComparePanel snapshot={snapshot} />" in panel
    assert "draft.target.expiry_utc" in panel
    assert "draft.target.window_start_utc" in panel
    assert "draft.target.window_end_utc" in panel
    assert "draft.selected_region.price_min_usd" in panel
    assert "draft.selected_region.price_max_usd" in panel


def test_region_bet_market_compare_does_not_recreate_parked_surfaces() -> None:
    touched = "\n".join(
        [
            (MSOS_WEB / "src" / "lib" / "regionBetMarketCompare.ts").read_text(
                encoding="utf-8"
            ),
            (
                MSOS_WEB / "src" / "components" / "RegionBetMarketComparePanel.tsx"
            ).read_text(encoding="utf-8"),
            (
                MSOS_WEB / "src" / "components" / "RegionBetGuidedShellPanel.tsx"
            ).read_text(encoding="utf-8"),
        ]
    )
    assert "OptionsExpressionFitRanking" not in touched
    assert "expected profit" not in touched.lower()
    assert "brokerage" not in touched.lower()
    assert "order ticket" not in touched.lower()
