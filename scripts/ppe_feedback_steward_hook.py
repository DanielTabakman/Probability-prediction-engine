"""Auto-steward hook when MSOS feedback usefulness drops (tracking v4)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppe_export_web_feedback import format_digest_line, load_records, records_in_days, resolve_feedback_path

BACKLOG_ID = "tracking-feedback-usefulness-low"
DEFAULT_MIN_SUBMISSIONS = 2
DEFAULT_MAX_AVG_USEFULNESS = 3.0


def feedback_window_stats(repo: Path, *, days: int = 7) -> dict:
    records = records_in_days(load_records(resolve_feedback_path(None)), days)
    if not records:
        return {"count": 0, "avg_usefulness": None, "avg_repeat": None}
    avg_use = sum(int(r.get("usefulness") or 0) for r in records) / len(records)
    avg_repeat = sum(int(r.get("repeat_use_intent") or 0) for r in records) / len(records)
    return {"count": len(records), "avg_usefulness": avg_use, "avg_repeat": avg_repeat}


def upsert_feedback_backlog_item(repo: Path, *, stats: dict, days: int) -> bool:
    from scripts.ppe_human_backlog import backlog_path, load_backlog, render_markdown

    repo = repo.resolve()
    path = backlog_path(repo)
    backlog = load_backlog(repo)
    items = list(backlog.get("items") or [])
    title = "MSOS feedback usefulness below target"
    summary = (
        f"Last {days}d: {stats['count']} submission(s), avg usefulness "
        f"{stats['avg_usefulness']:.1f}/5 (repeat {stats['avg_repeat']:.1f}/5). "
        "Review confusion categories and ship UX fixes."
    )
    row = {
        "id": BACKLOG_ID,
        "title": title,
        "status": "open",
        "priority": "high",
        "category": "validation",
        "summary": summary,
        "added": datetime.now(timezone.utc).date().isoformat(),
        "source": "ppe_feedback_steward_hook",
        "policyQuestion": "Which confusion category drives low usefulness this week?",
    }
    replaced = False
    for idx, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("id") or "") == BACKLOG_ID:
            items[idx] = row
            replaced = True
            break
    if not replaced:
        items.append(row)
    backlog["items"] = items
    path.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
    (repo / "docs/SOP/HUMAN_STEWARD_BACKLOG.md").write_text(render_markdown(repo), encoding="utf-8")
    return True


def run_hook(
    repo: Path,
    *,
    days: int = 7,
    min_submissions: int = DEFAULT_MIN_SUBMISSIONS,
    max_avg: float = DEFAULT_MAX_AVG_USEFULNESS,
    dry_run: bool = False,
) -> dict:
    stats = feedback_window_stats(repo, days=days)
    digest = format_digest_line(repo, days=days)
    triggered = (
        stats["count"] >= min_submissions
        and stats["avg_usefulness"] is not None
        and stats["avg_usefulness"] < max_avg
    )
    if triggered and not dry_run:
        upsert_feedback_backlog_item(repo, stats=stats, days=days)
    return {"triggered": triggered, "stats": stats, "digest_line": digest}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Steward hook for low MSOS feedback usefulness.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    out = run_hook(args.repo_root.resolve(), days=args.days, dry_run=args.dry_run)
    if out["triggered"]:
        print(f"ppe_feedback_steward_hook: flagged usefulness {out['stats']['avg_usefulness']:.1f}/5")
    else:
        print("ppe_feedback_steward_hook: ok (no steward flag)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
