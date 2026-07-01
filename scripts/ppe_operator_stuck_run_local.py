"""Detect and auto-recover stuck RUN_LOCAL closeouts (VM loop + desktop SSH)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_REL = "artifacts/control_plane/STUCK_RUN_LOCAL_RECOVERY.json"
LOG_REL = "artifacts/orchestrator/STUCK_RUN_LOCAL_RECOVERY.log"

DEFAULT_STUCK_SECONDS = 180
RETRY_COOLDOWN_SECONDS = 600
IN_FLIGHT_VM_PHASES = frozenset({"FINISH_IN_FLIGHT", "BUILD_IN_FLIGHT"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def state_path(repo: Path) -> Path:
    return (repo / STATE_REL).resolve()


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
    path = (repo / LOG_REL).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{_utc_now()} {line}\n")


def _run_local_in_flight(repo: Path) -> tuple[bool, str | None]:
    try:
        from scripts.ppe_remote_build_agent import _read_run_local_lock, _run_local_lock_active

        lock = _read_run_local_lock(repo)
        if _run_local_lock_active(repo, lock):
            pid = lock.get("worker_pid") if lock else None
            return True, f"run_local lock active (pid={pid})"
    except ImportError:
        pass
    return False, None


def assess_stuck_run_local(
    repo: Path,
    status: dict[str, Any] | None = None,
    *,
    stuck_seconds: int = DEFAULT_STUCK_SECONDS,
) -> dict[str, Any]:
    """Return whether RUN_LOCAL looks stuck (verdict pending, no worker, age over threshold)."""
    repo = repo.resolve()
    if status is None:
        from scripts.ppe_operator_status import collect_operator_status

        status = collect_operator_status(repo)

    verdict = str(status.get("verdict") or "")
    from scripts.ppe_operator_status import VERDICT_RUN_LOCAL

    if verdict != VERDICT_RUN_LOCAL:
        return {"stuck": False, "reason": f"verdict={verdict or 'unknown'}"}

    in_flight, flight_reason = _run_local_in_flight(repo)
    if in_flight:
        return {"stuck": False, "reason": flight_reason or "run_local in flight"}

    op_session = status.get("operator_session") if isinstance(status.get("operator_session"), dict) else {}
    elapsed = float(op_session.get("elapsed_seconds") or 0)
    if elapsed <= 0:
        session_file = repo / "artifacts/control_plane/OPERATOR_SESSION.json"
        if session_file.is_file():
            try:
                sess = json.loads(session_file.read_text(encoding="utf-8-sig"))
                started = _parse_utc(str(sess.get("started_at") or ""))
                if started is not None:
                    elapsed = max(0.0, (datetime.now(timezone.utc) - started).total_seconds())
            except (OSError, json.JSONDecodeError):
                pass

    vm_trust = status.get("vm_trust") if isinstance(status.get("vm_trust"), dict) else {}
    vm_phase = str(vm_trust.get("vm_phase") or "")
    if vm_phase in IN_FLIGHT_VM_PHASES:
        return {"stuck": False, "reason": f"vm_phase={vm_phase}"}

    stuck = elapsed >= max(60, int(stuck_seconds))
    return {
        "stuck": stuck,
        "elapsed_seconds": int(elapsed),
        "stuck_threshold_seconds": stuck_seconds,
        "verdict": verdict,
        "vm_phase": vm_phase or None,
        "reason": f"RUN_LOCAL pending {int(elapsed // 60)}m with no run_local worker" if stuck else "within threshold",
    }


def _cooldown_active(state: dict[str, Any], *, cooldown_seconds: int) -> bool:
    last = _parse_utc(str(state.get("last_attempt_at") or ""))
    if last is None:
        return False
    age = (datetime.now(timezone.utc) - last).total_seconds()
    return age < max(60, int(cooldown_seconds))


def _is_loop_host(repo: Path) -> bool:
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        return bool(loop_host_start_allowed()[0])
    except Exception:
        return bool(os.environ.get("PPE_LOOP_HOST", "").strip())


def _recover_on_loop_host(repo: Path, *, dry_run: bool) -> dict[str, Any]:
    from scripts.ppe_autobuilder import action_advance, action_run_local

    if dry_run:
        return {"action": "loop_host_recover", "dry_run": True, "would_run": "advance+run_local"}

    run_result = action_run_local(repo)
    if run_result.get("started"):
        return {"action": "loop_host_recover", "recovered": True, "step": "run_local", **run_result}

    advance = action_advance(repo)
    if advance.get("started"):
        return {"action": "loop_host_recover", "recovered": True, "step": "advance", **advance}

    handoff: dict[str, Any] = {"skipped": True}
    try:
        from scripts.ppe_vm_handoff_preflight import prepare_vm_handoff
        from scripts.ppe_post_build_watcher import try_finish_ide_build_handoff

        prep = prepare_vm_handoff(repo)
        handoff = try_finish_ide_build_handoff(repo)
        if handoff.get("started"):
            return {
                "action": "loop_host_recover",
                "recovered": True,
                "step": "finish_handoff",
                "prepare": prep,
                **handoff,
            }
    except ImportError:
        pass

    return {
        "action": "loop_host_recover",
        "recovered": False,
        "run_local": run_result,
        "advance": advance,
        "handoff": handoff,
    }


def _recover_on_desktop(repo: Path, *, dry_run: bool) -> dict[str, Any]:
    from scripts.ppe_operator_vm_ssh import fetch_vm_brief, ssh_vm, vm_advance_command, vm_finish_command

    brief = fetch_vm_brief(repo, use_cache=True)
    parsed = brief.get("parsed") if isinstance(brief.get("parsed"), dict) else {}
    vm_phase = str(parsed.get("phase") or "")
    if vm_phase in IN_FLIGHT_VM_PHASES:
        return {"action": "desktop_ssh_recover", "skipped": True, "reason": f"vm_phase={vm_phase}"}

    if dry_run:
        return {"action": "desktop_ssh_recover", "dry_run": True, "would_ssh": "advance then handoff"}

    advance = ssh_vm(vm_advance_command(), timeout=120)
    if advance.get("ok") and "started" in (advance.get("stdout") or ""):
        append_log(repo, f"desktop ssh advance ok: {(advance.get('stdout') or '')[:200]}")
        return {"action": "desktop_ssh_recover", "recovered": True, "step": "advance", **advance}

    handoff = ssh_vm(vm_finish_command(pull_main=True), timeout=120)
    recovered = bool(handoff.get("ok"))
    append_log(
        repo,
        f"desktop ssh handoff exit={handoff.get('exit_code')} recovered={recovered}",
    )
    return {
        "action": "desktop_ssh_recover",
        "recovered": recovered,
        "step": "handoff",
        **handoff,
    }


def _maybe_notify(repo: Path, status: dict[str, Any], result: dict[str, Any]) -> None:
    try:
        from scripts.ppe_notify_push import bootstrap_operator_notify_env, notify_enabled, send_ntfy

        bootstrap_operator_notify_env(repo)
        if not notify_enabled():
            return
        stuck = assess_stuck_run_local(repo, status)
        if not stuck.get("stuck") and not result.get("recovered"):
            return
        title = "PPE: RUN_LOCAL recovered" if result.get("recovered") else "PPE: RUN_LOCAL stuck — auto-retry"
        body = str(result.get("step") or result.get("reason") or stuck.get("reason") or "see STUCK_RUN_LOCAL_RECOVERY.log")
        send_ntfy(title=title, body=body[:400], tags=["ppe", "run_local", "auto"])
    except Exception:
        pass


def maybe_auto_recover_run_local(
    repo: Path,
    *,
    status: dict[str, Any] | None = None,
    dry_run: bool = False,
    source: str = "status",
    stuck_seconds: int = DEFAULT_STUCK_SECONDS,
    cooldown_seconds: int = RETRY_COOLDOWN_SECONDS,
) -> dict[str, Any] | None:
    """Rate-limited auto-recovery when RUN_LOCAL is stuck. Returns None when not applicable."""
    repo = repo.resolve()
    if os.environ.get("PPE_DISABLE_STUCK_RUN_LOCAL_RECOVERY", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "off",
    ):
        return None

    assessment = assess_stuck_run_local(repo, status, stuck_seconds=stuck_seconds)
    if not assessment.get("stuck"):
        return None

    state = load_state(repo)
    if _cooldown_active(state, cooldown_seconds=cooldown_seconds) and not dry_run:
        return {
            "action": "stuck_run_local",
            "skipped": True,
            "reason": "recovery cooldown",
            "assessment": assessment,
        }

    append_log(repo, f"stuck RUN_LOCAL detected source={source} elapsed={assessment.get('elapsed_seconds')}s")
    if _is_loop_host(repo):
        result = _recover_on_loop_host(repo, dry_run=dry_run)
    else:
        result = _recover_on_desktop(repo, dry_run=dry_run)

    result["assessment"] = assessment
    result["source"] = source

    if not dry_run:
        state["last_attempt_at"] = _utc_now()
        state["last_result"] = {
            "recovered": bool(result.get("recovered")),
            "step": result.get("step"),
            "source": source,
        }
        if result.get("recovered"):
            state["last_recovered_at"] = _utc_now()
        save_state(repo, state)
        _maybe_notify(repo, status or {}, result)

    return result


WATCH_STATE_REL = "artifacts/control_plane/STUCK_RUN_LOCAL_WATCH.json"
DEFAULT_WATCH_POLL_SECONDS = 120


def _watch_state_path(repo: Path) -> Path:
    return (repo / WATCH_STATE_REL).resolve()


def ensure_stuck_watch_daemon(repo: Path, *, poll_seconds: int = DEFAULT_WATCH_POLL_SECONDS) -> dict[str, Any]:
    """Desktop: start detached stuck-RUN_LOCAL watcher if not already running."""
    repo = repo.resolve()
    if _is_loop_host(repo):
        return {"action": "stuck_watch", "skipped": True, "reason": "loop_host"}

    state_path = _watch_state_path(repo)
    state: dict[str, Any] = {}
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            state = {}

    pid = state.get("daemon_pid")
    if pid is not None:
        try:
            from scripts.ppe_remote_agent_spawn import process_alive

            if process_alive(int(pid)):
                return {"action": "stuck_watch", "skipped": True, "reason": "already_running", "daemon_pid": pid}
        except (ImportError, TypeError, ValueError):
            pass

    from scripts.ppe_remote_agent_spawn import spawn_python_worker

    proc = spawn_python_worker(repo, "scripts/ppe_operator_stuck_run_local.py", "--watch-daemon")
    state = {
        "daemon_pid": proc.pid,
        "poll_seconds": poll_seconds,
        "started_at": _utc_now(),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    append_log(repo, f"stuck watch daemon started pid={proc.pid} poll={poll_seconds}s")
    return {"action": "stuck_watch", "started": True, "daemon_pid": proc.pid}


def run_watch_daemon(repo: Path, *, poll_seconds: int = DEFAULT_WATCH_POLL_SECONDS) -> int:
    """Poll operator status and auto-recover stuck RUN_LOCAL (desktop background)."""
    import time

    repo = repo.resolve()
    append_log(repo, f"watch daemon running poll={poll_seconds}s pid={os.getpid()}")
    while True:
        try:
            from scripts.ppe_operator_status import prepare_operator_status

            status = prepare_operator_status(repo)
            maybe_auto_recover_run_local(repo, status=status, source="watch_daemon")
        except Exception as exc:
            append_log(repo, f"watch daemon error: {exc}")
        time.sleep(max(60, int(poll_seconds)))


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Assess / recover stuck RUN_LOCAL closeouts")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--assess", action="store_true", help="Print assessment only")
    ap.add_argument("--recover", action="store_true", help="Run recovery if stuck")
    ap.add_argument("--watch-daemon", action="store_true", help="Run background stuck watch loop")
    ap.add_argument("--ensure-watch", action="store_true", help="Start detached watch daemon on desktop")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()

    if args.watch_daemon:
        return run_watch_daemon(repo)

    if args.ensure_watch:
        out = ensure_stuck_watch_daemon(repo)
        if args.json:
            print(json.dumps(out, indent=2))
        return 0

    from scripts.ppe_operator_status import prepare_operator_status

    status = prepare_operator_status(repo)
    if args.recover:
        out = maybe_auto_recover_run_local(repo, status=status, dry_run=args.dry_run, source="cli")
    else:
        out = assess_stuck_run_local(repo, status)

    if args.json:
        print(json.dumps(out, indent=2))
    elif out:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
