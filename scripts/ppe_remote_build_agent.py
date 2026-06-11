"""Phone-triggered IDE BUILD for the active queued product slice."""

from __future__ import annotations

import json
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_ide_build_starter import starter_path, write_starter
from scripts.ppe_operator_status import VERDICT_IDE_BUILD, VERDICT_RUN_LOCAL, collect_operator_status
from scripts.ppe_remote_agent import launch_agent_background, notify_agent_done

BUILD_LOCK_REL = "artifacts/orchestrator/REMOTE_BUILD_LOCK.json"
BUILD_LOCK_MAX_AGE_SEC = 7200


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_lock_path(repo: Path) -> Path:
    return repo.resolve() / BUILD_LOCK_REL


def read_build_lock(repo: Path) -> dict[str, Any] | None:
    path = build_lock_path(repo)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    started_raw = str(data.get("started_at") or "").strip()
    if started_raw:
        try:
            started = datetime.fromisoformat(started_raw.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - started).total_seconds()
            if age > BUILD_LOCK_MAX_AGE_SEC:
                return None
        except ValueError:
            pass
    return data


def write_build_lock(repo: Path, *, slice_id: str, plan_path: str, source: str) -> None:
    path = build_lock_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "slice_id": slice_id,
                "plan_path": plan_path,
                "source": source,
                "started_at": _utc_now(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def clear_build_lock(repo: Path) -> None:
    path = build_lock_path(repo)
    if path.is_file():
        path.unlink(missing_ok=True)


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


def launch_build(repo: Path, *, note: str = "", source: str = "phone") -> dict[str, Any]:
    repo = repo.resolve()
    target = resolve_build_target(repo)
    if not target.get("ok"):
        return {"action": "build", "started": False, **target}

    if target.get("mode") == "run_local":
        return {"action": "build", **_run_local_background(repo)}

    slice_id = str(target["slice_id"])
    plan_path = str(target["plan_path"])
    lock = read_build_lock(repo)
    if lock and str(lock.get("slice_id") or "") == slice_id:
        return {
            "action": "build",
            "started": False,
            "reason": f"build already in flight for {slice_id}",
            "lock": lock,
        }

    write_starter(repo, slice_id=slice_id, phase_plan=plan_path)
    starter_rel = starter_path(slice_id)
    prompt = build_ide_prompt(slice_id=slice_id, plan_path=plan_path, starter_rel=starter_rel, note=note)
    write_build_lock(repo, slice_id=slice_id, plan_path=plan_path, source=source)

    def _on_complete(result: dict[str, Any]) -> None:
        clear_build_lock(repo)
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
    if not out.get("started"):
        clear_build_lock(repo)
    return {
        "action": "build",
        "mode": "ide_build",
        "slice_id": slice_id,
        "plan_path": plan_path,
        "starter": starter_rel,
        "source": source,
        **out,
    }
