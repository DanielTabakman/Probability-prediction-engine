"""Shared CLI → IDE handoff dispatch for phone/loop agent commands (build, fix)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from scripts.ppe_ide_handoff import (
    headless_cli_skip_reason,
    launch_ide_fix_handoff,
    launch_ide_handoff,
    should_attempt_headless_cli,
)

AgentCommandMode = Literal["build", "fix"]


def respond_remote_agent(
    repo: Path,
    *,
    mode: AgentCommandMode,
    source: str,
    note: str = "",
    force_handoff: bool = False,
) -> dict[str, Any]:
    """Try headless CLI when allowed; otherwise surface IDE handoff."""
    if mode == "build":
        return _respond_build(repo, source=source, note=note, force_handoff=force_handoff)
    return _respond_fix(repo, source=source, note=note, force_handoff=force_handoff)


def _respond_build(
    repo: Path,
    *,
    source: str,
    note: str,
    force_handoff: bool,
) -> dict[str, Any]:
    from scripts.ppe_remote_agent import agent_available
    from scripts.ppe_remote_build_agent import launch_build, read_build_lock, resolve_build_target

    repo = repo.resolve()
    target = resolve_build_target(repo)
    if not target.get("ok"):
        return {"action": "ide_build", "started": False, **target}
    if target.get("mode") == "run_local":
        return launch_build(repo, note=note, source=source)

    slice_id = str(target["slice_id"])
    plan_path = str(target["plan_path"])

    if read_build_lock(repo):
        return {
            "action": "ide_build",
            "started": False,
            "reason": f"build already in flight for {slice_id}",
            "slice_id": slice_id,
        }

    try_cli = (
        should_attempt_headless_cli(repo, mode="build", force_handoff=force_handoff)
        and agent_available()
        and not force_handoff
    )
    cli_out: dict[str, Any] = {}
    if try_cli:
        cli_out = launch_build(repo, note=note, source=source)
        if cli_out.get("started"):
            return cli_out

    reason = headless_cli_skip_reason(repo, try_cli=try_cli, cli_out=cli_out)
    handoff = launch_ide_handoff(
        repo,
        slice_id=slice_id,
        plan_path=plan_path,
        source=source,
        reason=reason,
        force=force_handoff,
    )
    handoff["cli_attempted"] = try_cli
    return handoff


def _respond_fix(
    repo: Path,
    *,
    source: str,
    note: str,
    force_handoff: bool,
) -> dict[str, Any]:
    from scripts.ppe_operator_status import collect_operator_status
    from scripts.ppe_remote_agent import agent_available
    from scripts.ppe_remote_fix_agent import build_fix_prompt, launch_fix_cli

    repo = repo.resolve()
    status = collect_operator_status(repo)
    verdict = str(status.get("verdict") or "UNKNOWN")
    blocker = str(status.get("blocker") or "")
    prompt = build_fix_prompt(repo, user_note=note)

    try_cli = (
        should_attempt_headless_cli(repo, mode="fix", force_handoff=force_handoff)
        and agent_available()
        and not force_handoff
    )
    cli_out: dict[str, Any] = {}
    if try_cli:
        cli_out = launch_fix_cli(
            repo,
            user_note=note,
            source=source,
            status=status,
            prompt=prompt,
        )
        if cli_out.get("started"):
            return cli_out

    reason = headless_cli_skip_reason(repo, try_cli=try_cli, cli_out=cli_out)
    handoff = launch_ide_fix_handoff(
        repo,
        verdict=verdict,
        blocker=blocker,
        prompt=prompt,
        source=source,
        reason=reason,
        force=force_handoff,
    )
    handoff["cli_attempted"] = try_cli
    return handoff
