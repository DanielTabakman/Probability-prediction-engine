"""Generic fix agent for phone-triggered ntfy commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ppe_operator_status import collect_operator_status
from scripts.ppe_remote_agent import launch_agent_background


def build_fix_prompt(repo: Path, *, user_note: str = "") -> str:
    status = collect_operator_status(repo.resolve())
    parts = [
        "Operator sent **fix** from phone. Investigate and fix if possible.",
        f"Verdict: {status.get('verdict')}",
        f"Blocker: {status.get('blocker')}",
    ]
    for cmd in status.get("commands") or []:
        parts.append(f"- {cmd}")
    if user_note.strip():
        parts.append(user_note.strip())
    return "\n".join(parts)


def launch_fix_cli(
    repo: Path,
    *,
    user_note: str = "",
    source: str = "phone",
    status: dict[str, Any] | None = None,
    prompt: str | None = None,
) -> dict[str, Any]:
    """Start headless CLI fix worker only (no IDE handoff)."""
    repo = repo.resolve()
    if status is None:
        status = collect_operator_status(repo)
    if prompt is None:
        prompt = build_fix_prompt(repo, user_note=user_note)

    out = launch_agent_background(
        repo,
        prompt=prompt,
        log_name="REMOTE_FIX_AGENT.log",
        started_message="Fix agent started on desktop.",
        notify_ok_title="PPE fix finished",
        notify_fail_title="PPE fix failed",
        handoff={
            "mode": "fix",
            "verdict": str(status.get("verdict") or "UNKNOWN"),
            "blocker": str(status.get("blocker") or ""),
            "source": source,
            "user_note": user_note,
        },
    )
    return {"action": "fix", **out}


def launch_fix_agent(repo: Path, *, user_note: str = "") -> dict[str, Any]:
    """Phone fix: CLI when allowed, otherwise IDE handoff."""
    from scripts.ppe_remote_agent_dispatch import respond_remote_agent

    return respond_remote_agent(repo, mode="fix", source="phone", note=user_note)
