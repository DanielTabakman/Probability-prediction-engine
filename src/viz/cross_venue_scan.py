"""Cross-venue scan — rank Polymarket vs options-implied probability gaps."""

from __future__ import annotations

import json
from typing import Any

DEFAULT_GAP_COLUMN = "gap_bl_minus_pm_pct"
SCAN_JSON_VERSION = 1


def _parse_pct(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def rank_cross_venue_rows(
    rows: list[dict[str, str]],
    *,
    gap_column: str = DEFAULT_GAP_COLUMN,
    min_abs_gap_pct: float = 0.0,
) -> list[dict[str, str]]:
    """Rank export rows by absolute gap (largest first); drop rows without a gap."""
    ranked: list[tuple[float, dict[str, str]]] = []
    for row in rows:
        gap = _parse_pct(row.get(gap_column))
        if gap is None:
            continue
        if abs(gap) < min_abs_gap_pct:
            continue
        ranked.append((abs(gap), row))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in ranked]


def build_cross_venue_scan_report(
    rows: list[dict[str, str]],
    *,
    gap_column: str = DEFAULT_GAP_COLUMN,
    min_abs_gap_pct: float = 0.0,
    max_rows: int | None = None,
) -> dict[str, Any]:
    """Build structured scan report from cross-venue export rows."""
    ranked = rank_cross_venue_rows(
        rows,
        gap_column=gap_column,
        min_abs_gap_pct=min_abs_gap_pct,
    )
    if max_rows is not None:
        ranked = ranked[: max(0, max_rows)]

    as_of_utc = ranked[0].get("as_of_utc", "") if ranked else ""
    entries: list[dict[str, Any]] = []
    for rank, row in enumerate(ranked, start=1):
        gap = _parse_pct(row.get(gap_column))
        entries.append(
            {
                "rank": rank,
                "question": row.get("question", ""),
                "strike_usd": row.get("strike_usd", ""),
                "resolution_date": row.get("resolution_date", ""),
                "polymarket_yes_pct": row.get("polymarket_yes_pct", ""),
                "options_bl_p_above_pct": row.get("options_bl_p_above_pct", ""),
                gap_column: row.get(gap_column, ""),
                "abs_gap_pct": abs(gap) if gap is not None else None,
                "match_status": row.get("match_status", ""),
            }
        )

    return {
        "version": SCAN_JSON_VERSION,
        "as_of_utc": as_of_utc,
        "gap_column": gap_column,
        "row_count": len(entries),
        "entries": entries,
    }


def render_cross_venue_scan_markdown(report: dict[str, Any]) -> str:
    """Human-readable ranked gap report."""
    lines = [
        "# Cross-venue scan report",
        "",
        f"**As-of:** {report.get('as_of_utc') or '—'}",
        f"**Ranked rows:** {report.get('row_count', 0)}",
        "",
        "| Rank | Question | Strike | PM % | Options BL % | Gap (BL−PM) % | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for entry in report.get("entries") or []:
        question = str(entry.get("question") or "").replace("|", "\\|")
        lines.append(
            "| {rank} | {question} | {strike} | {pm} | {bl} | {gap} | {status} |".format(
                rank=entry.get("rank", ""),
                question=question[:80],
                strike=entry.get("strike_usd", ""),
                pm=entry.get("polymarket_yes_pct", ""),
                bl=entry.get("options_bl_p_above_pct", ""),
                gap=entry.get(DEFAULT_GAP_COLUMN, ""),
                status=entry.get("match_status", ""),
            )
        )
    lines.append("")
    return "\n".join(lines)


def serialize_cross_venue_scan_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
