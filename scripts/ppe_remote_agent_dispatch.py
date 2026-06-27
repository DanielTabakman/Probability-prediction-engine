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
from scripts.ppe_build_worker import WORKER_CODEX_CLI, WORKER_CURSOR_CLI

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
    from scripts.ppe_build_worker import resolve_build_worker
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

    resolved = resolve_build_worker(repo, force_handoff=force_handoff)
    try_headless = (
        should_attempt_headless_cli(repo, mode="build", force_handoff=force_handoff)
        and resolved.get("mode") == "headless"
        and not force_handoff
    )
    cli_out: dict[str, Any] = {}
    workers_tried: list[str] = []
    if try_headless:
        for worker in _headless_worker_chain(resolved):
            workers_tried.append(worker)
            cli_out = launch_build(repo, note=note, source=source, worker=worker)
            if cli_out.get("started"):
                cli_out["build_worker"] = worker
                cli_out["workers_tried"] = workers_tried
                return cli_out

    reason = headless_cli_skip_reason(repo, try_cli=try_headless, cli_out=cli_out)
    handoff = launch_ide_handoff(
        repo,
        slice_id=slice_id,
        plan_path=plan_path,
        source=source,
        reason=reason,
        force=force_handoff,
    )
    handoff["cli_attempted"] = try_headless
    handoff["workers_tried"] = workers_tried
    return handoff


def _headless_worker_chain(resolved: dict[str, Any]) -> list[str]:
    primary = str(resolved.get("worker") or WORKER_CURSOR_CLI)
    chain = [primary]
    if primary == WORKER_CURSOR_CLI and resolved.get("codex_cli_available"):
        chain.append(WORKER_CODEX_CLI)
    elif primary == WORKER_CODEX_CLI:
        pass
    return chain


def _respond_fix(
    repo: Path,
    *,
    source: str,
    note: str,
    force_handoff: bool,
) -> dict[str, Any]:
    from scripts.ppe_build_worker import resolve_build_worker
    from scripts.ppe_operator_status import VERDICT_IDE_BUILD, collect_operator_status
    from scripts.ppe_remote_fix_agent import build_fix_prompt, launch_fix_cli

    repo = repo.resolve()
    status = collect_operator_status(repo)
    verdict = str(status.get("verdict") or "UNKNOWN")
    if verdict == VERDICT_IDE_BUILD:
        return _respond_build(repo, source=source, note=note, force_handoff=force_handoff)
    blocker = str(status.get("blocker") or "")
    prompt = build_fix_prompt(repo, user_note=note)

    resolved = resolve_build_worker(repo, force_handoff=force_handoff)
    try_cli = (
        should_attempt_headless_cli(repo, mode="fix", force_handoff=force_handoff)
        and resolved.get("mode") == "headless"
        and not force_handoff
    )
    cli_out: dict[str, Any] = {}
    workers_tried: list[str] = []
    if try_cli:
        for worker in _headless_worker_chain(resolved):
            workers_tried.append(worker)
            cli_out = launch_fix_cli(
                repo,
                user_note=note,
                source=source,
                status=status,
                prompt=prompt,
                worker=worker,
            )
            if cli_out.get("started"):
                cli_out["workers_tried"] = workers_tried
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
    handoff["workers_tried"] = workers_tried
    return handoff
