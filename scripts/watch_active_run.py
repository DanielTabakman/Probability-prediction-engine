"""
Watch ACTIVE_RUN.json while run_phase / run_ppe is in flight.

- At susMinutes: Windows toast (scripts/notify_run_stalled.ps1) once per slice.
- At hardMinutes + grace: toast, kill parent process tree, reset manifest READY,
  remove ACTIVE_RUN, write a stall marker for LAST_RUN_REPORT consumers.

Disable: PPE_WATCH=0
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_phase_plan, set_manifest_status

WATCH_STATE_REL = "artifacts/orchestrator/watch_state.json"
STALL_REPORT_REL = "artifacts/orchestrator/STALL_REPORT.json"
RUN_ALERT_REL = "artifacts/orchestrator/run_alert.json"
POLL_SECONDS = 20
HARD_KILL_GRACE_SECONDS = 90


@dataclass(frozen=True)
class SliceLimits:
    slice_id: str
    sus_minutes: int
    hard_minutes: int


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _limits_from_slice(sl: dict[str, Any]) -> SliceLimits:
    return SliceLimits(
        slice_id=str(sl.get("sliceId") or "").strip(),
        sus_minutes=max(1, int(sl.get("susMinutes") or 15)),
        hard_minutes=max(1, int(sl.get("hardMinutes") or 30)),
    )


def resolve_slice_limits(
    repo: Path,
    *,
    active_run: dict[str, Any],
    plan_path: str | None,
) -> SliceLimits:
    env_sus = os.environ.get("PPE_SUS_MINUTES", "").strip()
    env_hard = os.environ.get("PPE_HARD_MINUTES", "").strip()
    if env_sus.isdigit() and env_hard.isdigit():
        return SliceLimits(
            slice_id=str(active_run.get("slice_id") or ""),
            sus_minutes=int(env_sus),
            hard_minutes=int(env_hard),
        )

    plan_rel = (plan_path or str(active_run.get("plan_path") or "")).strip()
    if plan_rel:
        try:
            plan = load_phase_plan(repo, plan_rel)
            slices = plan.get("slices") or []
            summary = _read_json(repo / "artifacts/orchestrator/steward_phase_summary.json")
            cursor = int((summary or {}).get("cursor") or 0)
            if 0 <= cursor < len(slices) and isinstance(slices[cursor], dict):
                return _limits_from_slice(slices[cursor])
            if slices and isinstance(slices[0], dict):
                return _limits_from_slice(slices[0])
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    return SliceLimits(
        slice_id=str(active_run.get("slice_id") or ""),
        sus_minutes=15,
        hard_minutes=30,
    )


def stall_level(elapsed_seconds: float, limits: SliceLimits) -> str | None:
    sus_s = limits.sus_minutes * 60
    hard_s = limits.hard_minutes * 60 + HARD_KILL_GRACE_SECONDS
    if elapsed_seconds >= hard_s:
        return "hard"
    if elapsed_seconds >= sus_s:
        return "sus"
    return None


def _notify_run_alert(repo: Path, alert: dict[str, Any], *, plan_path: str) -> None:
    ps1 = repo / "scripts" / "notify_run_error.ps1"
    if not ps1.is_file():
        return
    reason = str(alert.get("reason") or "orchestrator run_alert")
    slice_id = str(alert.get("slice_id") or "")
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ps1),
            "-RepoRoot",
            str(repo),
            "-Reason",
            reason[:400],
            "-SliceId",
            slice_id,
            "-PlanPath",
            plan_path,
        ],
        cwd=repo,
        check=False,
    )


def _notify(repo: Path, level: str, limits: SliceLimits, *, plan_path: str, elapsed_min: int) -> None:
    ps1 = repo / "scripts" / "notify_run_stalled.ps1"
    if not ps1.is_file():
        return
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ps1),
            "-RepoRoot",
            str(repo),
            "-Level",
            level,
            "-SliceId",
            limits.slice_id,
            "-PlanPath",
            plan_path,
            "-ElapsedMinutes",
            str(elapsed_min),
            "-LimitMinutes",
            str(limits.sus_minutes if level == "sus" else limits.hard_minutes),
        ],
        cwd=repo,
        check=False,
    )


def _kill_process_tree(pid: int) -> None:
    if pid <= 0:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            check=False,
            capture_output=True,
        )
    else:
        try:
            os.kill(pid, 9)
        except OSError:
            pass


def _write_stall_report(
    repo: Path,
    *,
    level: str,
    limits: SliceLimits,
    elapsed_seconds: float,
    parent_pid: int,
    active_run: dict[str, Any],
) -> None:
    out = repo / STALL_REPORT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": _utc_now_iso(),
        "level": level,
        "elapsed_seconds": round(elapsed_seconds, 1),
        "slice_id": limits.slice_id,
        "sus_minutes": limits.sus_minutes,
        "hard_minutes": limits.hard_minutes,
        "parent_pid": parent_pid,
        "active_run": active_run,
        "message": (
            "Watchdog terminated a stuck orchestrator run. "
            "Common causes: ACP provider error, hung sendPrompt, or relay_result never written."
        ),
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_watch_state(repo: Path) -> dict[str, Any]:
    return _read_json(repo / WATCH_STATE_REL) or {}


def _save_watch_state(repo: Path, state: dict[str, Any]) -> None:
    p = repo / WATCH_STATE_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _already_notified(state: dict[str, Any], key: str) -> bool:
    return bool(state.get(key))


def _mark_notified(state: dict[str, Any], key: str) -> None:
    state[key] = _utc_now_iso()


def _resolve_parent_pid(active: dict[str, Any], fallback: int) -> int:
    try:
        wp = int(active.get("wrapper_pid") or 0)
    except (TypeError, ValueError):
        wp = 0
    return wp if wp > 0 else fallback


def watch_loop(repo: Path, parent_pid: int, plan_path: str | None) -> int:
    active_path = repo / "artifacts/orchestrator/ACTIVE_RUN.json"
    state = _load_watch_state(repo)

    while True:
        if not active_path.is_file():
            return 0

        active = _read_json(active_path)
        if not active:
            time.sleep(POLL_SECONDS)
            continue

        kill_pid = _resolve_parent_pid(active, parent_pid)
        if kill_pid > 0 and not _pid_alive(kill_pid):
            return 0

        alert_path = repo / RUN_ALERT_REL
        alert = _read_json(alert_path)
        if alert:
            alert_key = f"alert_notified:{alert.get('ts_utc') or alert_path.stat().st_mtime}"
            if not _already_notified(state, alert_key):
                plan_rel_alert = plan_path or str(active.get("plan_path") or "")
                _notify_run_alert(repo, alert, plan_path=plan_rel_alert)
                _mark_notified(state, alert_key)
                _save_watch_state(repo, state)
                print(
                    f"watch_active_run: run_alert notified ({alert.get('reason', '')[:80]})",
                    flush=True,
                )

        started = active_path.stat().st_mtime
        elapsed = max(0.0, time.time() - started)
        limits = resolve_slice_limits(repo, active_run=active, plan_path=plan_path)
        level = stall_level(elapsed, limits)
        elapsed_min = int(elapsed // 60)
        plan_rel = plan_path or str(active.get("plan_path") or "")

        if level == "sus":
            key = f"sus_notified:{limits.slice_id or 'unknown'}"
            if not _already_notified(state, key):
                _notify(repo, "sus", limits, plan_path=plan_rel, elapsed_min=elapsed_min)
                _mark_notified(state, key)
                _save_watch_state(repo, state)
                print(
                    f"watch_active_run: SUS {elapsed_min}m "
                    f"(slice={limits.slice_id or '?'}, limit={limits.sus_minutes}m)",
                    flush=True,
                )

        if level == "hard":
            key = f"hard_notified:{limits.slice_id or 'unknown'}"
            if not _already_notified(state, key):
                _notify(repo, "hard", limits, plan_path=plan_rel, elapsed_min=elapsed_min)
                _mark_notified(state, key)
                _save_watch_state(repo, state)

            _write_stall_report(
                repo,
                level="hard",
                limits=limits,
                elapsed_seconds=elapsed,
                parent_pid=parent_pid,
                active_run=active,
            )
            try:
                set_manifest_status(repo, "READY")
            except Exception:
                pass
            try:
                active_path.unlink(missing_ok=True)
            except OSError:
                pass
            _kill_process_tree(kill_pid)
            print(
                f"watch_active_run: HARD kill after {elapsed_min}m "
                f"(slice={limits.slice_id or '?'}, limit={limits.hard_minutes}m)",
                flush=True,
            )
            return 2

        time.sleep(POLL_SECONDS)


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            check=False,
        )
        return str(pid) in (r.stdout or "")
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Watch ACTIVE_RUN and alert / kill on stall")
    ap.add_argument("--repo-root", type=Path, default=None)
    ap.add_argument("--parent-pid", type=int, required=True)
    ap.add_argument("--plan-path", type=str, default="")
    args = ap.parse_args(argv)

    if os.environ.get("PPE_WATCH", "").strip().lower() in {"0", "false", "no"}:
        return 0

    repo = (args.repo_root or Path.cwd()).resolve()
    return watch_loop(repo, args.parent_pid, args.plan_path.strip() or None)


if __name__ == "__main__":
    raise SystemExit(main())
