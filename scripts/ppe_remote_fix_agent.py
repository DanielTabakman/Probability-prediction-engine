"""Generic fix agent for phone-triggered ntfy commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ppe_operator_hint import resolve_operator_hint
from scripts.ppe_operator_status import VERDICT_IDE_BUILD, VERDICT_RUN_LOCAL, collect_operator_status

CONTINUITY_BRIEF = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"


def build_fix_prompt(repo: Path, *, user_note: str = "") -> str:
    repo = repo.resolve()
    status = collect_operator_status(repo)
    verdict = str(status.get("verdict") or "UNKNOWN")
    blocker = str(status.get("blocker") or "").strip()

    parts = [
        "Operator sent **fix** from phone. Investigate and fix if possible.",
        f"Verdict: {verdict}",
    ]
    if blocker:
        parts.append(f"Blocker: {blocker}")

    if verdict == VERDICT_IDE_BUILD:
        parts.extend(_ide_build_fix_lines(repo, status))
    elif verdict == VERDICT_RUN_LOCAL:
        parts.extend(
            [
                "",
                "Finish the chapter relay: run `run_ppe_local.cmd` (or `@ppe-finish-worker`).",
                "Do not start a new product slice until closeout completes.",
            ]
        )
    else:
        hint = resolve_operator_hint(verdict, repo=repo)
        if hint:
            parts.extend(["", f"Operator hint: {hint}"])

    avoid = status.get("avoid") or []
    if avoid:
        parts.append("")
        parts.append("Do NOT run:")
        for item in avoid:
            parts.append(f"- {item}")

    cmds = status.get("commands") or []
    if cmds and verdict != VERDICT_IDE_BUILD:
        parts.append("")
        parts.append("Suggested commands:")
        for cmd in cmds:
            parts.append(f"- {cmd}")

    parts.extend(
        [
            "",
            f"Load `@{CONTINUITY_BRIEF}` first.",
            "Execute autonomously; do not ask for confirmation.",
        ]
    )
    if user_note.strip():
        parts.append("")
        parts.append(user_note.strip())
    return "\n".join(parts)


def _ide_build_fix_lines(repo: Path, status: dict[str, Any]) -> list[str]:
    from scripts.ppe_ide_build_starter import starter_path, write_starter
    from scripts.ppe_ide_handoff import build_handoff_prompt
    from scripts.ppe_remote_build_agent import resolve_build_target

    target = resolve_build_target(repo)
    if not target.get("ok") or target.get("mode") != "ide_build":
        return [
            "",
            "IDE BUILD blocker but no product slice resolved — triage `OPERATOR_STATUS.md` "
            "or send `build` from phone.",
        ]

    slice_id = str(target["slice_id"])
    plan_path = str(target["plan_path"])
    starter_rel = starter_path(slice_id)
    try:
        write_starter(repo, slice_id=slice_id, plan_path=plan_path)
    except OSError:
        pass

    return [
        "",
        "This is an IDE BUILD blocker — implement the product slice (not generic triage):",
        build_handoff_prompt(slice_id=slice_id, starter_rel=starter_rel, plan_path=plan_path),
    ]


def launch_fix_cli(
    repo: Path,
    *,
    user_note: str = "",
    source: str = "phone",
    status: dict[str, Any] | None = None,
    prompt: str | None = None,
    worker: str | None = None,
) -> dict[str, Any]:
    """Start headless CLI fix worker only (no IDE handoff)."""
    from scripts.ppe_build_worker import WORKER_CURSOR_CLI, launch_build_worker_background, resolve_build_worker

    repo = repo.resolve()
    if status is None:
        status = collect_operator_status(repo)
    if prompt is None:
        prompt = build_fix_prompt(repo, user_note=user_note)

    resolved = resolve_build_worker(repo) if worker is None else {"worker": worker}
    build_worker = str(resolved.get("worker") or WORKER_CURSOR_CLI)

    out = launch_build_worker_background(
        repo,
        prompt=prompt,
        worker=build_worker,  # type: ignore[arg-type]
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
            "build_worker": build_worker,
        },
    )
    return {"action": "fix", "build_worker": build_worker, **out}


def launch_fix_agent(repo: Path, *, user_note: str = "") -> dict[str, Any]:
    """Phone fix: CLI when allowed, otherwise IDE handoff."""
    from scripts.ppe_remote_agent_dispatch import respond_remote_agent

    return respond_remote_agent(repo, mode="fix", source="phone", note=user_note)
