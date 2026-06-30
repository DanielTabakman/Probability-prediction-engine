"""Cross-venue tradeability — net gap after spread/cost proxy."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

TRADEABILITY_JSON_VERSION = 1
DEFAULT_REPORT_ROOT = Path("artifacts") / "cross_venue_tradeability"


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def score_tradeability_row(row: dict[str, str]) -> dict[str, Any] | None:
    if str(row.get("match_status") or "") != "ok":
        return None
    gap = _parse_float(row.get("gap_bl_minus_pm_pct"))
    cost = _parse_float(row.get("spread_proxy_prob_pct"))
    if gap is None:
        return None
    abs_gap = abs(gap)
    cost_pct = cost if cost is not None else 0.0
    net_edge_pct = round(abs_gap - cost_pct, 4)
    return {
        "question": row.get("question", ""),
        "strike_usd": row.get("strike_usd", ""),
        "resolution_date": row.get("resolution_date", ""),
        "as_of_utc": row.get("as_of_utc", ""),
        "abs_gap_pct": round(abs_gap, 4),
        "spread_proxy_prob_pct": round(cost_pct, 4),
        "net_edge_pct": net_edge_pct,
        "tradeable_after_costs": net_edge_pct > 0,
        "gap_bl_minus_pm_pct": row.get("gap_bl_minus_pm_pct", ""),
        "polymarket_yes_pct": row.get("polymarket_yes_pct", ""),
        "options_bl_p_above_pct": row.get("options_bl_p_above_pct", ""),
    }


def build_cross_venue_tradeability_report(
    rows: list[dict[str, str]],
    *,
    as_of_utc: str | None = None,
) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        entry = score_tradeability_row(row)
        if entry is not None:
            scored.append(entry)
    tradeable = [r for r in scored if r.get("tradeable_after_costs")]
    tradeable.sort(key=lambda r: float(r.get("net_edge_pct") or 0), reverse=True)
    scored.sort(key=lambda r: float(r.get("abs_gap_pct") or 0), reverse=True)
    return {
        "version": TRADEABILITY_JSON_VERSION,
        "as_of_utc": as_of_utc or datetime.now(tz=UTC).isoformat(),
        "row_count": len(rows),
        "scored_count": len(scored),
        "tradeable_count": len(tradeable),
        "strategy_ready": len(tradeable) > 0,
        "strategy_ready_reason": (
            f"{len(tradeable)} rows with net gap after spread proxy > 0"
            if tradeable
            else "no rows with net edge after spread proxy"
        ),
        "entries": scored,
        "tradeable": tradeable,
    }


def render_cross_venue_tradeability_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Cross-venue tradeability report",
        "",
        f"**As-of:** {report.get('as_of_utc') or '—'}",
        f"**Scored rows:** {report.get('scored_count', 0)}",
        f"**Tradeable after costs:** {report.get('tradeable_count', 0)}",
        f"**Strategy-ready signal:** {report.get('strategy_ready')}",
        "",
    ]
    tradeable = report.get("tradeable") or []
    if tradeable:
        lines.extend(
            [
                "## Net edge after spread proxy",
                "",
                "| Question | |Gap| | Cost % | Net % |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for entry in tradeable[:20]:
            q = str(entry.get("question") or "").replace("|", "\\|")[:50]
            lines.append(
                "| {q} | {g:.2f} | {c:.2f} | {n:.2f} |".format(
                    q=q,
                    g=float(entry.get("abs_gap_pct") or 0),
                    c=float(entry.get("spread_proxy_prob_pct") or 0),
                    n=float(entry.get("net_edge_pct") or 0),
                )
            )
        lines.append("")
    return "\n".join(lines)


def serialize_cross_venue_tradeability_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def write_cross_venue_tradeability_reports(
    report: dict[str, Any],
    *,
    report_root: Path = DEFAULT_REPORT_ROOT,
) -> tuple[Path, Path]:
    report_root.mkdir(parents=True, exist_ok=True)
    md_path = report_root / "latest_report.md"
    json_path = report_root / "latest_summary.json"
    md_path.write_text(render_cross_venue_tradeability_markdown(report), encoding="utf-8")
    json_path.write_text(serialize_cross_venue_tradeability_json(report), encoding="utf-8")
    return md_path, json_path
