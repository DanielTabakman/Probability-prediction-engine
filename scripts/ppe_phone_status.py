"""Plain-language operator status for phone (ntfy) replies."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import (
    format_snooze_until,
    is_ntfy_quiet_hours,
    is_ntfy_snoozed,
    load_ntfy_snooze,
    quiet_hours_until_local,
)
from scripts.ppe_operator_hint import append_ppe_go_hint, ppe_go_hint_for_verdict

_SLICE_RE = re.compile(r"\[([^\]]+)\]")


def _short_plan(plan: str | None) -> str:
    if not plan:
        return ""
    name = Path(plan).stem
    return name.replace("_relay", "").replace("_", " ")


def _extract_slice_id(blocker: str | None) -> str | None:
    if not blocker:
        return None
    match = _SLICE_RE.search(blocker)
    if not match:
        return None
    raw = match.group(1).split(",")[0].strip()
    return raw or None


def _clean_blocker(blocker: str | None, *, verdict: str, slice_id: str | None) -> str:
    text = (blocker or "").strip()
    if not text:
        return ""
    if verdict == "IDE_BUILD" and slice_id:
        return f"Slice {slice_id} needs an IDE BUILD in Cursor."
    if "IDE product marker present" in text:
        return "Product slices built — relay (run_ppe_local) has not finished yet."
    if "manifest RUNNING" in text and "ACTIVE_RUN" in text:
        return "Manifest says running but no active run file - may need a reset."
    if "no READY queue item" in text.lower():
        return "Queue is empty - add a chapter to the backlog or wait for closeout."
    if "PPE_SKIP_ACP" in text or "IDE_PRODUCT_READY" in text:
        if slice_id:
            return f"Slice {slice_id} needs an IDE BUILD in Cursor."
    text = re.sub(r"\s*\([^)]*PPE_[^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:280]


def verdict_headline(verdict: str) -> str:
    return {
        "RUN_AUTO": "Running",
        "RUN_LOCAL": "Relay finish needed",
        "IDE_BUILD": "Needs you - IDE BUILD",
        "FIX_PLAN": "Needs fix - plan/spec",
        "STALE_STATE": "Stale state",
        "ERROR": "Error",
        "SUPPLY_LOW": "Idle - no work queued",
    }.get(verdict, verdict.replace("_", " ").title())


def phone_status_title(status: dict[str, Any]) -> str:
    verdict = str(status.get("verdict") or "UNKNOWN")
    if verdict == "RUN_AUTO":
        return "PPE: All good"
    if verdict == "RUN_LOCAL":
        return "PPE: relay not running"
    if verdict == "IDE_BUILD":
        slice_id = _extract_slice_id(str(status.get("blocker") or ""))
        if slice_id:
            return f"PPE: IDE BUILD - {slice_id}"
        return "PPE: IDE BUILD needed"
    return f"PPE: {verdict_headline(verdict)}"


def _stack_line(stack: dict[str, Any] | None) -> str:
    stack = stack or {}
    loop = "on" if stack.get("loop_running") else "off"
    watch = "on" if stack.get("watch_running") else "off"
    listen = "on" if stack.get("ntfy_listen_running") else "off"
    return f"Desktop: loop {loop} · watch {watch} · phone cmds {listen}"


def _next_step(
    status: dict[str, Any],
    *,
    slice_id: str | None,
    stack: dict[str, Any] | None = None,
) -> str:
    verdict = str(status.get("verdict") or "")
    loop_running = bool((stack or {}).get("loop_running"))
    if verdict in ("RUN_AUTO",):
        return "Nothing needed on your phone - auto-loop is running."
    if verdict == "RUN_LOCAL":
        if loop_running:
            return (
                "Loop is up but relay is not running — auto-run_local should start run_ppe_local. "
                "If stuck, send build from phone or run run_ppe_local.cmd on the desktop."
            )
        return "Loop is off — send restart from phone or run run_ppe_desktop_operator.cmd on the PC."
    if verdict == "SUPPLY_LOW":
        return "No queued chapter ready — add backlog or clear focus gate. Loop will idle-sleep briefly."
    hint = ppe_go_hint_for_verdict(verdict)
    if hint:
        return f"On desktop: {hint}"
    cmds = status.get("commands") or []
    if cmds:
        return f"Next: {cmds[0]}"
    if slice_id:
        return f"Check slice {slice_id} on the desktop."
    return "Send fix or status from phone for more detail."


def _status_footer(repo: Path | None) -> str | None:
    lines: list[str] = []
    if repo is not None:
        snooze = load_ntfy_snooze(repo)
        if snooze and is_ntfy_snoozed(repo):
            until = format_snooze_until(str(snooze.get("until") or ""))
            lines.append(f"Snoozed until {until}")
    if is_ntfy_quiet_hours():
        lines.append(f"Quiet hours: routine alerts off until {quiet_hours_until_local()} local")
    if not lines:
        return None
    return "\n".join(lines)


def format_phone_status(
    status: dict[str, Any],
    *,
    stack: dict[str, Any] | None = None,
    repo: Path | None = None,
) -> str:
    """Multi-line body for phone status command (and similar ntfy replies)."""
    verdict = str(status.get("verdict") or "UNKNOWN")
    headline = verdict_headline(verdict)
    blocker = str(status.get("blocker") or "")
    slice_id = _extract_slice_id(blocker)
    chapter = str(status.get("chapter_name") or "").strip()
    plan_short = _short_plan(str(status.get("phase_plan_path") or ""))

    lines: list[str] = [headline, ""]

    if chapter:
        lines.append(f"Chapter: {chapter}")
    elif plan_short:
        lines.append(f"Plan: {plan_short}")
    if slice_id and verdict == "IDE_BUILD":
        lines.append(f"Slice: {slice_id}")

    detail = _clean_blocker(blocker, verdict=verdict, slice_id=slice_id)
    if detail and verdict not in ("RUN_AUTO",):
        lines.append(detail)

    lines.append("")
    lines.append(_next_step(status, slice_id=slice_id, stack=stack))

    if stack is not None:
        lines.append("")
        lines.append(_stack_line(stack))

    hint = ppe_go_hint_for_verdict(verdict)
    if hint and hint not in "\n".join(lines):
        lines.append(append_ppe_go_hint("", verdict).strip())

    footer = _status_footer(repo)
    if footer:
        lines.extend(["", footer])

    return "\n".join(line for line in lines if line is not None).strip()


def format_phone_alert_body(
    status: dict[str, Any],
    *,
    kind: str = "verdict_change",
    prior_verdict: str = "",
) -> str:
    """Shorter body for watch-loop push alerts."""
    verdict = str(status.get("verdict") or "")
    blocker = str(status.get("blocker") or "")
    slice_id = _extract_slice_id(blocker)
    chapter = str(status.get("chapter_name") or "").strip()

    if kind == "cleared":
        parts = ["Guard cleared - loop can continue."]
        if prior_verdict:
            parts.insert(0, f"Was: {prior_verdict}.")
        parts.append(f"Now: {verdict_headline(verdict)}.")
        return " ".join(parts)

    if kind == "stuck":
        detail = _clean_blocker(blocker, verdict=verdict, slice_id=slice_id) or verdict
        return f"Still stuck. {detail}"

    if kind == "loop_down":
        return "Auto-loop is not running on the desktop. Run run_ppe_desktop_operator.cmd on the PC."

    lines = [verdict_headline(verdict)]
    if chapter:
        lines.append(chapter)
    detail = _clean_blocker(blocker, verdict=verdict, slice_id=slice_id)
    if detail:
        lines.append(detail)
    hint = append_ppe_go_hint("", verdict).strip()
    if hint:
        lines.append(hint)
    return "\n".join(lines)
