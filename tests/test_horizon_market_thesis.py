"""Read-only market-thesis.v1 workflow: state, guards, and a canned BTC artifact."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.engine.market_thesis import (
    MarketThesisError,
    apply_event,
    artifact_body,
    make_citation,
    new_draft,
    sha256_canonical,
    validate_market_thesis,
)

FIXTURE = Path(__file__).with_name("test_horizon_market_thesis_btc.json")
FROZEN_AT = "2026-09-29T18:00:00Z"
AS_OF = "2026-09-29T17:00:00Z"


def _belief() -> dict:
    return {
        "source": "user",
        "direction": "bullish",
        "statement": "BTC trades higher over the next quarter.",
        "magnitude": {"kind": "percent_move", "percent_move": 15},
        "uncertainty": {"kind": "wider_than_market"},
        "assumptions": [{"id": "a1", "text": "No change to the listed-expiry set."}],
    }


def _citations() -> list[dict]:
    omr = make_citation(
        citation_id="omr-btc",
        primitive="options_market_read",
        endpoint="/v1/options-market-read",
        as_of_utc=AS_OF,
        request={"asset_id": "BTC", "expiry_date": "2026-09-25"},
        payload={
            "schema_version": "1.3",
            "ruleset_version": "options-market-read.v1.3",
            "metrics": {"middle_50_range": {"low": 85000, "high": 128000}},
        },
        schema_version="1.3",
        ruleset_version="options-market-read.v1.3",
    )
    horizon = make_citation(
        citation_id="horizon-btc",
        primitive="options_horizon_comparison",
        endpoint="/ppe-display-api/horizon/comparison.json",
        as_of_utc=AS_OF,
        request={"asset_id": "BTC", "target_bucket_days": 90},
        payload={"kind": "options_horizon_comparison", "one_sigma_move_usd": 18000},
    )
    return [omr, horizon]


def _row() -> dict:
    return {
        "candidate_id": "exposure:defined-risk-call-spread",
        "label": "Defined-risk call spread",
        "source_primitive": "exposure_paths",
        "rank": 1,
        "score": 72.5,
        "cost": {"amount_usd": 250, "label": "debit", "status": "estimated"},
        "max_loss": {"amount_usd": 250, "label": "premium paid", "status": "estimated", "bounded": True},
        "time_horizon": {"days": 90, "label": "about 90 days"},
        "payoff_shape": "Capped upside with the debit as the amount at risk",
        "failure_modes": ["The debit can expire worthless if BTC does not reach the spread."],
        "recommendation_status": "educational_fit_not_recommendation",
    }


def _saved_btc_thesis() -> dict:
    doc = new_draft(thesis_id="thesis-btc-2026-09-29", asset_id="BTC", symbol="BTC")
    doc = apply_event(doc, "set_belief", _belief())
    doc = apply_event(doc, "set_horizon", {"mode": "listed_expiry", "target_date": "2026-09-25"})
    doc = apply_event(doc, "attach_evidence", {"citations": _citations()})
    doc = apply_event(doc, "record_disagreement", {"citation_id": "omr-btc"})
    doc = apply_event(
        doc,
        "rank_expressions",
        {
            "max_loss_usd": 500,
            "payoff_preference": "defined_risk",
            "ranking_payload": {
                "kind": "options_expression_fit_ranking",
                "recommendation_status": "educational_fit_not_recommendation",
                "preferences": {"direction": "long", "belief": _belief()["statement"]},
                "exposure_paths": [
                    {
                        "path_id": "defined-risk-call-spread",
                        "label": "Defined-risk call spread",
                        "cost_hint_usd": 250,
                        "capital_shape": "Capped upside with the debit as the amount at risk",
                    }
                ],
            },
            "rows": [_row()],
        },
    )
    return apply_event(doc, "save_artifact", {"frozen_at_utc": FROZEN_AT})


def test_happy_path_reaches_saved_artifact_and_matches_fixture() -> None:
    doc = _saved_btc_thesis()
    assert validate_market_thesis(doc) == "artifact_saved"
    assert doc["user_belief"]["direction"] == "long"
    assert doc["authority"]["execution"] == "out_of_scope"
    assert "expected profit" not in doc["disagreement"]["summary"].lower()
    stored = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert doc == stored


def test_skipped_transition_is_illegal() -> None:
    doc = new_draft(thesis_id="thesis-btc-2026-09-29", asset_id="BTC")
    with pytest.raises(MarketThesisError) as caught:
        apply_event(doc, "rank_expressions", {"ranking_payload": {}, "rows": []})
    assert caught.value.code == "illegal_transition"


def test_belief_market_mix_rejects_market_metric_on_user_belief() -> None:
    belief = _belief()
    belief["magnitude"] = {"kind": "qualitative", "atm_iv_percent": 48}
    doc = new_draft(thesis_id="thesis-btc-2026-09-29", asset_id="BTC")
    with pytest.raises(MarketThesisError) as caught:
        apply_event(doc, "set_belief", belief)
    assert caught.value.code == "belief_market_mix"


def test_revise_drops_derived_work_and_horizon_mismatched_evidence() -> None:
    doc = _saved_btc_thesis()
    revised = apply_event(
        doc,
        "revise",
        {"section": "horizon", "value": {"mode": "listed_expiry", "target_date": "2026-12-25"}},
    )
    assert revised["revision"] == 2
    assert revised["workflow_state"] == "horizon_bound"
    assert revised["market_evidence"]["citations"] == []
    assert revised["disagreement"] is None
    assert revised["expression_comparison"] is None
    assert revised["artifact"] is None
    assert revised["prior_artifacts"][0]["content_sha256"] == doc["artifact"]["content_sha256"]
    assert validate_market_thesis(revised) == "horizon_bound"


def test_content_hash_is_byte_stable() -> None:
    first = _saved_btc_thesis()
    second = _saved_btc_thesis()
    assert first["artifact"]["content_sha256"] == second["artifact"]["content_sha256"]
    assert first["artifact"]["content_sha256"] == sha256_canonical(artifact_body(first))
    reordered = artifact_body(first)
    reordered = {key: reordered[key] for key in reversed(list(reordered))}
    assert sha256_canonical(reordered) == first["artifact"]["content_sha256"]


def test_execution_state_drift_and_stale_hash_codes() -> None:
    doc = _saved_btc_thesis()
    executed = dict(doc)
    executed["workflow_state"] = "executed"
    with pytest.raises(MarketThesisError) as caught:
        validate_market_thesis(executed)
    assert caught.value.code == "execution_out_of_scope"

    drifted = json.loads(json.dumps(doc))
    drifted["workflow_state"] = "expressions_ranked"
    with pytest.raises(MarketThesisError) as caught:
        validate_market_thesis(drifted)
    assert caught.value.code == "state_drift"

    stale = json.loads(json.dumps(doc))
    stale["artifact"]["content_sha256"] = "0" * 64
    with pytest.raises(MarketThesisError) as caught:
        validate_market_thesis(stale)
    assert caught.value.code == "stale_derived"
