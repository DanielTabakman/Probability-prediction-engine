"""
Phase 6 — aggregate reviewed frozen snapshots (non-pending reviews only).

Read-only rollups from persisted verification + benchmark witness fields.
No execution or automated trading semantics.
"""

from __future__ import annotations

import csv
import io
from collections import Counter
from typing import Any


def extract_summary_dimensions(record: dict[str, Any]) -> dict[str, str]:
    """
    Map frozen JSON into canonical-ish buckets for counting.

    `disagreement_category_id` proxies MVP1 “direction” of belief-vs-market disagreement.
    `shape_gap_strength` proxies exploratory confidence labeling from the classification trace / glance.
    `trust_breeden` uses Breeden gate status as a coarse market-implied trust artifact.
    """
    v = record.get("verification") if isinstance(record.get("verification"), dict) else {}
    vs = v.get("verification_summary") if isinstance(v.get("verification_summary"), dict) else {}
    bd = v.get("belief_disagreement") if isinstance(v.get("belief_disagreement"), dict) else {}
    trace = bd.get("classification_trace") if isinstance(bd.get("classification_trace"), dict) else {}
    glance = v.get("belief_vs_market_glance") if isinstance(v.get("belief_vs_market_glance"), dict) else {}
    mi = (v.get("density") or {}).get("market_implied") if isinstance(v.get("density"), dict) else {}
    mi = mi if isinstance(mi, dict) else {}
    bw = record.get("benchmark_witness") if isinstance(record.get("benchmark_witness"), dict) else {}

    cat = vs.get("disagreement_category_id") or bd.get("category_id") or trace.get("category_id")
    shape_gap = glance.get("shape_gap_strength") or trace.get("shape_gap_strength") or "—"
    trust = mi.get("breeden_litzenberger")
    benchmark_method = bw.get("method") or bw.get("identity") or "unknown"
    classifier = record.get("classifier_version") or "unknown"

    return {
        "disagreement_category_id": str(cat or "unknown"),
        "shape_gap_strength": str(shape_gap),
        "trust_breeden": str(trust or "unknown"),
        "benchmark_method": str(benchmark_method),
        "classifier_version": str(classifier),
    }


def operator_guidance_line(counts: Counter[str]) -> str:
    """Simple continue / refine / suppress / retire style line from review-status counts."""
    supportive = counts.get("supportive", 0)
    contradictory = counts.get("contradictory", 0)
    contaminated = counts.get("contaminated", 0)
    not_j = counts.get("not_judgeable", 0)
    n = sum(counts.values())

    if n == 0:
        return "No completed reviews yet — collect reviewed snapshots first."

    if supportive >= contradictory + contaminated and supportive >= 1 and contradictory == 0:
        return "continue — supportive outcomes dominate; class evidence is net-positive on reviewed runs."
    if contradictory > supportive:
        return "refine — contradictory reviews outweigh supportive; revisit disagreement framing or data quality."
    if contaminated + not_j >= max(supportive, contradictory, 1):
        return "suppress — contaminated / not judgeable labels dominate; treat the class as weak until cleaner witnesses."
    if n < 3:
        return "collect_more_evidence — fewer than three reviewed snapshots; defer strong class-level conclusions."
    return "mixed — continue logging reviews before a sharp class decision."


def build_class_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Parameters
    ----------
    rows :
        Items like ``list_completed_review_snapshots`` output:
        ``{"snapshot_id", "record", "review"}``.
    """
    by_status: Counter[str] = Counter()
    by_cat: Counter[str] = Counter()
    by_gap: Counter[str] = Counter()
    by_trust: Counter[str] = Counter()
    by_bench: Counter[str] = Counter()
    by_class: Counter[str] = Counter()

    for row in rows:
        rec = row.get("record") if isinstance(row.get("record"), dict) else {}
        rev = row.get("review") if isinstance(row.get("review"), dict) else {}
        st = rev.get("review_status")
        if not st:
            continue
        by_status[str(st)] += 1
        d = extract_summary_dimensions(rec)
        by_cat[d["disagreement_category_id"]] += 1
        by_gap[d["shape_gap_strength"]] += 1
        by_trust[d["trust_breeden"]] += 1
        by_bench[d["benchmark_method"]] += 1
        by_class[d["classifier_version"]] += 1

    return {
        "n_reviewed": sum(by_status.values()),
        "by_review_status": dict(by_status),
        "by_disagreement_category": dict(by_cat),
        "by_shape_gap_strength": dict(by_gap),
        "by_trust_breeden": dict(by_trust),
        "by_benchmark_method": dict(by_bench),
        "by_classifier_version": dict(by_class),
        "operator_summary_line": operator_guidance_line(by_status),
    }


_ROLLUP_COUNT_KEYS: tuple[str, ...] = (
    "by_review_status",
    "by_disagreement_category",
    "by_shape_gap_strength",
    "by_trust_breeden",
    "by_benchmark_method",
    "by_classifier_version",
)


def serialize_rollup_csv(rollup: dict[str, Any]) -> str:
    """Flat CSV for Phase 6 rollup download (metric, bucket, count)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["metric", "bucket", "count"])
    writer.writerow(["n_reviewed", "", rollup.get("n_reviewed", 0)])
    for metric in _ROLLUP_COUNT_KEYS:
        counts = rollup.get(metric)
        if not isinstance(counts, dict):
            continue
        for bucket, count in sorted(counts.items(), key=lambda kv: str(kv[0])):
            writer.writerow([metric, bucket, count])
    writer.writerow(
        ["operator_summary_line", "", rollup.get("operator_summary_line", "")]
    )
    return buf.getvalue()
