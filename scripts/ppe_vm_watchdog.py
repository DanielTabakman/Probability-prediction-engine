"""VM loop-host watchdog — rate-limited stack recovery when loop is down."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_REL = "artifacts/orchestrator/VM_WATCHDOG_STATE.json"
DEFAULT_DOWN_THRESHOLD = 2
DEFAULT_COOLDOWN_SEC = 3600


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _stack_healthy(repo: Path) -> tuple[bool, dict[str, Any]]:
    from scripts.ppe_autobuilder import collect_autobuilder_status

    status = collect_autobuilder_status(repo.resolve())
    stack = status.get("stack") or {}
    loop_ok = bool(stack.get("loop_running"))
    watch_ok = bool(stack.get("watch_running"))
    phase = str(status.get("phase") or "")
    healthy = loop_ok and watch_ok and phase != "STACK_DOWN"
    return healthy, {
        "phase": phase,
        "verdict": status.get("verdict"),
        "loop_running": loop_ok,
        "watch_running": watch_ok,
    }


def _cooldown_active(state: dict[str, Any], *, cooldown_sec: int) -> bool:
    last = str(state.get("last_restart_at") or "").strip()
    if not last:
        return False
    try:
        ts = datetime.fromisoformat(last.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - ts).total_seconds()
    except ValueError:
        return False
    return age < cooldown_sec


def _run_ensure_stack(repo: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ["cmd", "/c", "run_ppe_headless_stack.cmd", "--ensure"],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    ok = proc.returncode == 0
    return {
        "action": "ensure_stack",
        "ok": ok,
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "").strip()[-2000:],
        "stderr": (proc.stderr or "").strip()[-1000:],
    }


def check_and_recover(
    repo: Path,
    *,
    down_threshold: int = DEFAULT_DOWN_THRESHOLD,
    cooldown_sec: int = DEFAULT_COOLDOWN_SEC,
    apply: bool = True,
) -> dict[str, Any]:
    repo = repo.resolve()
    healthy, snapshot = _stack_healthy(repo)
    state = load_state(repo)
    consecutive = int(state.get("consecutive_down") or 0)

    if healthy:
        state["consecutive_down"] = 0
        state["last_healthy_at"] = _utc_now()
        save_state(repo, state)
        return {"action": "watchdog", "healthy": True, "snapshot": snapshot, "restarted": False}

    consecutive += 1
    state["consecutive_down"] = consecutive
    state["last_unhealthy_at"] = _utc_now()
    result: dict[str, Any] = {
        "action": "watchdog",
        "healthy": False,
        "snapshot": snapshot,
        "consecutive_down": consecutive,
        "restarted": False,
    }

    if consecutive < down_threshold:
        save_state(repo, state)
        result["reason"] = f"down {consecutive}/{down_threshold} — waiting before restart"
        return result

    if _cooldown_active(state, cooldown_sec=cooldown_sec):
        save_state(repo, state)
        result["reason"] = f"cooldown active ({cooldown_sec}s) — skip restart"
        return result

    if not apply:
        result["reason"] = "would restart stack (dry-run)"
        save_state(repo, state)
        return result

    ensure = _run_ensure_stack(repo)
    result["ensure"] = ensure
    if ensure.get("ok"):
        state["last_restart_at"] = _utc_now()
        state["consecutive_down"] = 0
        result["restarted"] = True
        try:
            from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy

            if notify_enabled() and ntfy_configured():
                phase = str(snapshot.get("phase") or "STACK_DOWN")
                send_ntfy(
                    "PPE VM watchdog: stack restarted",
                    f"Loop host was down — ran ensure_stack. Phase was {phase}.",
                    tags=["ppe", "watchdog", "stack"],
                    priority="high",
                )
        except Exception:
            pass
    save_state(repo, state)
    return result


def maybe_supervisor_tick(repo: Path) -> None:
    """Lightweight hook from headless supervisor poll loop."""
    if os.environ.get("PPE_VM_WATCHDOG", "1").strip().lower() in ("0", "false", "no", "off"):
        return
    try:
        check_and_recover(repo, apply=True)
    except Exception as exc:
        print(f"ppe_vm_watchdog: supervisor tick failed: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="VM loop-host watchdog")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--down-threshold", type=int, default=DEFAULT_DOWN_THRESHOLD)
    ap.add_argument("--cooldown-sec", type=int, default=DEFAULT_COOLDOWN_SEC)
    args = ap.parse_args(argv)

    result = check_and_recover(
        args.repo_root.resolve(),
        down_threshold=max(1, args.down_threshold),
        cooldown_sec=max(60, args.cooldown_sec),
        apply=not args.dry_run,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif not args.quiet:
        if result.get("healthy"):
            print("ppe_vm_watchdog: stack healthy")
        elif result.get("restarted"):
            print("ppe_vm_watchdog: restarted headless stack")
        else:
            print(f"ppe_vm_watchdog: {result.get('reason', result)}")
    return 0 if result.get("healthy") or result.get("restarted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
