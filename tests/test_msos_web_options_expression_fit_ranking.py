from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO / "apps" / "msos-web"


def test_msos_ranking_lib_declares_no_advice_contract_and_weights() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "optionsExpressionFitRanking.ts").read_text(encoding="utf-8")

    assert "EXPRESSION_FIT_WEIGHTS" in lib
    assert "direction_fit: 30" in lib
    assert "horizon_fit: 20" in lib
    assert "max_loss_fit: 20" in lib
    assert "payoff_fit: 15" in lib
    assert "trust_fit: 15" in lib
    assert "educational_fit_not_recommendation" in lib
    assert "not financial advice" in lib
    assert "expected-profit optimization" in lib
    assert "optionsHorizonComparison" not in lib


def test_msos_ranking_component_is_bounded_surface() -> None:
    component = (MSOS_WEB / "src" / "components" / "OptionsExpressionFitRankingPanel.tsx").read_text(
        encoding="utf-8"
    )

    assert "Educational fit ranking" in component
    assert "ranking.ranked.slice(0, 3)" in component
    assert "ranking.limitation" in component
    assert "recommendation" not in component.lower()


def test_expression_planning_panel_wires_ranking_without_advice_copy() -> None:
    panel = (MSOS_WEB / "src" / "components" / "ExpressionPlanningPanel.tsx").read_text(encoding="utf-8")

    assert "OptionsExpressionFitRankingPanel" in panel
    assert "rankOptionsExpressionFit" in panel
    assert "buildCandidateFromStrategySuggestion" in panel
    assert "payoff_preference: \"defined_risk\"" in panel
    assert "Educational fit ranking" not in panel
    assert "recommended trade" not in panel.lower()
