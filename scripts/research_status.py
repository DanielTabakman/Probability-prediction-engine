"""Human-readable research pipeline status."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research_archive_health import _console_safe, format_health_line  # noqa: E402
from src.viz.research_summary import build_research_summary  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Print research pipeline status")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    summary = build_research_summary(repo)

    print("Research pipeline status")
    print("=" * 40)
    for item in summary.get("archives") or []:
        if isinstance(item, dict):
            print(format_health_line(item))
    stale = summary.get("stale_collectors") or []
    if stale:
        print("")
        print("Stale collectors (check VM tasks):")
        for item in stale:
            if isinstance(item, dict):
                print(
                    f"  - {_console_safe(str(item.get('label') or item.get('id')))}: "
                    f"last {item.get('last_snapshot_utc') or 'never'}"
                )

    cv = summary.get("cross_venue") or {}
    if cv:
        print("")
        print("Cross-venue:")
        if cv.get("top_gap_pct") is not None:
            print(f"  Top gap today: {cv.get('top_gap_pct')}%")
        bt = cv.get("backtest") or {}
        print(
            f"  Backtest: resolved={bt.get('resolved_count', 0)} "
            f"strategy_ready={bt.get('strategy_ready', False)}"
        )
        tr = cv.get("tradeability") or {}
        print(f"  Tradeability: tradeable={tr.get('tradeable_count', 0)} strategy_ready={tr.get('strategy_ready', False)}")
        tbt = cv.get("tradeability_backtest") or {}
        if tbt.get("tradeable_resolved_count"):
            print(
                f"  Tradeability backtest: n={tbt.get('tradeable_resolved_count')} "
                f"bl_beat_pm={tbt.get('bl_beat_pm_rate')}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
