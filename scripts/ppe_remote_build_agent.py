"""Phone-triggered IDE BUILD for the active queued product slice."""

from __future__ import annotations

import subprocess
import threading
from pathlib import Path
from typing import Any

from scripts.ppe_ide_build_starter import starter_path, write_starter
from scripts.ppe_operator_status import VERDICT_IDE_BUILD, VERDICT_RUN_LOCAL, collect_operator_status
from scripts.ppe_remote_agent import launch_agent_background, notify_agent_done


def _primary_product_slice(status: dict[str, Any]) -> str | None:
    guard = status.get("guard") or {}
    detail = str(guard.get("detail") or status.get("blocker") or "")
    left, right = detail.find("["), detail.find("]")
    if left < 0 or right <= left:
        return None
    ids = [s.strip() for s in detail[left + 1 : right].split(",") if s.strip()]
    return ids[0] if ids else None


def resolve_build_target(repo: Path) -> dict[str, Any]:
    status = collect_operator_status(repo.resolve())
    verdict = str(status.get("verdict") or "")
    plan_path = str(status.get("phase_plan_path") or "").strip()
    product_slice = _primary_product_slice(status)

    if verdict == VERDICT_IDE_BUILD:
        if not plan_path or not product_slice:
            return {"ok": False, "verdict": verdict, "reason": "IDE_BUILD but no product slice resolved"}
        return {
            "ok": True,
            "mode": "ide_build",
            "slice_id": product_slice,
            "plan_path": plan_path,
            "verdict": verdict,
        }
    if verdict == VERDICT_RUN_LOCAL:
        return {"ok": True, "mode": "run_local", "verdict": verdict, "plan_path": plan_path}
    return {"ok": False, "verdict": verdict, "reason": f"build needs IDE_BUILD or RUN_LOCAL (got {verdict})"}


def build_ide_prompt(*, slice_id: str, plan_path: str, starter_rel: str, note: str = "") -> str:
    parts = [
        "You are the PPE desktop BUILD agent. The operator sent **build** from their phone.",
        "",
        f"SLICE_ID: {slice_id}",
        f"PHASE_PLAN: {plan_path}",
        f"Load ONLY `@{starter_rel}`. Implement the product slice within ALLOWED_PATHS.",
        "",
        "When done, in order:",
        "1. python scripts/run_pushable_gate.py",
        "2. git commit on plan buildBranch",
        f"3. mark_ide_product_ready.cmd {slice_id} {plan_path}",
        "4. run_ppe_local.cmd",
        "",
        "Execute autonomously; do not ask for confirmation.",
    ]
    if note.strip():
        parts.extend(["", note.strip()])
    return "\n".join(parts)


def _run_local_background(repo: Path) -> dict[str, Any]:
    log_path = repo / "artifacts/orchestrator/REMOTE_RUN_LOCAL.log"

    def _worker() -> None:
        proc = subprocess.run(["cmd", "/c", "run_ppe_local.cmd"], cwd=repo, capture_output=True, text=True, check=False)
        log_path.write_text((proc.stdout or "") + "\n" + (proc.stderr or ""), encoding="utf-8")
        notify_agent_done(
            title_ok="PPE run_local finished",
            title_fail="PPE run_local failed",
            result={"ok": proc.returncode == 0},
            log_path=log_path,
        )

    threading.Thread(target=_worker, daemon=True).start()
    return {
        "started": True,
        "mode": "run_local",
        "message": "run_ppe_local.cmd started on desktop.",
        "log": str(log_path),
    }


def launch_build(repo: Path, *, note: str = "") -> dict[str, Any]:
    repo = repo.resolve()
    target = resolve_build_target(repo)
    if not target.get("ok"):
        return {"action": "build", "started": False, **target}

    if target.get("mode") == "run_local":
        return {"action": "build", **_run_local_background(repo)}

    slice_id = str(target["slice_id"])
    plan_path = str(target["plan_path"])
    write_starter(repo, slice_id=slice_id, phase_plan=plan_path)
    starter_rel = starter_path(slice_id)
    prompt = build_ide_prompt(slice_id=slice_id, plan_path=plan_path, starter_rel=starter_rel, note=note)

    def _on_complete(result: dict[str, Any]) -> None:
        notify_agent_done(
            title_ok=f"PPE build finished: {slice_id}",
            title_fail=f"PPE build failed: {slice_id}",
            result=result,
            log_path=repo / "artifacts/orchestrator/REMOTE_BUILD_AGENT.log",
        )

    out = launch_agent_background(
        repo,
        prompt=prompt,
        log_name="REMOTE_BUILD_AGENT.log",
        on_complete=_on_complete,
        started_message=f"IDE BUILD started for {slice_id}.",
    )
    return {"action": "build", "mode": "ide_build", "slice_id": slice_id, "plan_path": plan_path, "starter": starter_rel, **out}
