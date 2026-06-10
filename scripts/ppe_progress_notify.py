"""Mobile ntfy when relay slices or chapters complete."""

from __future__ import annotations

import os

from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy


def progress_notify_enabled() -> bool:
    if os.environ.get("PPE_NTFY_PROGRESS", "").strip().lower() in ("0", "false", "no", "off"):
        return False
    return notify_enabled() and ntfy_configured()


def notify_slice_complete(
    slice_id: str,
    *,
    plan_path: str = "",
    chapter_id: str = "",
) -> bool:
    if not progress_notify_enabled():
        return False
    title = f"PPE slice done: {slice_id}"
    parts = [f"Slice {slice_id} finished."]
    if chapter_id:
        parts.append(f"Chapter: {chapter_id}.")
    if plan_path:
        parts.append(f"Plan: {plan_path}")
    return send_ntfy(
        title,
        " ".join(parts),
        tags=["ppe", "slice", "done"],
        priority="default",
    )


def notify_fix_working(
    issue: str,
    *,
    detail: str = "",
    plan_path: str = "",
) -> bool:
    """Phone ping when an operator/agent starts fixing a blocked state."""
    if not progress_notify_enabled():
        return False
    title = f"PPE fixing: {issue}"
    parts = [f"Working on: {issue}."]
    if detail:
        parts.append(detail)
    if plan_path:
        parts.append(f"Plan: {plan_path}")
    return send_ntfy(
        title,
        " ".join(parts),
        tags=["ppe", "fix", "working"],
        priority="default",
    )


def notify_fix_resolved(
    issue: str,
    *,
    summary: str = "",
    verdict: str = "",
    plan_path: str = "",
) -> bool:
    """Phone ping when a fix attempt finishes (success or still blocked)."""
    if not progress_notify_enabled():
        return False
    if verdict:
        title = f"PPE fixed ({verdict}): {issue}"
    else:
        title = f"PPE fix done: {issue}"
    parts: list[str] = []
    if summary:
        parts.append(summary)
    else:
        parts.append(f"Fix attempt finished for {issue}.")
    if verdict:
        parts.append(f"Verdict: {verdict}.")
    if plan_path:
        parts.append(f"Plan: {plan_path}")
    priority = "high" if verdict in ("RUN_AUTO", "RUN_LOCAL") else "default"
    return send_ntfy(
        title,
        " ".join(parts),
        tags=["ppe", "fix", "done"],
        priority=priority,
    )


def notify_chapter_complete(
    chapter_id: str,
    *,
    slice_id: str = "",
    plan_path: str = "",
    next_chapter: str = "",
) -> bool:
    if not progress_notify_enabled():
        return False
    title = f"PPE chapter done: {chapter_id}"
    parts = [f"Chapter {chapter_id} COMPLETE."]
    if slice_id:
        parts.append(f"Closeout slice: {slice_id}.")
    if next_chapter:
        parts.append(f"Next queued: {next_chapter}.")
    elif plan_path:
        parts.append("Queue propagating next chapter.")
    return send_ntfy(
        title,
        " ".join(parts),
        tags=["ppe", "chapter", "done"],
        priority="high",
    )
