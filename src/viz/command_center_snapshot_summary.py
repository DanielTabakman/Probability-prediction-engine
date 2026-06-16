"""Read-only Command Center summary from PPE snapshot SQLite."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.viz.frozen_evaluation_store import (
    get_review_for_snapshot,
    list_recent,
    list_snapshots_pending_review,
    open_store,
)


def _review_tag(review: dict[str, Any] | None) -> tuple[str, str | None]:
    if review is None:
        return "Snapshot", "amber"
    status = str(review.get("review_status") or "").strip().lower()
    if status in ("", "pending"):
        return "Review pending", "amber"
    if status == "supportive":
        return "Review: supportive", "teal"
    if status == "contradictory":
        return "Review: contradictory", "rose"
    if status == "contaminated":
        return "Review: contaminated", "rose"
    if status == "not_judgeable":
        return "Review: not judgeable", "muted"
    return f"Review: {status}", "muted"


def build_command_center_summary(db_path: Path | None = None) -> dict[str, Any]:
    from src.viz.frozen_evaluation_store import default_db_path

    path = db_path or default_db_path()
    degraded: dict[str, Any] = {
        "status": "degraded",
        "reason": "PPE snapshot database not configured or unreachable.",
        "sourceLabel": "From PPE snapshots",
        "kpis": [],
        "currentWork": [],
    }
    if not path.is_file():
        degraded["reason"] = f"Snapshot database missing at {path.as_posix()}"
        return degraded
    try:
        conn = open_store(path)
    except OSError as exc:
        degraded["reason"] = f"Could not open snapshot database: {exc}"
        return degraded
    try:
        recent = list_recent(conn, limit=10)
        pending = list_snapshots_pending_review(conn, limit=50)
        reviewed = 0
        for row in recent:
            rev = get_review_for_snapshot(conn, str(row["id"]))
            if rev and str(rev.get("review_status") or "").lower() not in ("", "pending"):
                reviewed += 1
        kpis = [
            {
                "label": "Recent snapshots",
                "value": str(len(recent)),
                "sub": "Frozen evaluations in PPE store",
            },
            {
                "label": "Pending review",
                "value": str(len(pending)),
                "sub": "Awaiting outcome in review queue",
                **({"tone": "amber"} if pending else {}),
            },
            {
                "label": "Reviewed (recent)",
                "value": str(reviewed),
                "sub": "Recent rows with completed review",
            },
        ]
        current_work: list[dict[str, Any]] = []
        for row in recent[:6]:
            sid = str(row["id"])
            rev = get_review_for_snapshot(conn, sid)
            tag, tag_tone = _review_tag(rev)
            current_work.append(
                {
                    "name": str(row.get("expiry") or sid[:8]),
                    "tag": tag,
                    **({"tagTone": tag_tone} if tag_tone else {}),
                    "detail": str(row.get("summary_line") or "PPE snapshot"),
                }
            )
        return {
            "status": "live",
            "sourceLabel": "From PPE snapshots",
            "kpis": kpis,
            "currentWork": current_work,
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(build_command_center_summary(), indent=2))
    sys.exit(0)
