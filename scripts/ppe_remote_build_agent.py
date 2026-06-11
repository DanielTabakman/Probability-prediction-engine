"""Phone-triggered IDE BUILD for the active queued product slice."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_ide_build_starter import starter_path, write_starter
from scripts.ppe_operator_status import VERDICT_IDE_BUILD, VERDICT_RUN_LOCAL, collect_operator_status
from scripts.ppe_remote_agent import launch_agent_background
from scripts.ppe_remote_agent_spawn import process_alive, spawn_python_worker

BUILD_LOCK_REL = "artifacts/orchestrator/REMOTE_BUILD_LOCK.json"
BUILD_LOG_REL = "artifacts/orchestrator/REMOTE_BUILD_AGENT.log"
BUILD_LOCK_MAX_AGE_SEC = 7200


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_lock_stale_sec() -> int:
    try:
        return max(30, int(os.environ.get("PPE_BUILD_LOCK_STALE_SEC", "90")))
    except ValueError:
        return 90


def build_lock_path(repo: Path) -> Path:
    return repo.resolve() / BUILD_LOCK_REL


def _read_build_lock_raw(repo: Path) -> dict[str, Any] | None:
    path = build_lock_path(repo)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _lock_age_sec(lock: dict[str, Any]) -> float | None:
    started_raw = str(lock.get("started_at") or "").strip()
    if not started_raw:
        return None
    try:
        started = datetime.fromisoformat(started_raw.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - started).total_seconds()
    except ValueError:
        return None


def _log_shows_agent_started(repo: Path) -> bool:
    log_path = repo.resolve() / BUILD_LOG_REL
    if not log_path.is_file():
        return False
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "--- agent cli start" in text or "--- cursor-sdk start" in text


def is_build_lock_stale(repo: Path, lock: dict[str, Any]) -> bool:
    """True when lock exists but no live worker is making progress."""
    worker_pid = lock.get("worker_pid")
    if worker_pid is not None:
        try:
            if process_alive(int(worker_pid)):
                return False
        except (TypeError, ValueError):
            pass
        return True

    age = _lock_age_sec(lock)
    if age is None:
        return False
    if age > BUILD_LOCK_MAX_AGE_SEC:
        return True
    if age >= _build_lock_stale_sec() and not _log_shows_agent_started(repo):
        return True
    return False


def read_build_lock(repo: Path) -> dict[str, Any] | None:
    data = _read_build_lock_raw(repo)
    if not data:
        return None

    age = _lock_age_sec(data)
    if age is not None and age > BUILD_LOCK_MAX_AGE_SEC:
        clear_build_lock(repo)
        return None

    if is_build_lock_stale(repo, data):
        clear_build_lock(repo)
        return None

    return data


def write_build_lock(
    repo: Path,
    *,
    slice_id: str,
    plan_path: str,
    source: str,
    worker_pid: int | None = None,
) -> None:
    path = build_lock_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "slice_id": slice_id,
        "plan_path": plan_path,
        "source": source,
        "started_at": _utc_now(),
    }
    if worker_pid is not None:
        payload["worker_pid"] = worker_pid
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_build_lock_worker_pid(repo: Path, worker_pid: int) -> None:
    data = _read_build_lock_raw(repo)
    if not data:
        return
    data["worker_pid"] = worker_pid
    build_lock_path(repo).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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


def _run_local_detached(repo: Path) -> dict[str, Any]:
    log_path = repo / "artifacts/orchestrator/REMOTE_RUN_LOCAL.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(f"run_local detached start {_utc_now()}\n", encoding="utf-8")

    job_dir = repo / "artifacts" / "orchestrator"
    job_path = job_dir / f"REMOTE_RUN_LOCAL_JOB_{os.getpid()}.json"
    job_path.write_text(
        json.dumps({"repo_root": str(repo.resolve()), "log_path": str(log_path)}, indent=2) + "\n",
        encoding="utf-8",
    )

    try:
        proc = spawn_python_worker(
            repo,
            "scripts/ppe_remote_run_local_worker.py",
            "--job",
            str(job_path),
            "--delete-job",
        )
    except OSError as exc:
        job_path.unlink(missing_ok=True)
        return {"started": False, "reason": f"failed to spawn run_local worker: {exc}"}

    return {
        "started": True,
        "mode": "run_local",
        "message": "run_ppe_local.cmd started on desktop.",
        "log": str(log_path),
        "worker_pid": proc.pid,
    }


def launch_build(repo: Path, *, note: str = "", source: str = "phone") -> dict[str, Any]:
    repo = repo.resolve()
    target = resolve_build_target(repo)
    if not target.get("ok"):
        return {"action": "build", "started": False, **target}

    if target.get("mode") == "run_local":
        return {"action": "build", **_run_local_detached(repo)}

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

    out = launch_agent_background(
        repo,
        prompt=prompt,
        log_name="REMOTE_BUILD_AGENT.log",
        started_message=f"IDE BUILD started for {slice_id}.",
        clear_build_lock=True,
        notify_ok_title=f"PPE build finished: {slice_id}",
        notify_fail_title=f"PPE build failed: {slice_id}",
        handoff={"slice_id": slice_id, "plan_path": plan_path, "source": source},
    )
    if not out.get("started"):
        clear_build_lock(repo)
    else:
        worker_pid = out.get("worker_pid")
        if worker_pid is not None:
            update_build_lock_worker_pid(repo, int(worker_pid))
    return {
        "action": "build",
        "mode": "ide_build",
        "slice_id": slice_id,
        "plan_path": plan_path,
        "starter": starter_rel,
        "source": source,
        **out,
    }
