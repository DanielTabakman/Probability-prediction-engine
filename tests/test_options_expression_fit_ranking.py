from __future__ import annotations

import inspect
import json

from src.engine.options_expression_fit_ranking import (
    LIMITATION_TEXT,
    ExpressionFitPreferences,
    rank_expression_candidates,
)


def _candidate(path_id: str, **kwargs):
    base = {
        "candidate_id": f"exposure:{path_id}",
        "path_id": path_id,
        "label": path_id.replace("_", " ").title(),
        "direction": "long",
        "leverage": "defined",
        "time_bound": "dated",
        "horizon_days": 30,
        "trust_badge": "Live",
        "fit_lenses": ["defined_risk"],
        "max_loss_usd": 500,
        "source_order": 0,
    }
    base.update(kwargs)
    return base


def test_score_components_and_top_fit_are_deterministic() -> None:
    prefs = ExpressionFitPreferences(
        direction="long",
        target_horizon_days=30,
        max_loss_usd=750,
        payoff_preference="defined_risk",
    )
    candidates = [
        _candidate("bull_call_spread", source_order=1),
        _candidate("stock", leverage="none", time_bound="none", fit_lenses=["simplest"], max_loss_usd=None, source_order=0),
    ]

    first = rank_expression_candidates(candidates, prefs)
    second = rank_expression_candidates(list(reversed(candidates)), prefs)

    assert first["top_fit"]["candidate_id"] == "exposure:bull_call_spread"
    assert first["top_fit"]["components"]["direction_fit"]["score"] == 30
    assert first["top_fit"]["components"]["max_loss_fit"]["score"] == 20
    assert first["ranked"] == second["ranked"]
    assert first["limitation"] == LIMITATION_TEXT
    assert first["recommendation_status"] == "educational_fit_not_recommendation"


def test_max_loss_and_payoff_preference_lower_rank_alternative() -> None:
    prefs = ExpressionFitPreferences(
        direction="long",
        target_horizon_days=30,
        max_loss_usd=500,
        payoff_preference="capital_light",
    )
    ranked = rank_expression_candidates(
        [
            _candidate("cheap_spread", max_loss_usd=250, fit_lenses=["capital_light"], source_order=1),
            _candidate("expensive_spread", max_loss_usd=1_500, fit_lenses=["defined_risk"], source_order=0),
        ],
        prefs,
    )

    assert ranked["top_fit"]["candidate_id"] == "exposure:cheap_spread"
    lower = ranked["ranked"][1]
    assert lower["components"]["max_loss_fit"]["score"] == 0
    assert any("exceeds" in reason for reason in lower["why_lower"])


def test_tie_break_prefers_live_then_source_order_then_id() -> None:
    prefs = ExpressionFitPreferences(direction="long", payoff_preference="defined_risk")
    ranked = rank_expression_candidates(
        [
            _candidate("b", trust_badge="Thin chain", source_order=0),
            _candidate("c", source_order=2),
            _candidate("a", source_order=1),
        ],
        prefs,
    )

    assert [row["candidate_id"] for row in ranked["ranked"]] == ["exposure:a", "exposure:c", "exposure:b"]


def test_boundary_consumes_current_main_primitives_without_job_a_import(monkeypatch) -> None:
    import src.viz.options_expression_fit_ranking_boundary as boundary

    monkeypatch.setattr(
        boundary,
        "build_exposure_menu_response",
        lambda environ: {
            "kind": "exposure_paths",
            "asset_id": "NVDA",
            "paths": [_candidate("defined_option")],
        },
    )
    monkeypatch.setattr(
        boundary,
        "build_strategy_suggestion_response",
        lambda **kwargs: {
            "kind": "strategy_suggestion_boundary",
            "suggested": {
                "preset_id": "short_iron_fly",
                "name": "Iron fly",
                "expression_family": "range",
                "summary": {"max_loss_usd": 300},
                "legs": [],
            },
        },
    )

    payload = boundary.build_options_expression_fit_ranking_response(
        {"QUERY_STRING": "asset=NVDA&direction=neutral&expiry=2026-09-18&target_horizon_days=30&max_loss_usd=500"}
    )
    assert payload["source_kinds"] == {
        "exposure_menu": "exposure_paths",
        "strategy_suggestion": "strategy_suggestion_boundary",
    }
    assert payload["top_fit"]["candidate_id"] == "strategy:short_iron_fly"
    assert payload["kind"] == "options_expression_fit_ranking"

    source = inspect.getsource(boundary)
    assert "options_horizon_comparison" not in source


def test_wsgi_handler_returns_stable_json(monkeypatch) -> None:
    import src.viz.options_expression_fit_ranking_boundary as boundary

    monkeypatch.setattr(
        boundary,
        "build_exposure_menu_response",
        lambda environ: {"kind": "exposure_paths", "asset_id": "NVDA", "paths": [_candidate("defined_option")]},
    )
    result = boundary.handle_options_expression_fit_ranking_wsgi_path(
        "/ppe-display-api/options-expression-fit-ranking.json",
        {"QUERY_STRING": "asset=NVDA&direction=long&offline=1"},
    )

    assert result is not None
    status, body = result
    assert status == "200 OK"
    assert json.loads(body)["kind"] == "options_expression_fit_ranking"
