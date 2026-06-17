"""Poll .cursor/IDE_BUILD_TRIGGER.json and dispatch local agent CLI on pending handoffs."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_ide_build_automation_trigger import load_trigger, write_trigger_dispatched, write_trigger_idle
from scripts.ppe_remote_agent import agent_available, launch_agent_background
from scripts.ppe_remote_build_agent import (
    clear_build_lock,
    read_build_lock,
    update_build_lock_worker_pid,
    write_build_lock,
)

STATE_REL = "artifacts/orchestrator/IDE_BUILD_LOCAL_WATCHER_STATE.json"
LOG_REL = "artifacts/orchestrator/IDE_BUILD_LOCAL_WATCHER.log"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_path(repo: Path) -> Path:
    return (repo / STATE_REL).resolve()


def log_path(repo: Path) -> Path:
    return (repo / LOG_REL).resolve()


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


def append_log(repo: Path, line: str) -> None:
    path = log_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{_utc_now()} {line}\n")


def local_trigger_watcher_enabled(repo: Path) -> bool:
    env = os.environ.get("PPE_IDE_LOCAL_TRIGGER_WATCHER", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        handoff = cfg.get("ideHandoff")
        if isinstance(handoff, dict):
            if handoff.get("localTriggerWatcher") is False:
                return False
            if handoff.get("localTriggerWatcher") is True:
                return True
            if handoff.get("enabled") is False:
                return False
    except ImportError:
        pass
    return True


def _poll_interval_sec() -> int:
    raw = os.environ.get("PPE_IDE_LOCAL_WATCHER_INTERVAL_SEC", "5").strip()
    try:
        return max(2, int(raw))
    except ValueError:
        return 5


def trigger_dispatch_key(trigger: dict[str, Any]) -> str:
    """Dedup key — slice only so new handoffAt timestamps do not re-dispatch."""
    return str(trigger.get("sliceId") or "").strip()


def _dispatch_fail_cooldown_sec() -> int:
    raw = os.environ.get("PPE_IDE_LOCAL_WATCHER_FAIL_COOLDOWN_SEC", "300").strip()
    try:
        return max(30, int(raw))
    except ValueError:
        return 300


def _parse_utc(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def watcher_should_skip_cli(repo: Path) -> tuple[bool, str]:
    """When True, local watcher must not spawn headless agent CLI."""
    try:
        from scripts.ppe_ide_handoff import should_attempt_headless_cli

        if not should_attempt_headless_cli(repo, mode="build"):
            from scripts.ppe_ide_handoff import cli_usage_exhausted, prefer_ide_over_cli

            if prefer_ide_over_cli(repo):
                return True, "prefer_ide_over_cli"
            if cli_usage_exhausted(repo):
                return True, "cli_usage_exhausted"
            return True, "headless_cli_disabled"
    except ImportError:
        pass
    return False, ""


def _slice_dispatch_blocked(state: dict[str, Any], slice_id: str) -> str | None:
    """Return skip reason when this slice was already dispatched or in fail cooldown."""
    last = state.get("last_dispatch") if isinstance(state.get("last_dispatch"), dict) else {}
    if str(last.get("slice_id") or "") != slice_id:
        return None
    if last.get("started"):
        return f"already dispatched for slice {slice_id}"
    updated = _parse_utc(str(state.get("updatedAt") or ""))
    if updated is not None:
        age = (datetime.now(timezone.utc) - updated).total_seconds()
        if age < _dispatch_fail_cooldown_sec():
            return f"dispatch fail cooldown ({int(_dispatch_fail_cooldown_sec() - age)}s left)"
    return None


def build_trigger_watcher_prompt(*, slice_id: str, plan_path: str, starter_rel: str) -> str:
    return "\n".join(
        [
            "You are the PPE desktop BUILD agent. The local IDE_BUILD trigger watcher dispatched this run.",
            "",
            f"SLICE_ID: {slice_id}",
            f"PHASE_PLAN: {plan_path}",
            f"Load ONLY `@{starter_rel}`. Implement the product slice within ALLOWED_PATHS / TOUCH_SET.",
            "",
            "When done, in order:",
            "1. python scripts/run_pushable_gate.py",
            "2. git commit on plan buildBranch (if not already committed)",
            f"3. ppe_ide_build_closeout.cmd {slice_id} {plan_path}",
            "",
            "Execute autonomously. Do not ask for confirmation. Do not paste orchestrator logs.",
            "If run_ppe_local.cmd fails, fix and retry once; then stop with a short failure summary.",
        ]
    )


def try_dispatch_from_trigger(repo: Path, trigger: dict[str, Any]) -> dict[str, Any]:
    repo = repo.resolve()
    status = str(trigger.get("status") or "").strip().lower()
    if status != "pending":
        return {"action": "local_trigger_watcher", "skipped": True, "reason": f"status={status or 'missing'}"}

    slice_id = str(trigger.get("sliceId") or "").strip()
    plan_path = str(trigger.get("planPath") or "").strip()
    starter_rel = str(trigger.get("starter") or "").strip()
    handoff_at = str(trigger.get("handoffAt") or "").strip()
    if not slice_id or not plan_path or not starter_rel:
        return {
            "action": "local_trigger_watcher",
            "skipped": True,
            "reason": "incomplete trigger (need sliceId, planPath, starter)",
        }

    try:
        from scripts.ppe_phase_plan_window import completed_slice_ids
        from scripts.ppe_manifest import load_phase_plan
        from scripts.ppe_ide_product_ready import _branch_has_commits

        if slice_id in completed_slice_ids(repo, plan_path):
            write_trigger_idle(repo, completed_slice=slice_id)
            clear_build_lock(repo)
            return {
                "action": "local_trigger_watcher",
                "skipped": True,
                "reason": f"slice already completed: {slice_id}",
                "slice_id": slice_id,
            }
        plan = load_phase_plan(repo, plan_path)
        for sl in plan.get("slices") or []:
            if not isinstance(sl, dict) or str(sl.get("sliceId") or "").strip() != slice_id:
                continue
            branch = str(sl.get("buildBranch") or "").strip()
            baseline = str(plan.get("baselineBranch") or "main").strip() or "main"
            if branch and _branch_has_commits(repo, build_branch=branch, baseline=baseline):
                write_trigger_idle(repo, completed_slice=slice_id)
                clear_build_lock(repo)
                return {
                    "action": "local_trigger_watcher",
                    "skipped": True,
                    "reason": f"build branch already has commits: {branch}",
                    "slice_id": slice_id,
                }
            break
    except (ImportError, FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        pass

    dispatch_key = trigger_dispatch_key(trigger)
    state = load_state(repo)
    last_dispatch = state.get("last_dispatch") if isinstance(state.get("last_dispatch"), dict) else {}
    blocked = _slice_dispatch_blocked(state, slice_id)
    if blocked:
        return {
            "action": "local_trigger_watcher",
            "skipped": True,
            "reason": blocked,
            "dispatch_key": dispatch_key,
        }
    if state.get("last_dispatch_key") == dispatch_key and last_dispatch.get("started"):
        return {
            "action": "local_trigger_watcher",
            "skipped": True,
            "reason": "already dispatched",
            "dispatch_key": dispatch_key,
        }

    lock = read_build_lock(repo)
    if lock and str(lock.get("slice_id") or "") == slice_id:
        return {
            "action": "local_trigger_watcher",
            "skipped": True,
            "reason": f"build already in flight for {slice_id}",
            "dispatch_key": dispatch_key,
        }

    skip_cli, skip_reason = watcher_should_skip_cli(repo)
    if skip_cli:
        if state.get("last_cli_skip_slice") != slice_id:
            append_log(repo, f"skip CLI dispatch for {slice_id}: {skip_reason}")
            save_state(
                repo,
                {
                    **state,
                    "last_cli_skip_slice": slice_id,
                    "last_cli_skip_reason": skip_reason,
                },
            )
        return {
            "action": "local_trigger_watcher",
            "skipped": True,
            "reason": skip_reason,
            "slice_id": slice_id,
            "dispatch_key": dispatch_key,
        }

    if not agent_available():
        if state.get("last_agent_missing_key") != dispatch_key:
            append_log(repo, f"agent unavailable for {dispatch_key} — run setup_cursor_agent.cmd")
            save_state(
                repo,
                {
                    **state,
                    "last_agent_missing_key": dispatch_key,
                    "last_skip": {"reason": "agent unavailable", "dispatch_key": dispatch_key},
                },
            )
            _maybe_notify_agent_missing(repo, slice_id=slice_id)
        return {
            "action": "local_trigger_watcher",
            "skipped": True,
            "reason": "agent CLI unavailable (setup_cursor_agent.cmd + agent login)",
            "dispatch_key": dispatch_key,
        }

    prompt = build_trigger_watcher_prompt(slice_id=slice_id, plan_path=plan_path, starter_rel=starter_rel)
    write_build_lock(repo, slice_id=slice_id, plan_path=plan_path, source="local-watcher")

    out = launch_agent_background(
        repo,
        prompt=prompt,
        log_name="REMOTE_BUILD_AGENT.log",
        started_message=f"Local trigger watcher started IDE BUILD for {slice_id}.",
        clear_build_lock=True,
        notify_ok_title=f"PPE build finished: {slice_id}",
        notify_fail_title=f"PPE build failed: {slice_id}",
        handoff={"slice_id": slice_id, "plan_path": plan_path, "source": "local-watcher"},
    )
    if not out.get("started"):
        clear_build_lock(repo)
        append_log(repo, f"dispatch failed {dispatch_key}: {out.get('reason')}")
        save_state(
            repo,
            {
                **state,
                "last_dispatch_key": dispatch_key,
                "last_dispatch": {
                    "started": False,
                    "slice_id": slice_id,
                    **out,
                },
            },
        )
        return {"action": "local_trigger_watcher", "slice_id": slice_id, "dispatch_key": dispatch_key, **out}

    worker_pid = out.get("worker_pid")
    write_trigger_dispatched(
        repo,
        slice_id=slice_id,
        plan_path=plan_path,
        starter_rel=starter_rel,
        handoff_at=handoff_at or _utc_now(),
        source="local-watcher",
        worker_pid=int(worker_pid) if worker_pid is not None else None,
    )
    if worker_pid is not None:
        update_build_lock_worker_pid(repo, int(worker_pid))

    append_log(repo, f"dispatched {dispatch_key} worker_pid={worker_pid}")
    save_state(
        repo,
        {
            **state,
            "last_dispatch_key": dispatch_key,
            "last_dispatch": {
                "started": True,
                "slice_id": slice_id,
                "worker_pid": worker_pid,
                "log": out.get("log"),
            },
            "last_agent_missing_key": None,
        },
    )
    _maybe_notify_started(repo, slice_id=slice_id)
    return {
        "action": "local_trigger_watcher",
        "started": True,
        "slice_id": slice_id,
        "dispatch_key": dispatch_key,
        **out,
    }


def _maybe_notify_agent_missing(repo: Path, *, slice_id: str) -> None:
    try:
        from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy
    except ImportError:
        return
    if not notify_enabled() or not ntfy_configured():
        return
    send_ntfy(
        f"PPE watcher: agent missing ({slice_id})",
        "Run setup_cursor_agent.cmd and agent login on the desktop.",
        tags=["ppe", "watch", "build"],
        priority="high",
    )


def _maybe_notify_started(repo: Path, *, slice_id: str) -> None:
    try:
        from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy
    except ImportError:
        return
    if not notify_enabled() or not ntfy_configured():
        return
    send_ntfy(
        f"PPE auto-build started: {slice_id}",
        "Local trigger watcher dispatched agent CLI on desktop.",
        tags=["ppe", "watch", "build"],
        priority="default",
    )


def watch_once(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    if not local_trigger_watcher_enabled(repo):
        return {"action": "local_trigger_watcher", "skipped": True, "reason": "disabled"}

    trigger = load_trigger(repo)
    if not trigger:
        return {"action": "local_trigger_watcher", "skipped": True, "reason": "no trigger file"}

    return try_dispatch_from_trigger(repo, trigger)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Local IDE BUILD trigger watcher (.cursor/IDE_BUILD_TRIGGER.json)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--once", action="store_true", help="Single poll")
    ap.add_argument("--interval", type=int, default=0, help="Poll interval seconds (default env or 5)")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    interval = args.interval if args.interval > 0 else _poll_interval_sec()

    if args.once:
        result = watch_once(repo)
        print(json.dumps(result, indent=2))
        return 0 if result.get("started") or result.get("skipped") else 1

    if not local_trigger_watcher_enabled(repo):
        print(
            "ppe_ide_build_local_watcher: disabled "
            "(set ideHandoff.localTriggerWatcher or PPE_IDE_LOCAL_TRIGGER_WATCHER=1)"
        )
        return 0

    print(f"ppe_ide_build_local_watcher: polling every {interval}s — Ctrl+C to stop")
    while True:
        result = watch_once(repo)
        if result.get("started"):
            brief = f"started slice={result.get('slice_id')}"
        elif result.get("skipped"):
            brief = f"skip reason={result.get('reason')}"
        else:
            brief = f"result={result.get('reason') or 'unknown'}"
        print(f"[{_utc_now()}] {brief}", flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
