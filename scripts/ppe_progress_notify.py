"""Mobile ntfy when relay slices or chapters complete."""

from __future__ import annotations

import os

from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy

# Operator check-in hints after chapter closeout (phone ntfy body append / second ping).
CHECK_IN_HINTS: dict[str, str] = {
    "mvp1_distribution_quant_research_v2": (
        "Dist-quant chapter done. Next: visual parity auto-starts if loop is running."
    ),
    "msos_storyboard_visual_parity_v1": (
        "Open marketstructureos.com routes vs storyboard HTML. Reply status on phone if URLs look wrong."
    ),
    "msos_public_demo_launch_v1": (
        "Public demo launch done. Check apex homepage + /command-center + research beta CTA. "
        "Log one row in VALIDATION_REALITY_CHECKS if demo-ready."
    ),
}

PIPELINE_IDLE_CHECK_IN = (
    "All chartered chapters complete — queue idle. Check in: review site URLs, "
    "then add next backlog row or run outreach."
)


def check_in_notify_enabled() -> bool:
    raw = os.environ.get("PPE_NTFY_CHECK_IN", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def progress_notify_mode() -> str:
    """off | chapter (default) | all — controls relay/fix progress pings."""
    raw = os.environ.get("PPE_NTFY_PROGRESS", "chapter").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return "off"
    if raw in ("1", "true", "yes", "on", "all", "full"):
        return "all"
    return "chapter"


def progress_notify_enabled() -> bool:
    return progress_notify_mode() != "off" and notify_enabled() and ntfy_configured()


def _slice_progress_enabled() -> bool:
    return progress_notify_mode() == "all"


def _fix_progress_enabled() -> bool:
    return progress_notify_mode() == "all"


def check_in_hint_for_chapter(chapter_id: str) -> str:
    key = str(chapter_id or "").strip().lower()
    return CHECK_IN_HINTS.get(key, "")


def notify_operator_check_in(
    headline: str,
    *,
    detail: str = "",
    chapter_id: str = "",
) -> bool:
    """Actionable phone ping when the loop thinks operator review is needed."""
    if not progress_notify_enabled() or not check_in_notify_enabled():
        return False
    title = f"PPE check in: {headline}"
    parts: list[str] = []
    if detail:
        parts.append(detail)
    hint = check_in_hint_for_chapter(chapter_id) if chapter_id else ""
    if hint and hint not in detail:
        parts.append(hint)
    if not parts:
        parts.append("Review operator status and next backlog item.")
    return send_ntfy(
        title,
        " ".join(parts),
        tags=["ppe", "checkin", "operator"],
        priority="high",
    )


def notify_pipeline_idle(*, last_chapter: str = "") -> bool:
    """Ping when manifest is idle and no READY queue item remains."""
    detail = PIPELINE_IDLE_CHECK_IN
    if last_chapter:
        detail = f"After {last_chapter}. {detail}"
    return notify_operator_check_in("pipeline idle", detail=detail, chapter_id=last_chapter)


def notify_slice_complete(
    slice_id: str,
    *,
    plan_path: str = "",
    chapter_id: str = "",
) -> bool:
    if not progress_notify_enabled() or not _slice_progress_enabled():
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
    if not progress_notify_enabled() or not _fix_progress_enabled():
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
    if not progress_notify_enabled() or not _fix_progress_enabled():
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
    hint = check_in_hint_for_chapter(chapter_id)
    if hint:
        parts.append(f"Check in: {hint}")
    return send_ntfy(
        title,
        " ".join(parts),
        tags=["ppe", "chapter", "done"],
        priority="high",
    )
