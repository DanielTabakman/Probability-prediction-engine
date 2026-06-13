"""Mobile ntfy when relay slices or chapters complete."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    "mvp1_mobile_research_demo_v1": (
        "Charter mobile demo relay if not done, then run ppe_queue_insert_after after public launch. "
        "Test marketstructureos.com on your phone."
    ),
}

PIPELINE_IDLE_CHECK_IN = (
    "All chartered chapters complete — queue idle. Check in: review site URLs, "
    "then add next backlog row or run outreach."
)

QUEUE_SKIP_STATE_REL = "artifacts/control_plane/QUEUE_SKIP_NOTIFY_STATE.json"


def check_in_notify_enabled() -> bool:
    raw = os.environ.get("PPE_NTFY_CHECK_IN", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def queue_skip_notify_enabled() -> bool:
    raw = os.environ.get("PPE_NTFY_QUEUE_SKIP", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def queue_skip_notify_hours() -> float:
    raw = os.environ.get("PPE_NTFY_QUEUE_SKIP_HOURS", "6").strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 6.0


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


def _queue_skip_state_path(repo: Path) -> Path:
    return repo / QUEUE_SKIP_STATE_REL


def _load_queue_skip_state(repo: Path) -> dict[str, Any]:
    path = _queue_skip_state_path(repo)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}


def _save_queue_skip_state(repo: Path, state: dict[str, Any]) -> None:
    path = _queue_skip_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _parse_utc(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _skip_notify_key(plan_path: str, reason: str, *, kind: str) -> str:
    blob = f"{kind}|{plan_path}|{reason}".encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def _skip_notify_due(repo: Path, key: str) -> bool:
    hours = queue_skip_notify_hours()
    if hours <= 0:
        return True
    state = _load_queue_skip_state(repo)
    last = _parse_utc(str(state.get(key) or ""))
    if last is None:
        return True
    age_h = (datetime.now(timezone.utc) - last).total_seconds() / 3600.0
    return age_h >= hours


def _mark_skip_notified(repo: Path, key: str) -> None:
    state = _load_queue_skip_state(repo)
    state[key] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    _save_queue_skip_state(repo, state)


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


def notify_chapter_skipped(
    repo: Path,
    *,
    skipped_chapter_id: str,
    skipped_plan: str,
    reason: str,
    continued_with_chapter_id: str = "",
    continued_with_plan: str = "",
) -> bool:
    """Phone ping when a blocked chapter was skipped and the loop continued elsewhere."""
    if not progress_notify_enabled() or not queue_skip_notify_enabled():
        return False

    key = _skip_notify_key(skipped_plan, reason, kind="skip")
    if not _skip_notify_due(repo, key):
        return False

    if continued_with_plan:
        title = f"PPE skipped: {skipped_chapter_id}"
        body = (
            f"Blocked: {reason}. "
            f"Continuing with {continued_with_chapter_id or continued_with_plan}."
        )
    else:
        title = f"PPE queue blocked: {skipped_chapter_id}"
        body = f"Could not select: {reason}. No other selectable chapter — check backlog or set urgent:true."

    sent = send_ntfy(
        title,
        body,
        tags=["ppe", "queue", "skip"],
        priority="high",
    )
    if sent:
        _mark_skip_notified(repo, key)
    return sent


def notify_queue_selection_skips(
    repo: Path,
    skipped: list[Any],
    *,
    selected_plan: str | None,
    selected_chapter_id: str = "",
) -> int:
    """Notify for each newly skipped chapter (deduped). Returns count sent."""
    if not skipped:
        return 0
    from scripts.ppe_queue_selection import chapter_id_for_plan

    sent = 0
    for row in skipped:
        if hasattr(row, "plan_path"):
            plan = str(row.plan_path)
            cid = str(row.chapter_id)
            reason = str(row.reason)
        elif isinstance(row, dict):
            plan = str(row.get("planPath") or "")
            cid = str(row.get("chapterId") or "")
            reason = str(row.get("reason") or "")
        else:
            continue
        if not cid and plan:
            cid = chapter_id_for_plan(repo, plan)
        if notify_chapter_skipped(
            repo,
            skipped_chapter_id=cid,
            skipped_plan=plan,
            reason=reason,
            continued_with_chapter_id=selected_chapter_id,
            continued_with_plan=selected_plan or "",
        ):
            sent += 1
    return sent


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
    sent = send_ntfy(
        title,
        " ".join(parts),
        tags=["ppe", "slice", "done"],
        priority="default",
    )
    if sent:
        try:
            from scripts.ppe_notify_push import repo_root
            from scripts.ppe_operator_daily_metrics import record_slice_completed

            record_slice_completed(repo_root(), slice_id=slice_id, plan_path=plan_path)
        except ImportError:
            pass
    return sent


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
    sent = send_ntfy(
        title,
        " ".join(parts),
        tags=["ppe", "chapter", "done"],
        priority="high",
    )
    if sent:
        try:
            from scripts.ppe_notify_push import repo_root
            from scripts.ppe_operator_daily_metrics import record_chapter_completed

            record_chapter_completed(repo_root(), chapter_id=chapter_id)
        except ImportError:
            pass
    return sent
