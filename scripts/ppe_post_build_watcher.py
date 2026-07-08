"""Detect finished IDE product commits and auto mark + run_ppe_local."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_ide_product_ready import (
    _branch_has_commits,
    _resolve_slice_and_branch,
    completed_product_slice_ids,
    next_pending_product_slice,
)
from scripts.ppe_remote_agent_spawn import process_alive, spawn_python_worker

STATE_REL = "artifacts/orchestrator/POST_BUILD_WATCHER_STATE.json"
LOG_REL = "artifacts/orchestrator/POST_BUILD_FINISH.log"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_path(repo: Path) -> Path:
    return (repo / STATE_REL).resolve()


def load_state(repo: Path) -> dict[str, Any]:
    p = state_path(repo)
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(repo: Path, data: dict[str, Any]) -> None:
    p = state_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = _utc_now()
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def post_build_watcher_enabled(repo: Path) -> bool:
    env = os.environ.get("PPE_POST_BUILD_WATCHER", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        handoff = cfg.get("ideHandoff")
        if isinstance(handoff, dict) and handoff.get("postBuildWatcher") is False:
            return False
        if cfg.get("postBuildWatcher") is False:
            return False
    except ImportError:
        pass
    return True


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _branch_head(repo: Path, branch: str) -> str:
    proc = _git(repo, "rev-parse", branch)
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def _resolve_watch_target(repo: Path) -> dict[str, Any] | None:
    repo = repo.resolve()
    try:
        from scripts.ppe_manifest import load_manifest

        manifest = load_manifest(repo)
    except FileNotFoundError:
        return None

    plan_path = str(manifest.get("phasePlanPath") or "").strip()
    if not plan_path:
        return None

    slice_id = next_pending_product_slice(repo, plan_path=plan_path)
    if not slice_id:
        return None

    if slice_id in completed_product_slice_ids(repo, plan_path=plan_path):
        return None

    try:
        _, build_branch, baseline = _resolve_slice_and_branch(
            repo, slice_id=slice_id, plan_path=plan_path, build_branch=None
        )
    except ValueError:
        return None

    if not _branch_has_commits(repo, build_branch=build_branch, baseline=baseline):
        return None

    head = _branch_head(repo, build_branch)
    if not head:
        return None

    return {
        "slice_id": slice_id,
        "plan_path": plan_path,
        "build_branch": build_branch,
        "baseline": baseline,
        "commit_sha": head,
    }


def _finish_worker_already_running(repo: Path, state: dict[str, Any]) -> bool:
    pid = state.get("worker_pid")
    if pid is None:
        return False
    try:
        return process_alive(int(pid))
    except (TypeError, ValueError):
        return False


def _spawn_finish_worker(repo: Path, *, target: dict[str, Any]) -> dict[str, Any]:
    repo = repo.resolve()
    log_path = repo / LOG_REL
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(f"post_build_finish start {_utc_now()}\n", encoding="utf-8")

    job_dir = repo / "artifacts" / "orchestrator"
    job_path = job_dir / f"POST_BUILD_FINISH_JOB_{os.getpid()}.json"
    job_path.write_text(
        json.dumps(
            {
                "repo_root": str(repo),
                "log_path": str(log_path),
                "slice_id": target["slice_id"],
                "plan_path": target["plan_path"],
                "build_branch": target["build_branch"],
                "commit_sha": target["commit_sha"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        proc = spawn_python_worker(
            repo,
            "scripts/ppe_post_build_finish_worker.py",
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
        "slice_id": target["slice_id"],
        "commit_sha": target["commit_sha"],
    }


def try_finish_pending_ide_build(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """If next pending slice has build-branch commits, mark ready and run_ppe_local."""
    repo = repo.resolve()
    if not post_build_watcher_enabled(repo):
        return {"action": "post_build_watcher", "skipped": True, "reason": "disabled"}

    try:
        from scripts.ppe_remote_build_agent import read_build_lock

        lock = read_build_lock(repo)
        if lock:
            return {
                "action": "post_build_watcher",
                "skipped": True,
                "reason": f"build lock active for {lock.get('slice_id')}",
            }
    except ImportError:
        pass

    target = _resolve_watch_target(repo)
    if not target:
        return {"action": "post_build_watcher", "skipped": True, "reason": "no finishable slice"}

    state = load_state(repo)
    if _finish_worker_already_running(repo, state):
        return {
            "action": "post_build_watcher",
            "skipped": True,
            "reason": "finish worker already running",
            "worker_pid": state.get("worker_pid"),
        }

    slice_id = str(target["slice_id"])
    sha = str(target["commit_sha"])
    last_key = f"{target['plan_path']}::{slice_id}"
    last_finished = (state.get("last_finished") or {}).get(last_key)
    if isinstance(last_finished, dict) and str(last_finished.get("commit_sha") or "") == sha:
        return {
            "action": "post_build_watcher",
            "skipped": True,
            "reason": "already finished for this commit",
            "slice_id": slice_id,
            "commit_sha": sha,
        }

    if dry_run:
        return {
            "action": "post_build_watcher",
            "dry_run": True,
            "would_finish": target,
        }

    spawned = _spawn_finish_worker(repo, target=target)
    if not spawned.get("started"):
        return {"action": "post_build_watcher", "started": False, **spawned}

    last_finished_map = dict(state.get("last_finished") or {})
    last_finished_map[last_key] = {
        "commit_sha": sha,
        "started_at": _utc_now(),
        "worker_pid": spawned.get("worker_pid"),
    }
    save_state(
        repo,
        {
            **state,
            "last_finished": last_finished_map,
            "worker_pid": spawned.get("worker_pid"),
            "last_slice_id": slice_id,
        },
    )
    return {"action": "post_build_watcher", **spawned}


def try_closeout_only_run_local(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """When product is already on main (CLOSEOUT_ONLY), spawn run_ppe_local if idle."""
    repo = repo.resolve()
    try:
        from scripts.ppe_chapter_mode import MODE_CLOSEOUT_ONLY
        from scripts.ppe_operator_status import VERDICT_RUN_LOCAL, collect_operator_status
        from scripts.ppe_remote_build_agent import (
            _read_run_local_lock,
            _run_local_lock_active,
            spawn_run_local_detached,
        )
    except ImportError as exc:
        return {"action": "closeout_finish", "skipped": True, "reason": str(exc)}

    status = collect_operator_status(repo)
    verdict = str(status.get("verdict") or "")
    chapter_mode = status.get("chapter_mode") if isinstance(status.get("chapter_mode"), dict) else {}
    mode = str(chapter_mode.get("mode") or "")

    closeout_registry = bool(chapter_mode.get("closeout_only_registry")) and bool(
        chapter_mode.get("product_on_main")
    )
    if mode != MODE_CLOSEOUT_ONLY and not closeout_registry:
        return {"action": "closeout_finish", "skipped": True, "reason": "not closeout-only"}
    if verdict not in (VERDICT_RUN_LOCAL, "RUN_AUTO"):
        return {
            "action": "closeout_finish",
            "skipped": True,
            "reason": f"verdict={verdict or 'unknown'}",
        }

    lock = _read_run_local_lock(repo)
    if _run_local_lock_active(repo, lock):
        return {
            "action": "closeout_finish",
            "skipped": True,
            "reason": "run_local already in flight",
            "worker_pid": lock.get("worker_pid") if lock else None,
        }

    if dry_run:
        return {"action": "closeout_finish", "dry_run": True, "would_start": True}

    spawned = spawn_run_local_detached(repo)
    return {"action": "closeout_finish", **spawned}


def try_finish_ide_build_handoff(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Post-build mark+finish, else explicit CLOSEOUT_ONLY run_ppe_local trigger."""
    post = try_finish_pending_ide_build(repo, dry_run=dry_run)
    if post.get("started"):
        return post
    if dry_run and post.get("would_finish"):
        return post

    closeout = try_closeout_only_run_local(repo, dry_run=dry_run)
    if closeout.get("started"):
        return closeout
    if dry_run and closeout.get("would_start"):
        return closeout

    if post.get("skipped") and closeout.get("skipped"):
        return {
            "action": "finish_ide_build_handoff",
            "skipped": True,
            "post_build_reason": post.get("reason"),
            "closeout_reason": closeout.get("reason"),
        }
    return closeout if not closeout.get("skipped") else post


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Post-build watcher for IDE product slices")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--finish-handoff", action="store_true", help="Post-build + CLOSEOUT_ONLY run_local")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.finish_handoff:
        result = try_finish_ide_build_handoff(repo, dry_run=args.dry_run)
    else:
        result = try_finish_pending_ide_build(repo, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2))
    elif not result.get("skipped") and result.get("started"):
        action = str(result.get("action") or "post_build_watcher")
        label = result.get("slice_id") or "closeout"
        print(f"ppe_post_build_watcher: {action} started for {label} (pid={result.get('worker_pid')})")
    elif result.get("dry_run"):
        if result.get("would_start"):
            print("ppe_post_build_watcher: would start closeout run_local")
        else:
            print(f"ppe_post_build_watcher: would finish {result.get('would_finish')}")
    elif args.finish_handoff and result.get("skipped"):
        print(
            "ppe_post_build_watcher: finish handoff skipped — "
            f"post_build={result.get('post_build_reason') or result.get('reason')}; "
            f"closeout={result.get('closeout_reason') or result.get('reason')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
