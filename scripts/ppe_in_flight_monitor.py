"""Adaptive VM in-flight monitor — refresh mirror, report progress, escalate when stuck.

Desktop/operator threads use this instead of passive wait on BUILD_IN_FLIGHT /
FINISH_IN_FLIGHT. Prefers git mirror; one bounded SSH only when mirror stale or
stuck >= 45m.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.ppe_operator_vm_mirror_refresh import (  # noqa: E402
    assess_mirror_health,
    mirror_age_seconds,
    refresh_vm_mirror_from_git,
)
from scripts.ppe_operator_vm_ssh import (  # noqa: E402
    fetch_vm_brief,
    resolve_vm_trust,
    ssh_vm,
    vm_advance_command,
)
from scripts.ppe_vm_phase_mirror import (  # noqa: E402
    IN_FLIGHT_PHASES,
    approaching_threshold_seconds,
    load_vm_phase_mirror,
    stuck_threshold_seconds,
)

MONITOR_STATE_REL = "artifacts/control_plane/IN_FLIGHT_MONITOR_STATE.json"
MONITOR_DAEMON_STATE_REL = "artifacts/control_plane/IN_FLIGHT_MONITOR_DAEMON.json"

POLL_STALE_MIRROR_SECONDS = 60
POLL_HEALTHY_SECONDS = 1800
POLL_APPROACHING_SECONDS = 600
POLL_STUCK_SECONDS = 300
ESCALATE_COOLDOWN_SECONDS = 3600
DEFAULT_MAX_DAEMON_HOURS = 8.0
LOG_TAIL_LINES = 20
IN_FLIGHT_LOG_PATHS: dict[str, str] = {
    "BUILD_IN_FLIGHT": "artifacts/orchestrator/REMOTE_BUILD_AGENT.log",
    "FINISH_IN_FLIGHT": "artifacts/orchestrator/POST_BUILD_FINISH.log",
}


def _phase_stuck_seconds(phase: str) -> float:
    return stuck_threshold_seconds(phase)


def _tail_file(path: Path, *, lines: int = LOG_TAIL_LINES) -> list[str]:
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    rows = text.splitlines()
    return rows[-max(1, lines) :] if rows else []


def collect_stuck_log_tail(repo: Path, phase: str) -> dict[str, Any] | None:
    rel = IN_FLIGHT_LOG_PATHS.get(phase)
    if not rel:
        return None
    path = (repo / rel).resolve()
    tail = _tail_file(path)
    if not tail:
        return None
    return {"path": rel, "lines": tail}


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


def monitor_state_path(repo: Path) -> Path:
    return (repo / MONITOR_STATE_REL).resolve()


def load_monitor_state(repo: Path) -> dict[str, Any]:
    path = monitor_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_monitor_state(repo: Path, state: dict[str, Any]) -> None:
    path = monitor_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _utc_now()
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def compute_next_poll_seconds(
    *,
    phase: str,
    elapsed_s: float | None,
    mirror_stale: bool,
    wait_for_vm: bool,
) -> int:
    if mirror_stale:
        return POLL_STALE_MIRROR_SECONDS
    if not wait_for_vm and phase not in IN_FLIGHT_PHASES:
        return 0
    elapsed = float(elapsed_s or 0.0)
    if elapsed >= _phase_stuck_seconds(phase):
        return POLL_STUCK_SECONDS
    if elapsed >= approaching_threshold_seconds(phase):
        return POLL_APPROACHING_SECONDS
    return POLL_HEALTHY_SECONDS


def _elapsed_in_phase(state: dict[str, Any], phase: str) -> float | None:
    if str(state.get("watch_phase") or "") != phase:
        return None
    started = _parse_utc(str(state.get("watch_started_at") or ""))
    if started is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - started).total_seconds())


def _update_watch_state(state: dict[str, Any], phase: str, wait_for_vm: bool) -> dict[str, Any]:
    out = dict(state)
    out["last_phase"] = phase
    out["last_pass_at"] = _utc_now()
    out["pass_count"] = int(out.get("pass_count") or 0) + 1
    if wait_for_vm or phase in IN_FLIGHT_PHASES:
        if str(out.get("watch_phase") or "") != phase:
            out["watch_phase"] = phase
            out["watch_started_at"] = _utc_now()
    else:
        out.pop("watch_phase", None)
        out.pop("watch_started_at", None)
    return out


def _should_escalate(state: dict[str, Any]) -> bool:
    last = _parse_utc(str(state.get("last_escalation_at") or ""))
    if last is None:
        return True
    elapsed = (datetime.now(timezone.utc) - last).total_seconds()
    return elapsed >= ESCALATE_COOLDOWN_SECONDS


def _maybe_escalate_stuck(
    repo: Path,
    *,
    phase: str,
    elapsed_s: float,
    state: dict[str, Any],
    enable: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {"attempted": False, "skipped": True}
    if not enable:
        result["reason"] = "escalate_disabled"
        return result
    if phase not in IN_FLIGHT_PHASES:
        result["reason"] = "not_in_flight"
        return result
    if elapsed_s < _phase_stuck_seconds(phase):
        result["reason"] = "below_stuck_threshold"
        return result
    if not _should_escalate(state):
        result["reason"] = "escalate_cooldown"
        return result

    ssh = ssh_vm(vm_advance_command())
    result = {
        "attempted": True,
        "skipped": False,
        "ssh_ok": bool(ssh.get("ok")),
        "stdout": str(ssh.get("stdout") or "")[-400:],
        "stderr": str(ssh.get("stderr") or "")[-200:],
    }
    state["last_escalation_at"] = _utc_now()
    state["last_escalation_phase"] = phase
    return result


def _completion_action(trust: dict[str, Any], local_verdict: str) -> str | None:
    if trust.get("wait_for_vm"):
        return None
    rec = str(trust.get("recommended_action") or "")
    vm_phase = str(trust.get("vm_phase") or "")
    vm_verdict = str(trust.get("vm_verdict") or "")
    if rec == "desktop_continue":
        return "DESKTOP_CONTINUE.cmd --no-pause"
    if vm_phase == "RUN_LOCAL_PENDING":
        return "DESKTOP_CONTINUE.cmd --no-pause"
    if (
        local_verdict == "RUN_LOCAL"
        and vm_verdict == "RUN_LOCAL"
        and vm_phase not in ("HEALTHY_IDLE", "AWAITING_BUILD", "SUPPLY_LOW", "")
    ):
        return "DESKTOP_CONTINUE.cmd --no-pause"
    return None


def collect_monitor_snapshot(
    repo: Path,
    *,
    local_verdict: str = "",
    force_fetch: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    refresh = refresh_vm_mirror_from_git(repo, force_fetch=force_fetch)
    mirror = load_vm_phase_mirror(repo)
    mirror_health = assess_mirror_health(mirror, local_verdict=local_verdict)
    mirror_untrusted = bool(mirror_health.get("untrusted"))

    vm_brief = None
    if mirror_untrusted or not str(mirror_health.get("phase") or "").strip():
        vm_brief = fetch_vm_brief(repo, use_cache=False)

    trust = resolve_vm_trust(
        local_verdict=local_verdict,
        vm_brief=vm_brief,
        vm_mirror=mirror,
        mirror_stale=mirror_untrusted,
    )
    phase = str(trust.get("vm_phase") or mirror_health.get("phase") or "")
    wait_for_vm = bool(trust.get("wait_for_vm"))
    state = load_monitor_state(repo)
    elapsed_s = _elapsed_in_phase(state, phase) if phase else None
    if elapsed_s is None and wait_for_vm and phase:
        state = _update_watch_state(state, phase, wait_for_vm)
        elapsed_s = _elapsed_in_phase(state, phase)

    next_poll_s = compute_next_poll_seconds(
        phase=phase,
        elapsed_s=elapsed_s,
        mirror_stale=mirror_untrusted or bool(mirror_health.get("heartbeat_overdue")),
        wait_for_vm=wait_for_vm,
    )
    stuck_threshold_s = _phase_stuck_seconds(phase) if phase in IN_FLIGHT_PHASES else None
    stuck_threshold_m = int(stuck_threshold_s // 60) if stuck_threshold_s is not None else None
    stuck = bool(
        wait_for_vm
        and elapsed_s is not None
        and stuck_threshold_s is not None
        and elapsed_s >= stuck_threshold_s
    )
    stuck_at: str | None = None
    if stuck and state.get("watch_started_at"):
        started = _parse_utc(str(state.get("watch_started_at") or ""))
        if started is not None and stuck_threshold_s is not None:
            stuck_dt = started + timedelta(seconds=stuck_threshold_s)
            stuck_at = stuck_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    log_tail = collect_stuck_log_tail(repo, phase) if stuck else None
    completion = _completion_action(trust, local_verdict)
    done = not wait_for_vm and bool(completion or phase not in IN_FLIGHT_PHASES)

    mins = int((elapsed_s or 0) // 60)
    if wait_for_vm:
        status = "stuck" if stuck else "watching"
        message = (
            f"Watching `{phase}` — {mins}m elapsed; next check in {max(1, next_poll_s // 60)}m."
        )
        if mirror_untrusted:
            message += " Mirror untrusted — refreshed from git; confirm phase."
        elif mirror_health.get("heartbeat_overdue"):
            message += " Mirror heartbeat overdue — git pull or wait for VM publish."
    elif completion:
        status = "action_ready"
        message = f"Phase cleared (`{phase}`) — run {completion}."
        done = True
    elif done:
        status = "cleared"
        message = f"Phase `{phase}` — no longer in-flight."
    else:
        status = "idle"
        message = f"Phase `{phase}` — monitor not required."

    return {
        "as_of": _utc_now(),
        "phase": phase or None,
        "verdict": trust.get("vm_verdict"),
        "local_verdict": local_verdict or None,
        "source": trust.get("source"),
        "wait_for_vm": wait_for_vm,
        "mirror_stale": mirror_untrusted,
        "mirror_untrusted": mirror_untrusted,
        "mirror_heartbeat_overdue": bool(mirror_health.get("heartbeat_overdue")),
        "mirror_age_s": mirror_age_seconds(mirror),
        "mirror_refresh": refresh,
        "elapsed_in_phase_s": elapsed_s,
        "elapsed_in_phase_m": mins if elapsed_s is not None else None,
        "stuck": stuck,
        "stuck_at": stuck_at,
        "stuck_threshold_s": stuck_threshold_s,
        "stuck_threshold_m": stuck_threshold_m,
        "log_tail": log_tail,
        "next_poll_s": next_poll_s,
        "next_poll_m": max(0, next_poll_s // 60),
        "status": status,
        "done": done,
        "completion_action": completion,
        "message": message,
        "trust": trust,
    }


def run_monitor_pass(
    repo: Path,
    *,
    local_verdict: str = "",
    force_fetch: bool = False,
    escalate: bool = True,
    auto_act: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    state = load_monitor_state(repo)
    prior_status = str((state.get("last_snapshot") or {}).get("status") or "")

    snapshot = collect_monitor_snapshot(
        repo, local_verdict=local_verdict, force_fetch=force_fetch
    )
    phase = str(snapshot.get("phase") or "")
    wait_for_vm = bool(snapshot.get("wait_for_vm"))
    elapsed_s = snapshot.get("elapsed_in_phase_s")
    state = _update_watch_state(state, phase, wait_for_vm)

    current_status = str(snapshot.get("status") or "")
    if current_status == "action_ready" and prior_status != "action_ready":
        try:
            from scripts.ppe_notify_push import maybe_notify_action_ready

            maybe_notify_action_ready(
                repo,
                phase=phase,
                completion_action=str(snapshot.get("completion_action") or ""),
            )
        except Exception:
            pass

    escalation: dict[str, Any] = {"skipped": True}
    if snapshot.get("stuck"):
        escalation = _maybe_escalate_stuck(
            repo,
            phase=phase,
            elapsed_s=float(elapsed_s or 0),
            state=state,
            enable=escalate,
        )
        if escalation.get("attempted"):
            snapshot["message"] += " Escalated: VM ppe_autobuilder.cmd advance."

    auto_act_result: dict[str, Any] | None = None
    completion = snapshot.get("completion_action")
    if auto_act and completion and snapshot.get("done"):
        try:
            from scripts.ppe_operator_dispatch import dispatch_direct_action

            auto_act_result = dispatch_direct_action(
                repo,
                str(completion),
                force=True,
            )
        except Exception as exc:
            auto_act_result = {"ok": False, "error": str(exc)}
        state["last_auto_act"] = auto_act_result
        if auto_act_result and auto_act_result.get("ok"):
            try:
                from scripts.ppe_notify_push import maybe_notify_action_ready

                maybe_notify_action_ready(
                    repo,
                    phase=phase,
                    completion_action=str(completion or ""),
                    auto_dispatched=True,
                )
            except Exception:
                pass

    state["last_snapshot"] = {
        "phase": snapshot.get("phase"),
        "status": snapshot.get("status"),
        "done": snapshot.get("done"),
        "next_poll_s": snapshot.get("next_poll_s"),
    }
    save_monitor_state(repo, state)

    return {
        **snapshot,
        "escalation": escalation,
        "auto_act": auto_act_result,
    }


def monitor_daemon_state_path(repo: Path) -> Path:
    return (repo / MONITOR_DAEMON_STATE_REL).resolve()


def load_monitor_daemon_state(repo: Path) -> dict[str, Any]:
    path = monitor_daemon_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_monitor_daemon_state(repo: Path, state: dict[str, Any]) -> None:
    path = monitor_daemon_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _utc_now()
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def monitor_daemon_running(repo: Path) -> bool:
    from scripts.ppe_remote_agent_spawn import process_alive

    state = load_monitor_daemon_state(repo)
    pid = state.get("daemon_pid")
    if pid is None:
        return False
    try:
        return process_alive(int(pid))
    except (TypeError, ValueError):
        return False


def start_detached_daemon(repo: Path, *, auto_act: bool = False) -> dict[str, Any]:
    from scripts.ppe_remote_agent_spawn import process_alive, spawn_python_worker

    repo = repo.resolve()
    state = load_monitor_daemon_state(repo)
    pid = state.get("daemon_pid")
    if pid is not None:
        try:
            if process_alive(int(pid)):
                return {"started": False, "reason": "already running", "pid": int(pid)}
        except (TypeError, ValueError):
            pass

    args = ["scripts/ppe_in_flight_monitor.py", "--repo-root", str(repo), "--daemon"]
    if auto_act:
        args.append("--auto-act")
    proc = spawn_python_worker(repo, *args)
    save_monitor_daemon_state(
        repo,
        {
            "daemon_pid": proc.pid,
            "auto_act": auto_act,
            "started_at": _utc_now(),
        },
    )
    return {"started": True, "pid": proc.pid, "auto_act": auto_act}


def stop_daemon(repo: Path) -> dict[str, Any]:
    import subprocess

    from scripts.ppe_remote_agent_spawn import process_alive

    repo = repo.resolve()
    state = load_monitor_daemon_state(repo)
    killed: list[int] = []
    pid = state.get("daemon_pid")
    if pid is not None:
        try:
            pid_i = int(pid)
            if process_alive(pid_i):
                subprocess.run(
                    ["taskkill", "/PID", str(pid_i), "/F"],
                    capture_output=True,
                    check=False,
                )
                killed.append(pid_i)
        except (TypeError, ValueError):
            pass
    save_monitor_daemon_state(repo, {"daemon_pid": None, "stopped_at": _utc_now()})
    return {"stopped": True, "killed": killed}


def maybe_start_monitor_daemon(repo: Path, *, auto_act: bool = False) -> dict[str, Any]:
    """Start background monitor if not already running (desktop only)."""
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        if bool(loop_host_start_allowed()[0]):
            return {"skipped": True, "reason": "loop_host"}
    except Exception:
        pass
    if monitor_daemon_running(repo):
        state = load_monitor_daemon_state(repo)
        return {"started": False, "reason": "already running", "pid": state.get("daemon_pid")}
    return start_detached_daemon(repo, auto_act=auto_act)


def format_brief(result: dict[str, Any]) -> str:
    status = str(result.get("status") or "?")
    phase = result.get("phase") or "?"
    elapsed = result.get("elapsed_in_phase_m")
    elapsed_s = f"{elapsed}m" if elapsed is not None else "?"
    next_m = result.get("next_poll_m")
    parts = [
        f"[IN_FLIGHT_MONITOR] {status} phase={phase} elapsed={elapsed_s}",
    ]
    if result.get("done"):
        action = result.get("completion_action")
        if action:
            parts.append(f"action={action}")
    elif next_m is not None and int(result.get("next_poll_s") or 0) > 0:
        parts.append(f"next_check={next_m}m")
    msg = str(result.get("message") or "").strip()
    if msg:
        parts.append(msg)
    return " · ".join(parts)


def run_daemon(
    repo: Path,
    *,
    local_verdict: str = "",
    max_hours: float = DEFAULT_MAX_DAEMON_HOURS,
    escalate: bool = True,
    auto_act: bool = False,
) -> int:
    repo = repo.resolve()
    deadline = time.monotonic() + max(0.5, max_hours) * 3600.0
    last_brief = ""
    while time.monotonic() < deadline:
        result = run_monitor_pass(
            repo,
            local_verdict=local_verdict,
            escalate=escalate,
            auto_act=auto_act,
        )
        brief = format_brief(result)
        if brief != last_brief:
            print(brief, flush=True)
            last_brief = brief
        if result.get("done"):
            return 0
        sleep_s = max(30, int(result.get("next_poll_s") or POLL_HEALTHY_SECONDS))
        time.sleep(sleep_s)
    print("[IN_FLIGHT_MONITOR] max_hours reached — rotate operator thread.", flush=True)
    return 2


def _read_cached_local_verdict(repo: Path) -> str:
    """Fast verdict from last OPERATOR_STATUS.md write — avoids full collect pass."""
    path = repo / "artifacts/orchestrator/OPERATOR_STATUS.md"
    if not path.is_file():
        return ""
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:30]:
            if line.startswith("VERDICT:"):
                return line.split(":", 1)[1].strip()
    except OSError:
        return ""
    return ""


def _default_local_verdict(repo: Path) -> str:
    cached = _read_cached_local_verdict(repo)
    if cached:
        return cached
    if os.environ.get("PPE_MONITOR_FULL_STATUS", "").strip().lower() in ("1", "true", "yes"):
        try:
            from scripts.ppe_operator_status import collect_operator_status

            status = collect_operator_status(repo)
            return str(status.get("verdict") or "")
        except Exception:
            return ""
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Adaptive VM in-flight monitor (mirror-first, escalate when stuck)",
    )
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--local-verdict", default="", help="Override local verdict (default: from status)")
    ap.add_argument("--force-fetch", action="store_true", help="Bypass git fetch cooldown")
    ap.add_argument("--no-escalate", action="store_true", help="Do not SSH advance when stuck")
    ap.add_argument("--auto-act", action="store_true", help="Run completion_action when phase clears")
    ap.add_argument("--daemon", action="store_true", help="Poll until done or max-hours")
    ap.add_argument("--max-hours", type=float, default=DEFAULT_MAX_DAEMON_HOURS)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--brief", action="store_true", default=True)
    ap.add_argument("--no-brief", action="store_false", dest="brief")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    local_verdict = str(args.local_verdict or "").strip() or _default_local_verdict(repo)

    if args.daemon:
        return run_daemon(
            repo,
            local_verdict=local_verdict,
            max_hours=args.max_hours,
            escalate=not args.no_escalate,
            auto_act=args.auto_act,
        )

    result = run_monitor_pass(
        repo,
        local_verdict=local_verdict,
        force_fetch=args.force_fetch,
        escalate=not args.no_escalate,
        auto_act=args.auto_act,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.brief:
        print(format_brief(result))
    return 0 if result.get("done") or not result.get("wait_for_vm") else 1


if __name__ == "__main__":
    raise SystemExit(main())
