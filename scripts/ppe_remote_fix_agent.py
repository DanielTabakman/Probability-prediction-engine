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


def launch_fix_agent(repo: Path, *, user_note: str = "") -> dict[str, Any]:
    repo = repo.resolve()
    prompt = build_fix_prompt(repo, user_note=user_note)

    out = launch_agent_background(
        repo,
        prompt=prompt,
        log_name="REMOTE_FIX_AGENT.log",
        started_message="Fix agent started on desktop.",
        notify_ok_title="PPE fix finished",
        notify_fail_title="PPE fix failed",
    )
    return {"action": "fix", **out}
