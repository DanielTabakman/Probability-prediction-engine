"""Build durable JSON records for frozen implied-lab evaluations (MVP1 Phase 4)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

PAYLOAD_SCHEMA_VERSION = "ppe_frozen_eval_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_frozen_evaluation_record(
    *,
    verification: dict[str, Any],
    expiry_str: str,
    operator_note: str | None = None,
) -> dict[str, Any]:
    """
    Canonical JSON-serializable record for SQLite persistence.
    Captures benchmark witness + classifier version per MVP1 Phase 4 canon.
    """
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
    return {
        "snapshot_id": str(uuid.uuid4()),
        "created_at_utc": _utc_now_iso(),
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
        "expiry": str(expiry_str),
        "operator_note": (operator_note or "").strip() or None,
        "classifier_version": classifier_version,
        "benchmark_witness": benchmark_witness,
        "verification": v,
    }


def summary_line_for_record(rec: dict[str, Any]) -> str:
    """One-line label for list UI."""
    vs = rec.get("verification") if isinstance(rec.get("verification"), dict) else {}
    inner = vs.get("verification_summary") if isinstance(vs.get("verification_summary"), dict) else {}
    cat = inner.get("disagreement_category_id") or "—"
    as_of = inner.get("as_of_utc") or rec.get("created_at_utc") or "—"
    return f"{as_of} · {rec.get('expiry', '—')} · {cat}"
