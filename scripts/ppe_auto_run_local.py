"""Auto-start run_ppe_local when IDE product marker is ready (RUN_LOCAL / IDE_MARKER_OK)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_operator_status import VERDICT_RUN_LOCAL, collect_operator_status
from scripts.ppe_remote_agent_spawn import process_alive, spawn_python_worker

STATE_REL = "artifacts/orchestrator/AUTO_RUN_LOCAL_STATE.json"
LOG_REL = "artifacts/orchestrator/REMOTE_RUN_LOCAL.log"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_path(repo: Path) -> Path:
    return repo.resolve() / STATE_REL


def load_state(repo: Path) -> dict[str, Any]:
    path = state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(repo: Path, data: dict[str, Any]) -> None:
    path = state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = _utc_now()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def auto_run_local_enabled(repo: Path) -> bool:
    env = os.environ.get("PPE_AUTO_RUN_LOCAL", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        if cfg.get("autoRunLocal") is False:
            return False
        return cfg.get("autoRunLocal", True) is not False
    except ImportError:
        return True


def _active_run_exists(repo: Path) -> bool:
    active = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    return active.is_file()


def run_local_worker_running(repo: Path) -> bool:
    state = load_state(repo)
    pid = state.get("worker_pid")
    if pid is not None:
        try:
            if process_alive(int(pid)):
                return True
        except (TypeError, ValueError):
            pass
    try:
        from scripts.ppe_remote_build_agent import read_build_lock

        lock = read_build_lock(repo)
        if lock:
            return True
    except ImportError:
        pass
    return False


def _spawn_run_local_worker(repo: Path, *, plan_path: str) -> dict[str, Any]:
    repo = repo.resolve()
    log_path = repo / LOG_REL
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(f"auto_run_local start {_utc_now()} plan={plan_path}\n", encoding="utf-8")

    job_dir = repo / "artifacts" / "orchestrator"
    job_path = job_dir / f"AUTO_RUN_LOCAL_JOB_{os.getpid()}.json"
    job_path.write_text(
        json.dumps(
            {
                "repo_root": str(repo),
                "log_path": str(log_path),
                "plan_path": plan_path,
                "source": "auto-run-local",
            },
            indent=2,
        )
        + "\n",
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
        return {"started": False, "reason": str(exc)}

    return {
        "started": True,
        "worker_pid": proc.pid,
        "log": str(log_path),
        "plan_path": plan_path,
    }


def try_auto_run_local(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Spawn run_ppe_local when verdict is RUN_LOCAL and no worker is active."""
    repo = repo.resolve()
    if not auto_run_local_enabled(repo):
        return {"action": "auto_run_local", "skipped": True, "reason": "disabled"}

    try:
        from scripts.ppe_operator_maintenance import is_maintenance_active

        if is_maintenance_active(repo):
            return {"action": "auto_run_local", "skipped": True, "reason": "maintenance"}
    except ImportError:
        pass

    status = collect_operator_status(repo)
    verdict = str(status.get("verdict") or "")
    if verdict != VERDICT_RUN_LOCAL:
        return {"action": "auto_run_local", "skipped": True, "reason": f"verdict={verdict}"}

    guard = status.get("guard") or {}
    if str(guard.get("reason") or "") != "IDE_MARKER_OK":
        return {
            "action": "auto_run_local",
            "skipped": True,
            "reason": f"guard={guard.get('reason') or 'unknown'}",
        }

    plan_path = str(status.get("phase_plan_path") or "").strip()
    if not plan_path:
        return {"action": "auto_run_local", "skipped": True, "reason": "no plan_path"}

    if _active_run_exists(repo):
        return {"action": "auto_run_local", "skipped": True, "reason": "active_run present"}

    if run_local_worker_running(repo):
        return {"action": "auto_run_local", "skipped": True, "reason": "worker already running"}

    if dry_run:
        return {"action": "auto_run_local", "dry_run": True, "would_start": plan_path}

    spawned = _spawn_run_local_worker(repo, plan_path=plan_path)
    if spawned.get("started"):
        save_state(
            repo,
            {
                **load_state(repo),
                "worker_pid": spawned.get("worker_pid"),
                "plan_path": plan_path,
                "started_at": _utc_now(),
            },
        )
        try:
            from scripts.ppe_operator_idle_alert import record_progress

            record_progress(repo, reason="auto_run_local_started")
        except ImportError:
            pass
    return {"action": "auto_run_local", **spawned}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Auto-start run_ppe_local for RUN_LOCAL / IDE_MARKER_OK")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    result = try_auto_run_local(repo, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get("started"):
        print(
            f"ppe_auto_run_local: started run_ppe_local "
            f"(pid={result.get('worker_pid')}) plan={result.get('plan_path')}"
        )
    elif not result.get("skipped") and result.get("reason"):
        print(f"ppe_auto_run_local: {result.get('reason')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
