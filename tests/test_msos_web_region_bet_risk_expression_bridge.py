"""Region Bet risk-to-expression bridge v1 product-slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def _read(*parts: str) -> str:
    return (MSOS_WEB.joinpath(*parts)).read_text(encoding="utf-8")


def test_region_bet_risk_expression_maps_to_existing_fit_primitives() -> None:
    bridge = _read("src", "lib", "regionBetRiskExpression.ts")
    assert "rankOptionsExpressionFit" in bridge
    assert "buildCandidatesFromExposureMenu" in bridge
    assert "buildCandidateFromStrategySuggestion" in bridge
    assert "mapRegionBetToExpressionFitPreferences" in bridge
    assert "max_loss_usd: Math.min(maxLoss, maxPremium)" in bridge
    assert "payoff_preference: regionBet.risk_constraints.payoff_preference" in bridge
    assert "5428" not in bridge
    assert "src/engine/options_expression_fit_ranking" not in bridge


def test_region_bet_guided_flow_captures_bounded_risk_preferences() -> None:
    contract = _read("src", "lib", "regionBet.ts")
    shell = _read("src", "lib", "regionBetGuidedShell.ts")
    panel = _read("src", "components", "RegionBetRiskExpressionPanel.tsx")
    assert "payoff_preference?: string" in contract
    assert "max_loss_usd?: number" in contract
    assert "max_premium_usd?: number" in contract
    assert "payoff_preference: seed?.risk_constraints?.payoff_preference" in shell
    assert "selected_expression_ref?:" in shell
    assert "Max loss (USD)" in panel
    assert "Premium budget (USD)" in panel
    assert "Payoff preference" in panel
    assert "REGION_BET_PAYOFF_PREFERENCES" in panel


def test_region_bet_risk_expression_explains_three_paper_lanes() -> None:
    bridge = _read("src", "lib", "regionBetRiskExpression.ts")
    panel = _read("src", "components", "RegionBetRiskExpressionPanel.tsx")
    assert 'safer: "Safer / more likely"' in bridge
    assert 'best_fit: "Best fit"' in bridge
    assert 'convex: "Higher payout / convex"' in bridge
    assert "assignRegionBetExpressionLanes" in bridge
    assert "explainRegionBetExpressionLane" in bridge
    assert "Not an expected-return claim" in bridge
    assert "Paper comparison only" in bridge
    assert "choice.label" in panel
    assert "not financial advice" in panel.lower()
    assert "not a recommendation" in panel.lower()
    assert "not order execution" in panel.lower()
    assert "expected profit" not in panel.lower()
    assert "recommended trade" not in panel.lower()


def test_region_bet_persists_only_selected_expression_and_constraints() -> None:
    bridge = _read("src", "lib", "regionBetRiskExpression.ts")
    panel = _read("src", "components", "RegionBetRiskExpressionPanel.tsx")
    shell = _read("src", "components", "RegionBetGuidedShell.tsx")
    assert "selectedRegionBetExpressionRef" in bridge
    assert "expression_id: ranked.candidate_id" in bridge
    assert "source: ranked.candidate.source" in bridge
    assert "selected_expression_ref: selectedRegionBetExpressionRef(choice)" in panel
    assert "max_loss_usd: draft.risk_constraints.max_loss_usd" in panel
    assert "max_premium_usd: draft.risk_constraints.max_premium_usd" in panel
    assert "payoff_preference: draft.risk_constraints.payoff_preference" in panel
    assert "persistRegionBet" in shell
    assert "top_fit" not in panel
    assert "expected_return" not in panel
    assert "ranking:" not in panel


def test_region_bet_risk_expression_fails_closed_for_invalid_and_empty() -> None:
    bridge = _read("src", "lib", "regionBetRiskExpression.ts")
    panel = _read("src", "components", "RegionBetRiskExpressionPanel.tsx")
    assert "isRegionBetRiskExpressionReady" in bridge
    assert 'status: "invalid_constraints"' in bridge
    assert 'status: "empty_candidates"' in bridge
    assert "premium cannot exceed the stated max-loss" in bridge
    assert "max-loss must be a finite amount above zero" in bridge
    assert "filterRegionBetExpressionCandidatesByPremium" in bridge
    assert "No paper expression candidates fit these limits" in panel
    assert "Enter a max-loss, premium budget, and payoff preference" in panel


def test_region_bet_review_embeds_risk_expression_without_parked_surfaces() -> None:
    guided_panel = _read("src", "components", "RegionBetGuidedShellPanel.tsx")
    panel = _read("src", "components", "RegionBetRiskExpressionPanel.tsx")
    assert "<RegionBetRiskExpressionPanel draft={draft} onDraftChange={onDraftChange} />" in guided_panel
    assert "data-testid=\"region-bet-risk-expression-panel\"" in panel
    assert "fetchExposureMenuClient" in panel
    assert "fetchStrategySuggestion" in panel
    assert "buildRegionBetRiskExpression" in panel
    assert "OptionsHorizonComparison" not in panel
    assert "brokerage" not in panel.lower()
    assert "order ticket" not in panel.lower()
    assert "expected-profit" not in panel.lower()
    assert "5428" not in panel
