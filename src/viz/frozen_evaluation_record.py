"""Build durable JSON records for frozen implied-lab evaluations (MVP1 Phase 4)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

PAYLOAD_SCHEMA_VERSION = "ppe_frozen_eval_v1"
SUPPORTED_PAYLOAD_SCHEMA_VERSIONS = frozenset({PAYLOAD_SCHEMA_VERSION})
SNAPSHOT_REVIEW_SCHEMA_VERSION = "snapshot_review_v1"


def _require_mapping(value: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_frozen_evaluation_record(
    *,
    verification: dict[str, Any],
    expiry_str: str,
    operator_note: str | None = None,
    owner_email: str | None = None,
) -> dict[str, Any]:
    """
    Canonical JSON-serializable record for SQLite persistence.
    Captures benchmark witness + classifier version per MVP1 Phase 4 canon.
    """
    snapshot_id = str(uuid.uuid4())
    created_at_utc = _utc_now_iso()
    v = verification if isinstance(verification, dict) else {}
    dens = v.get("density") if isinstance(v.get("density"), dict) else {}
    ref = dens.get("reference_risk_neutral") if isinstance(dens.get("reference_risk_neutral"), dict) else {}
    benchmark_witness: dict[str, Any] = {
        "identity": "lognormal_risk_neutral_reference",
        "method": ref.get("method"),
        "forward_usd": ref.get("forward_usd"),
        "atm_iv_annual": ref.get("atm_iv_annual"),
        "T_years": ref.get("T_years"),
        "grid_price_min_usd": ref.get("grid_price_min_usd"),
        "grid_price_max_usd": ref.get("grid_price_max_usd"),
        "grid_points": ref.get("grid_points"),
    }
    bd = v.get("belief_disagreement") if isinstance(v.get("belief_disagreement"), dict) else {}
    classifier_version = str(bd.get("contract_schema_version") or "").strip() or str(
        v.get("belief_disagreement_provenance", {}).get("schema_version") or ""
    ).strip() or "unknown"

    vs = v.get("verification_summary") if isinstance(v.get("verification_summary"), dict) else {}
    mvp1 = v.get("mvp1_decision") if isinstance(v.get("mvp1_decision"), dict) else {}
    mat = mvp1.get("materiality") if isinstance(mvp1.get("materiality"), dict) else {}
    record_header = {
        "snapshot_id": snapshot_id,
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
        "created_at_utc": created_at_utc,
        "expiry": str(expiry_str),
        "classifier_version": classifier_version,
    }
    return {
        "snapshot_id": snapshot_id,
        "created_at_utc": created_at_utc,
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
        "record_header": record_header,
        "expiry": str(expiry_str),
        "operator_note": (operator_note or "").strip() or None,
        "owner_email": (owner_email or "").strip().lower() or None,
        "classifier_version": classifier_version,
        "benchmark_witness": benchmark_witness,
        "data_quality": mvp1.get("data_quality") or vs.get("data_quality"),
        "primary_output_state": mvp1.get("primary_output_state") or vs.get("primary_output_state"),
        "classification_label": mvp1.get("classification_label") or vs.get("classification_label"),
        "materiality_rule_version": mat.get("materiality_rule_version"),
        "market_width_1sigma_move_pct": mat.get("market_width_1sigma_move_pct"),
        "benchmark_width_1sigma_move_pct": mat.get("benchmark_width_1sigma_move_pct"),
        "materiality_m_ratio": mat.get("m_ratio"),
        "verification": v,
    }


def record_header_for_record(record: dict[str, Any]) -> dict[str, Any]:
    """Minimal review-facing header; intentionally excludes owner identity."""
    rec = _require_mapping(record, label="frozen evaluation record")
    return {
        "snapshot_id": str(rec.get("snapshot_id") or ""),
        "payload_schema_version": str(rec.get("payload_schema_version") or ""),
        "created_at_utc": str(rec.get("created_at_utc") or ""),
        "expiry": str(rec.get("expiry") or ""),
        "classifier_version": str(rec.get("classifier_version") or ""),
    }


def validate_frozen_evaluation_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize the Python-owned frozen evaluation record boundary."""
    rec = dict(_require_mapping(record, label="frozen evaluation record"))
    version = str(rec.get("payload_schema_version") or "").strip()
    if version not in SUPPORTED_PAYLOAD_SCHEMA_VERSIONS:
        raise ValueError(
            f"unsupported frozen evaluation payload_schema_version {version!r}; "
            f"expected {PAYLOAD_SCHEMA_VERSION!r}"
        )
    snapshot_id = str(rec.get("snapshot_id") or "").strip()
    if not snapshot_id:
        raise ValueError("frozen evaluation snapshot_id is required")
    created_at_utc = str(rec.get("created_at_utc") or "").strip()
    if not created_at_utc:
        raise ValueError("frozen evaluation created_at_utc is required")

    header = rec.get("record_header")
    if header is None:
        rec["record_header"] = record_header_for_record(rec)
        return rec
    hdr = _require_mapping(header, label="frozen evaluation record_header")
    header_snapshot_id = str(hdr.get("snapshot_id") or "").strip()
    if header_snapshot_id != snapshot_id:
        raise ValueError(
            "frozen evaluation record_header.snapshot_id must match snapshot_id "
            f"({header_snapshot_id!r} != {snapshot_id!r})"
        )
    header_version = str(hdr.get("payload_schema_version") or "").strip()
    if header_version != PAYLOAD_SCHEMA_VERSION:
        raise ValueError(
            "frozen evaluation record_header.payload_schema_version must be "
            f"{PAYLOAD_SCHEMA_VERSION!r}"
        )
    rec["record_header"] = record_header_for_record(rec)
    return rec


def build_snapshot_review_payload(
    *,
    record: dict[str, Any],
    review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Minimal review-facing payload for a frozen snapshot and optional review row."""
    rec = validate_frozen_evaluation_record(record)
    return {
        "schema_version": SNAPSHOT_REVIEW_SCHEMA_VERSION,
        "snapshot_id": rec["snapshot_id"],
        "record_header": record_header_for_record(rec),
        "review": dict(review or {}),
    }


def validate_snapshot_review_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate snapshot_review_v1, including outer/header snapshot identity."""
    data = dict(_require_mapping(payload, label="snapshot review payload"))
    version = str(data.get("schema_version") or "").strip()
    if version != SNAPSHOT_REVIEW_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported snapshot review schema_version {version!r}; "
            f"expected {SNAPSHOT_REVIEW_SCHEMA_VERSION!r}"
        )
    snapshot_id = str(data.get("snapshot_id") or "").strip()
    if not snapshot_id:
        raise ValueError("snapshot review snapshot_id is required")
    header = _require_mapping(data.get("record_header"), label="snapshot review record_header")
    header_snapshot_id = str(header.get("snapshot_id") or "").strip()
    if header_snapshot_id != snapshot_id:
        raise ValueError(
            "snapshot_review_v1 snapshot_id must match record_header.snapshot_id "
            f"({snapshot_id!r} != {header_snapshot_id!r})"
        )
    header_version = str(header.get("payload_schema_version") or "").strip()
    if header_version != PAYLOAD_SCHEMA_VERSION:
        raise ValueError(
            "snapshot_review_v1 record_header.payload_schema_version must be "
            f"{PAYLOAD_SCHEMA_VERSION!r}"
        )
    review = data.get("review")
    if review is not None and not isinstance(review, dict):
        raise ValueError("snapshot review review must be an object when present")
    data["record_header"] = {
        "snapshot_id": header_snapshot_id,
        "payload_schema_version": header_version,
        "created_at_utc": str(header.get("created_at_utc") or ""),
        "expiry": str(header.get("expiry") or ""),
        "classifier_version": str(header.get("classifier_version") or ""),
    }
    data["review"] = dict(review or {})
    return data


def summary_line_for_record(rec: dict[str, Any]) -> str:
    """One-line label for list UI."""
    vs = rec.get("verification") if isinstance(rec.get("verification"), dict) else {}
    inner = vs.get("verification_summary") if isinstance(vs.get("verification_summary"), dict) else {}
    cat = inner.get("disagreement_category_id") or "—"
    as_of = inner.get("as_of_utc") or rec.get("created_at_utc") or "—"
    return f"{as_of} · {rec.get('expiry', '—')} · {cat}"
