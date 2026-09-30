"""Pure market-thesis.v1 validator and derived state.

No network. Writers recompute ``workflow_state`` with ``derive_state``.
The contract is ``docs/SOP/MARKET_THESIS_WORKFLOW_V1.md``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Any, Mapping

SCHEMA_VERSION = "market-thesis.v1"
KIND = "market_thesis"
DISAGREEMENT_METHOD = "belief_vs_cited_evidence.v1"
AUTHORITY = {
    "execution": "out_of_scope",
    "recommendation_status": "educational_comparison_not_recommendation",
}
FIT_STATUS = "educational_fit_not_recommendation"
RANKING_KIND = "options_expression_fit_ranking"

STATES = (
    "draft",
    "belief_captured",
    "horizon_bound",
    "evidence_attached",
    "disagreement_recorded",
    "expressions_ranked",
    "artifact_saved",
)
_STATE_INDEX = {name: index for index, name in enumerate(STATES)}
_EVENT_FROM = {
    "set_belief": "draft",
    "set_horizon": "belief_captured",
    "attach_evidence": "horizon_bound",
    "record_disagreement": "evidence_attached",
    "rank_expressions": "disagreement_recorded",
    "save_artifact": "expressions_ranked",
}
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_BUCKETS = {30, 60, 90, 180, 365}
_DIRECTIONS = {"long", "short", "neutral"}
_DIRECTION_ALIASES = {
    "long": "long",
    "short": "short",
    "neutral": "neutral",
    "bullish": "long",
    "bearish": "short",
    "up": "long",
    "down": "short",
    "bullish_in_region": "long",
    "bearish_in_region": "short",
}
_EVIDENCE_PRIMITIVES = {
    "options_market_read",
    "options_horizon_comparison",
    "horizon_region_implied_mass",
}
_MARKET_KEYS = {
    "atm_iv",
    "atm_iv_percent",
    "middle_50_range",
    "implied_mass_pct",
    "one_sigma_move_usd",
    "fit_score",
    "payload",
    "payload_sha256",
}
_CITATION_THESIS_KEYS = {"user_belief", "fit_score", "order_id", "statement", "thesis"}
_EXECUTION_KEYS = {
    "order_id",
    "broker_order_id",
    "broker",
    "venue_ticket",
    "executed",
    "filled",
    "submitted",
}
_EXECUTION_STATES = {"executed", "filled", "submitted"}


class MarketThesisError(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(detail or code)


def canonical_json(value: Any) -> str:
    """Canonical JSON: sorted keys, compact separators."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def artifact_body(document: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "user_belief": document.get("user_belief"),
        "horizon": document.get("horizon"),
        "market_evidence": document.get("market_evidence"),
        "disagreement": document.get("disagreement"),
        "expression_comparison": document.get("expression_comparison"),
        "authority": document.get("authority"),
    }


def new_draft(*, thesis_id: str, asset_id: str, symbol: str | None = None) -> dict[str, Any]:
    if not thesis_id or not asset_id:
        raise MarketThesisError("illegal_transition", "id and asset_id are required")
    asset: dict[str, Any] = {"asset_id": asset_id}
    if symbol:
        asset["symbol"] = symbol
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "id": thesis_id,
        "revision": 1,
        "workflow_state": "draft",
        "asset": asset,
        "user_belief": None,
        "horizon": None,
        "market_evidence": {"citations": []},
        "disagreement": None,
        "expression_comparison": None,
        "artifact": None,
        "prior_artifacts": [],
        "links": {},
        "authority": dict(AUTHORITY),
    }


def make_citation(
    *,
    citation_id: str,
    primitive: str,
    endpoint: str,
    as_of_utc: str,
    request: Mapping[str, Any],
    payload: Mapping[str, Any],
    schema_version: str | None = None,
    ruleset_version: str | None = None,
) -> dict[str, Any]:
    citation: dict[str, Any] = {
        "citation_id": citation_id,
        "primitive": primitive,
        "endpoint": endpoint,
        "as_of_utc": as_of_utc,
        "request": dict(request),
        "payload": copy.deepcopy(dict(payload)),
    }
    if schema_version is not None:
        citation["schema_version"] = schema_version
    if ruleset_version is not None:
        citation["ruleset_version"] = ruleset_version
    citation["payload_sha256"] = sha256_canonical(citation["payload"])
    return citation


def derive_state(document: Mapping[str, Any]) -> str:
    """Furthest state whose guards pass. Does not read a clock or the network."""
    _reject_execution(document)
    _reject_belief_market_mix(document)
    _assert_fresh(document)
    if not _draft_guard(document):
        raise MarketThesisError("illegal_transition", "draft guard failed")
    state = "draft"
    if _belief_guard(document):
        state = "belief_captured"
    else:
        return state
    if _horizon_guard(document):
        state = "horizon_bound"
    else:
        return state
    if _evidence_guard(document):
        state = "evidence_attached"
    else:
        return state
    if _disagreement_guard(document):
        state = "disagreement_recorded"
    else:
        return state
    if _expressions_guard(document):
        state = "expressions_ranked"
    else:
        return state
    if _artifact_guard(document):
        state = "artifact_saved"
    return state


def validate_market_thesis(document: Mapping[str, Any]) -> str:
    state = derive_state(document)
    stored = document.get("workflow_state")
    if stored != state:
        raise MarketThesisError("state_drift", f"{stored} != {state}")
    return state


def apply_event(document: Mapping[str, Any], event: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a new document after one state-machine event."""
    if event in _EXECUTION_STATES:
        raise MarketThesisError("execution_out_of_scope", event)
    body = payload or {}
    doc = copy.deepcopy(dict(document))
    if event == "revise":
        _revise(doc, body)
    elif event in _EVENT_FROM:
        prior = derive_state(doc)
        expected = _EVENT_FROM[event]
        if prior != expected:
            raise MarketThesisError(
                "illegal_transition",
                f"{event} requires {expected}, document is {prior}",
            )
        if event == "set_belief":
            doc["user_belief"] = _with_canonical_direction(body)
        elif event == "set_horizon":
            doc["horizon"] = _horizon(body)
        elif event == "attach_evidence":
            incoming = body.get("citations", body)
            if isinstance(incoming, Mapping):
                incoming = [incoming]
            citations = list(doc["market_evidence"]["citations"])
            seen = {item["citation_id"] for item in citations}
            for raw in incoming:
                citation = _citation(raw)
                if citation["citation_id"] in seen:
                    raise MarketThesisError("illegal_transition", "duplicate citation_id")
                citations.append(citation)
                seen.add(citation["citation_id"])
            doc["market_evidence"]["citations"] = citations
        elif event == "record_disagreement":
            doc["disagreement"] = _disagreement(doc, str(body.get("citation_id") or ""))
        elif event == "rank_expressions":
            doc["expression_comparison"] = _comparison(doc, body)
        elif event == "save_artifact":
            frozen = str(body.get("frozen_at_utc") or "")
            if not frozen:
                raise MarketThesisError("illegal_transition", "frozen_at_utc is required")
            doc["artifact"] = {
                "frozen_at_utc": frozen,
                "content_sha256": sha256_canonical(artifact_body(doc)),
                "shareable": True,
                "execution": "out_of_scope",
            }
    else:
        raise MarketThesisError("illegal_transition", f"unknown event {event}")
    doc["workflow_state"] = derive_state(doc)
    return doc


def _revise(doc: dict[str, Any], payload: Mapping[str, Any]) -> None:
    if not str(doc.get("id") or ""):
        raise MarketThesisError("illegal_transition", "revise requires an id")
    section = str(payload.get("section") or "")
    if section not in {"user_belief", "horizon", "market_evidence", "risk_limits"}:
        raise MarketThesisError("illegal_transition", f"unknown revise section {section}")
    derive_state(doc)
    if doc.get("artifact"):
        doc["prior_artifacts"].append(copy.deepcopy(doc["artifact"]))
    doc["revision"] = int(doc["revision"]) + 1
    if section == "user_belief":
        doc["user_belief"] = _with_canonical_direction(payload.get("value") or {})
        doc["disagreement"] = None
        doc["expression_comparison"] = None
        doc["artifact"] = None
    elif section == "horizon":
        doc["horizon"] = _horizon(payload.get("value") or {})
        doc["market_evidence"]["citations"] = [
            item
            for item in doc["market_evidence"]["citations"]
            if _citation_matches_horizon(item, doc["horizon"])
        ]
        doc["disagreement"] = None
        doc["expression_comparison"] = None
        doc["artifact"] = None
    elif section == "market_evidence":
        _revise_evidence(doc, payload.get("value"))
    elif section == "risk_limits":
        doc["expression_comparison"] = None
        doc["artifact"] = None


def _revise_evidence(doc: dict[str, Any], value: Any) -> None:
    raw_items = [value] if isinstance(value, Mapping) else list(value or [])
    revised = [_citation(item) for item in raw_items]
    used = (doc.get("disagreement") or {}).get("market_side_citation_id")
    previous = {
        item["citation_id"]: item for item in doc["market_evidence"]["citations"]
    }
    changed = False
    if used:
        old = previous.get(used)
        new = next((item for item in revised if item["citation_id"] == used), None)
        changed = old is None or new is None or canonical_json(old) != canonical_json(new)
    doc["market_evidence"]["citations"] = revised
    if changed:
        doc["disagreement"] = None
        doc["expression_comparison"] = None
        doc["artifact"] = None


def _draft_guard(document: Mapping[str, Any]) -> bool:
    asset = document.get("asset") or {}
    authority = document.get("authority") or {}
    evidence = document.get("market_evidence") or {}
    return (
        document.get("schema_version") == SCHEMA_VERSION
        and document.get("kind") == KIND
        and isinstance(document.get("id"), str)
        and bool(document.get("id"))
        and isinstance(document.get("revision"), int)
        and not isinstance(document.get("revision"), bool)
        and int(document["revision"]) >= 1
        and isinstance(asset.get("asset_id"), str)
        and bool(asset.get("asset_id"))
        and authority.get("execution") == "out_of_scope"
        and authority.get("recommendation_status") == "educational_comparison_not_recommendation"
        and isinstance(evidence.get("citations"), list)
        and isinstance(document.get("prior_artifacts"), list)
        and isinstance(document.get("links"), dict)
    )


def _belief_guard(document: Mapping[str, Any]) -> bool:
    belief = document.get("user_belief")
    if belief is None:
        return False
    try:
        _belief(belief)
    except MarketThesisError:
        return False
    return True


def _belief(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise MarketThesisError("illegal_transition", "belief must be an object")
    _reject_market_keys(raw, "user_belief")
    allowed = {
        "source",
        "direction",
        "statement",
        "magnitude",
        "uncertainty",
        "assumptions",
        "legacy_strategy_lab",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise MarketThesisError("illegal_transition", f"unknown belief fields {sorted(unknown)}")
    direction = raw.get("direction")
    if direction not in _DIRECTIONS:
        raise MarketThesisError("illegal_transition", "direction is not long, short, or neutral")
    statement = str(raw.get("statement") or "").strip()
    if raw.get("source") != "user" or not statement:
        raise MarketThesisError("illegal_transition", "belief source and statement are required")
    magnitude = _magnitude(raw.get("magnitude"))
    uncertainty = _uncertainty(raw.get("uncertainty"))
    assumptions = _assumptions(raw.get("assumptions"))
    belief: dict[str, Any] = {
        "source": "user",
        "direction": direction,
        "statement": statement,
        "magnitude": magnitude,
        "uncertainty": uncertainty,
        "assumptions": assumptions,
    }
    if "legacy_strategy_lab" in raw:
        belief["legacy_strategy_lab"] = _legacy(raw.get("legacy_strategy_lab"))
    return belief


def _with_canonical_direction(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise MarketThesisError("illegal_transition", "belief must be an object")
    direction = _DIRECTION_ALIASES.get(str(raw.get("direction") or "").strip().lower())
    if direction is None:
        raise MarketThesisError("illegal_transition", "direction is not long, short, or neutral")
    cloned = dict(raw)
    cloned["direction"] = direction
    return _belief(cloned)


def _magnitude(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise MarketThesisError("illegal_transition", "magnitude is required")
    _reject_market_keys(raw, "magnitude")
    kind = raw.get("kind")
    if kind not in {"price_band", "percent_move", "qualitative"}:
        raise MarketThesisError("illegal_transition", "magnitude.kind is invalid")
    allowed = {"kind", "price_min_usd", "price_max_usd", "percent_move", "qualitative_label"}
    unknown = set(raw) - allowed
    if unknown:
        raise MarketThesisError("illegal_transition", f"unknown magnitude fields {sorted(unknown)}")
    magnitude: dict[str, Any] = {"kind": kind}
    for key in ("price_min_usd", "price_max_usd", "percent_move"):
        if key in raw:
            magnitude[key] = _number(raw[key], key)
    if "qualitative_label" in raw:
        magnitude["qualitative_label"] = str(raw["qualitative_label"])
    if kind == "price_band" and "price_min_usd" in magnitude and "price_max_usd" in magnitude:
        if magnitude["price_max_usd"] <= magnitude["price_min_usd"]:
            raise MarketThesisError("illegal_transition", "price band max must exceed min")
    return magnitude


def _uncertainty(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise MarketThesisError("illegal_transition", "uncertainty is required")
    _reject_market_keys(raw, "uncertainty")
    kind = raw.get("kind")
    if kind not in {
        "wider_than_market",
        "narrower_than_market",
        "similar_to_market",
        "unspecified",
    }:
        raise MarketThesisError("illegal_transition", "uncertainty.kind is invalid")
    unknown = set(raw) - {"kind", "note"}
    if unknown:
        raise MarketThesisError("illegal_transition", f"unknown uncertainty fields {sorted(unknown)}")
    uncertainty: dict[str, Any] = {"kind": kind}
    if "note" in raw:
        uncertainty["note"] = str(raw["note"])
    return uncertainty


def _assumptions(raw: Any) -> list[dict[str, str]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise MarketThesisError("illegal_transition", "assumptions must be a list")
    items: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, Mapping) or not str(item.get("id") or "") or not str(item.get("text") or ""):
            raise MarketThesisError("illegal_transition", "assumption needs id and text")
        items.append({"id": str(item["id"]), "text": str(item["text"])})
    return items


def _legacy(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise MarketThesisError("illegal_transition", "legacy_strategy_lab must be an object")
    allowed = {"thesis_record_id", "forward_mult", "vol_mult", "thesis_range_pct"}
    unknown = set(raw) - allowed
    if unknown:
        raise MarketThesisError("illegal_transition", f"unknown legacy fields {sorted(unknown)}")
    legacy: dict[str, Any] = {}
    if "thesis_record_id" in raw:
        legacy["thesis_record_id"] = str(raw["thesis_record_id"])
    for key in ("forward_mult", "vol_mult", "thesis_range_pct"):
        if key in raw:
            legacy[key] = _number(raw[key], key)
    return legacy


def _horizon_guard(document: Mapping[str, Any]) -> bool:
    horizon = document.get("horizon")
    if horizon is None:
        return False
    try:
        _horizon(horizon)
    except MarketThesisError:
        return False
    return True


def _horizon(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise MarketThesisError("illegal_transition", "horizon must be an object")
    mode = raw.get("mode")
    if mode not in {"listed_expiry", "bucket", "price_time_region"}:
        raise MarketThesisError("illegal_transition", "horizon.mode is invalid")
    allowed = {"mode", "target_date", "expiry_date", "target_bucket_days", "linked_expiry_ts", "region"}
    unknown = set(raw) - allowed
    if unknown:
        raise MarketThesisError("illegal_transition", f"unknown horizon fields {sorted(unknown)}")
    horizon: dict[str, Any] = {"mode": mode}
    for key in ("target_date", "expiry_date"):
        if key in raw:
            if not _DATE.match(str(raw[key])):
                raise MarketThesisError("illegal_transition", f"{key} must be YYYY-MM-DD")
            horizon[key] = str(raw[key])
    if mode == "listed_expiry" and "target_date" not in horizon and "expiry_date" not in horizon:
        raise MarketThesisError("illegal_transition", "listed expiry needs a date")
    if "target_bucket_days" in raw:
        days = raw["target_bucket_days"]
        if days not in _BUCKETS:
            raise MarketThesisError("illegal_transition", "target_bucket_days is not a listed bucket")
        horizon["target_bucket_days"] = days
    if mode == "bucket" and horizon.get("target_bucket_days") not in _BUCKETS:
        raise MarketThesisError("illegal_transition", "bucket horizon needs target_bucket_days")
    if "linked_expiry_ts" in raw:
        if not isinstance(raw["linked_expiry_ts"], int) or isinstance(raw["linked_expiry_ts"], bool):
            raise MarketThesisError("illegal_transition", "linked_expiry_ts must be an integer")
        horizon["linked_expiry_ts"] = raw["linked_expiry_ts"]
    if "region" in raw:
        horizon["region"] = _region(raw["region"])
    if mode == "price_time_region" and "region" not in horizon:
        raise MarketThesisError("illegal_transition", "price_time_region needs a region")
    return horizon


def _region(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise MarketThesisError("illegal_transition", "region must be an object")
    required = ("time_start_utc", "time_end_utc", "price_min_usd", "price_max_usd")
    if any(not raw.get(key) and raw.get(key) != 0 for key in required):
        raise MarketThesisError("illegal_transition", "region is incomplete")
    start = _parse_utc(str(raw["time_start_utc"]))
    end = _parse_utc(str(raw["time_end_utc"]))
    if end <= start:
        raise MarketThesisError("illegal_transition", "region end must be after start")
    price_min = _number(raw["price_min_usd"], "price_min_usd")
    price_max = _number(raw["price_max_usd"], "price_max_usd")
    if price_max <= price_min:
        raise MarketThesisError("illegal_transition", "region price max must exceed min")
    return {
        "time_start_utc": str(raw["time_start_utc"]),
        "time_end_utc": str(raw["time_end_utc"]),
        "price_min_usd": price_min,
        "price_max_usd": price_max,
    }


def _evidence_guard(document: Mapping[str, Any]) -> bool:
    citations = (document.get("market_evidence") or {}).get("citations") or []
    return any(
        isinstance(item, Mapping) and item.get("primitive") in _EVIDENCE_PRIMITIVES for item in citations
    )


def _citation(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise MarketThesisError("illegal_transition", "citation must be an object")
    if raw.get("primitive") not in _EVIDENCE_PRIMITIVES:
        raise MarketThesisError("illegal_transition", "citation primitive is not market evidence")
    for key in ("citation_id", "endpoint", "as_of_utc"):
        if not str(raw.get(key) or ""):
            raise MarketThesisError("illegal_transition", f"citation {key} is required")
    if not isinstance(raw.get("request"), Mapping):
        raise MarketThesisError("illegal_transition", "citation request is required")
    payload = raw.get("payload")
    if payload is not None and not isinstance(payload, Mapping):
        raise MarketThesisError("illegal_transition", "citation payload must be an object")
    if isinstance(payload, Mapping):
        leaked = _CITATION_THESIS_KEYS.intersection(payload)
        if leaked:
            raise MarketThesisError("belief_market_mix", f"citation payload contains {sorted(leaked)}")
    citation: dict[str, Any] = {
        "citation_id": str(raw["citation_id"]),
        "primitive": raw["primitive"],
        "endpoint": str(raw["endpoint"]),
        "as_of_utc": str(raw["as_of_utc"]),
        "request": copy.deepcopy(dict(raw["request"])),
    }
    if "schema_version" in raw:
        citation["schema_version"] = raw["schema_version"]
    if "ruleset_version" in raw:
        citation["ruleset_version"] = str(raw["ruleset_version"])
    if isinstance(payload, Mapping):
        citation["payload"] = copy.deepcopy(dict(payload))
        digest = sha256_canonical(citation["payload"])
        supplied = raw.get("payload_sha256")
        if supplied is not None and supplied != digest:
            raise MarketThesisError("stale_derived", "payload_sha256 does not match payload")
        citation["payload_sha256"] = digest
    elif raw.get("payload_sha256"):
        if not _SHA.match(str(raw["payload_sha256"])):
            raise MarketThesisError("stale_derived", "payload_sha256 is malformed")
        citation["payload_sha256"] = str(raw["payload_sha256"])
    return citation


def _citation_matches_horizon(citation: Mapping[str, Any], horizon: Mapping[str, Any]) -> bool:
    request = citation.get("request") or {}
    mode = horizon.get("mode")
    primitive = citation.get("primitive")
    if primitive == "horizon_region_implied_mass":
        if mode != "price_time_region":
            return False
        region = horizon.get("region") or {}
        req_region = request.get("region") if isinstance(request.get("region"), Mapping) else request
        for key in ("time_start_utc", "time_end_utc", "price_min_usd", "price_max_usd"):
            if key in req_region and req_region.get(key) != region.get(key):
                return False
        return True
    if primitive == "options_horizon_comparison":
        if "target_bucket_days" in request:
            return mode == "bucket" and request.get("target_bucket_days") == horizon.get("target_bucket_days")
        return True
    if primitive == "options_market_read":
        expiry = request.get("expiry_date") or request.get("target_date")
        if mode == "listed_expiry":
            allowed = {horizon.get("target_date"), horizon.get("expiry_date")} - {None}
            return expiry is None or expiry in allowed
        if expiry:
            return False
        if "target_bucket_days" in request:
            return mode == "bucket" and request.get("target_bucket_days") == horizon.get("target_bucket_days")
    return True


def _disagreement_guard(document: Mapping[str, Any]) -> bool:
    disagreement = document.get("disagreement")
    if not isinstance(disagreement, Mapping):
        return False
    if disagreement.get("method") != DISAGREEMENT_METHOD or disagreement.get("read_only") is not True:
        return False
    user_side = disagreement.get("user_side")
    belief = document.get("user_belief") or {}
    if not isinstance(user_side, list) or not user_side:
        return False
    if any(not isinstance(item, str) or item not in belief for item in user_side):
        return False
    citation_id = disagreement.get("market_side_citation_id")
    citations = (document.get("market_evidence") or {}).get("citations") or []
    match = next((item for item in citations if item.get("citation_id") == citation_id), None)
    if not isinstance(match, Mapping):
        return False
    return bool(str(disagreement.get("summary") or ""))


def _disagreement(doc: Mapping[str, Any], citation_id: str) -> dict[str, Any]:
    citations = doc["market_evidence"]["citations"]
    match = next((item for item in citations if item.get("citation_id") == citation_id), None)
    if not isinstance(match, Mapping) or not match.get("payload"):
        raise MarketThesisError("illegal_transition", "disagreement needs one embedded citation")
    summary = _summary(doc["user_belief"], match)
    return {
        "method": DISAGREEMENT_METHOD,
        "user_side": ["magnitude", "uncertainty"],
        "market_side_citation_id": citation_id,
        "summary": summary,
        "read_only": True,
    }


def _summary(belief: Mapping[str, Any], citation: Mapping[str, Any]) -> str:
    magnitude = str(belief["magnitude"]["kind"]).replace("_", " ")
    uncertainty = str(belief["uncertainty"]["kind"]).replace("_", " ")
    return (
        f"User belief magnitude is {magnitude} and uncertainty is {uncertainty}. "
        f"Market citation {citation['citation_id']} ({citation['primitive']}) reports {_market_fact(citation)}. "
        "Descriptive comparison only."
    )


def _market_fact(citation: Mapping[str, Any]) -> str:
    payload = citation.get("payload") or {}
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), Mapping) else {}
    middle = metrics.get("middle_50_range") if isinstance(metrics, Mapping) else None
    if isinstance(middle, Mapping) and "low" in middle and "high" in middle:
        return f"middle 50 range {_num(middle['low'])} to {_num(middle['high'])}"
    if "one_sigma_move_usd" in payload:
        return f"one-sigma move {_num(payload['one_sigma_move_usd'])} USD"
    computed = payload.get("computed") if isinstance(payload.get("computed"), Mapping) else {}
    mass = payload.get("implied_mass_pct", computed.get("implied_mass_pct") if isinstance(computed, Mapping) else None)
    if mass is not None:
        return f"implied mass {_num(mass)} percent"
    return "no middle-50, one-sigma move, or implied mass"


def _expressions_guard(document: Mapping[str, Any]) -> bool:
    comparison = document.get("expression_comparison")
    if not isinstance(comparison, Mapping):
        return False
    if comparison.get("ranking_kind") != RANKING_KIND:
        return False
    if comparison.get("recommendation_status") != FIT_STATUS:
        return False
    payload = comparison.get("ranking_payload")
    if not isinstance(payload, Mapping) or payload.get("kind") != RANKING_KIND:
        return False
    rows = comparison.get("rows")
    if not isinstance(rows, list):
        return False
    if not rows:
        return isinstance(comparison.get("empty_reason"), str) and bool(comparison.get("empty_reason"))
    return all(_row_ok(row) for row in rows)


def _comparison(doc: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    ranking = payload.get("ranking_payload")
    if not isinstance(ranking, Mapping) or ranking.get("kind") != RANKING_KIND:
        raise MarketThesisError("illegal_transition", "ranking payload is required")
    if ranking.get("recommendation_status") not in (None, FIT_STATUS):
        raise MarketThesisError("illegal_transition", "ranking recommendation_status is not educational")
    rows_in = payload.get("rows")
    if not isinstance(rows_in, list):
        raise MarketThesisError("illegal_transition", "rows are required")
    rows = [_row(item) for item in rows_in]
    belief = doc["user_belief"]
    comparison: dict[str, Any] = {
        "ranking_kind": RANKING_KIND,
        "recommendation_status": FIT_STATUS,
        "preferences": {
            "direction": belief["direction"],
            "belief": belief["statement"],
            "max_loss_usd": payload.get("max_loss_usd"),
            "payoff_preference": payload.get("payoff_preference"),
        },
        "ranking_payload": copy.deepcopy(dict(ranking)),
        "rows": rows,
    }
    if not rows:
        reason = str(payload.get("empty_reason") or "").strip()
        if not reason:
            raise MarketThesisError("illegal_transition", "empty ranking needs empty_reason")
        comparison["empty_reason"] = reason
    elif payload.get("empty_reason"):
        comparison["empty_reason"] = str(payload["empty_reason"])
    return comparison


def _row(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not _row_ok(raw):
        raise MarketThesisError("illegal_transition", "comparison row is incomplete")
    row = {
        "candidate_id": str(raw["candidate_id"]),
        "label": str(raw["label"]),
        "source_primitive": raw["source_primitive"],
        "cost": _money(raw["cost"]),
        "max_loss": _money(raw["max_loss"]),
        "time_horizon": {
            "label": str(raw["time_horizon"]["label"]),
        },
        "payoff_shape": str(raw["payoff_shape"]),
        "failure_modes": [str(item) for item in raw["failure_modes"]],
        "recommendation_status": FIT_STATUS,
    }
    if "days" in raw["time_horizon"]:
        days = raw["time_horizon"]["days"]
        if days is not None and (not isinstance(days, int) or isinstance(days, bool)):
            raise MarketThesisError("illegal_transition", "time horizon days must be an integer")
        row["time_horizon"]["days"] = days
    if "rank" in raw:
        row["rank"] = raw["rank"]
    if "score" in raw:
        row["score"] = raw["score"]
    return row


def _row_ok(raw: Any) -> bool:
    if not isinstance(raw, Mapping):
        return False
    horizon = raw.get("time_horizon")
    return (
        bool(raw.get("candidate_id"))
        and bool(raw.get("label"))
        and raw.get("source_primitive") in {"exposure_paths", "strategy_suggestion"}
        and _money_ok(raw.get("cost"))
        and _money_ok(raw.get("max_loss"))
        and isinstance(horizon, Mapping)
        and bool(horizon.get("label"))
        and bool(str(raw.get("payoff_shape") or ""))
        and isinstance(raw.get("failure_modes"), list)
        and len(raw["failure_modes"]) >= 1
        and all(str(item) for item in raw["failure_modes"])
        and raw.get("recommendation_status") == FIT_STATUS
    )


def _money(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not _money_ok(raw):
        raise MarketThesisError("illegal_transition", "cost or max loss is incomplete")
    money: dict[str, Any] = {"status": raw["status"]}
    if "amount_usd" in raw:
        money["amount_usd"] = None if raw["amount_usd"] is None else _number(raw["amount_usd"], "amount_usd")
    if "label" in raw:
        money["label"] = str(raw["label"])
    if "bounded" in raw:
        money["bounded"] = bool(raw["bounded"])
    return money


def _money_ok(raw: Any) -> bool:
    if not isinstance(raw, Mapping) or raw.get("status") not in {"estimated", "unavailable"}:
        return False
    if raw.get("status") == "unavailable" and raw.get("bounded") is not False:
        return False
    return True


def _artifact_guard(document: Mapping[str, Any]) -> bool:
    artifact = document.get("artifact")
    if not isinstance(artifact, Mapping):
        return False
    digest = artifact.get("content_sha256")
    if not isinstance(digest, str) or not _SHA.match(digest):
        return False
    if digest != sha256_canonical(artifact_body(document)):
        return False
    if artifact.get("shareable") is not True or artifact.get("execution") != "out_of_scope":
        return False
    if not str(artifact.get("frozen_at_utc") or ""):
        return False
    citations = (document.get("market_evidence") or {}).get("citations") or []
    used = (document.get("disagreement") or {}).get("market_side_citation_id")
    for citation in citations:
        if used and citation.get("citation_id") != used:
            continue
        if "payload" not in citation or not _SHA.match(str(citation.get("payload_sha256") or "")):
            return False
    return True


def _assert_fresh(document: Mapping[str, Any]) -> None:
    for citation in (document.get("market_evidence") or {}).get("citations") or []:
        if not isinstance(citation, Mapping):
            continue
        payload = citation.get("payload")
        digest = citation.get("payload_sha256")
        if isinstance(payload, Mapping) and digest is not None:
            if digest != sha256_canonical(payload):
                raise MarketThesisError("stale_derived", "payload_sha256 does not match payload")
    artifact = document.get("artifact")
    if isinstance(artifact, Mapping) and artifact.get("content_sha256"):
        if artifact["content_sha256"] != sha256_canonical(artifact_body(document)):
            raise MarketThesisError("stale_derived", "content_sha256 does not match the thesis body")
    belief = document.get("user_belief") or {}
    comparison = document.get("expression_comparison")
    if isinstance(comparison, Mapping) and isinstance(belief, Mapping):
        prefs = comparison.get("preferences") or {}
        if isinstance(prefs, Mapping) and "direction" in prefs and prefs.get("direction") != belief.get("direction"):
            raise MarketThesisError("stale_derived", "comparison direction does not match user belief")
        ranking = comparison.get("ranking_payload") or {}
        ranked_prefs = ranking.get("preferences") if isinstance(ranking, Mapping) else None
        if (
            isinstance(ranked_prefs, Mapping)
            and "direction" in ranked_prefs
            and ranked_prefs.get("direction") != belief.get("direction")
        ):
            raise MarketThesisError("stale_derived", "ranking direction does not match user belief")


def _reject_execution(document: Mapping[str, Any]) -> None:
    state = document.get("workflow_state")
    if state in _EXECUTION_STATES:
        raise MarketThesisError("execution_out_of_scope", str(state))
    authority = document.get("authority") or {}
    if isinstance(authority, Mapping) and "execution" in authority and authority.get("execution") != "out_of_scope":
        raise MarketThesisError("execution_out_of_scope", str(authority.get("execution")))
    for key in _iter_keys(_without_payloads(document)):
        if key in _EXECUTION_KEYS:
            raise MarketThesisError("execution_out_of_scope", key)


def _reject_belief_market_mix(document: Mapping[str, Any]) -> None:
    belief = document.get("user_belief")
    if isinstance(belief, Mapping):
        _reject_market_keys(belief, "user_belief")
    for citation in (document.get("market_evidence") or {}).get("citations") or []:
        if not isinstance(citation, Mapping):
            continue
        payload = citation.get("payload")
        if isinstance(payload, Mapping):
            leaked = _CITATION_THESIS_KEYS.intersection(payload)
            if leaked:
                raise MarketThesisError("belief_market_mix", f"citation payload contains {sorted(leaked)}")


def _reject_market_keys(value: Mapping[str, Any], where: str) -> None:
    found = [key for key in _iter_keys(value) if key in _MARKET_KEYS]
    if found:
        raise MarketThesisError("belief_market_mix", f"{where} contains {found[0]}")


def _without_payloads(document: Mapping[str, Any]) -> dict[str, Any]:
    cloned = copy.deepcopy(dict(document))
    evidence = cloned.get("market_evidence")
    if isinstance(evidence, dict):
        for citation in evidence.get("citations") or []:
            if isinstance(citation, dict):
                citation.pop("payload", None)
    return cloned


def _iter_keys(value: Any):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from _iter_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_keys(item)


def _number(value: Any, label: str) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MarketThesisError("illegal_transition", f"{label} must be a number")
    return value


def _num(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MarketThesisError("illegal_transition", "region time is not ISO-8601") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
