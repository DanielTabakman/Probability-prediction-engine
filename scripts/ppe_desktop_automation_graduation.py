"""Level A → Level B desktop automation graduation (success + time thresholds).

Canon: docs/SOP/DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GRADUATION_STATE_REL = "artifacts/control_plane/DESKTOP_AUTOMATION_GRADUATION.json"
DEFAULT_MIN_SUCCESSES = 5
DEFAULT_MIN_HOURS = 48.0
SUCCESS_EVENTS = frozenset(
    {
        "desktop_continue",
        "auto_dispatch",
        "monitor_auto_act",
    }
)


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


def graduation_state_path(repo: Path) -> Path:
    return (repo / GRADUATION_STATE_REL).resolve()


def load_graduation_state(repo: Path) -> dict[str, Any]:
    path = graduation_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_graduation_state(repo: Path, state: dict[str, Any]) -> Path:
    path = graduation_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {**state, "updated_at": _utc_now()}
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path


def graduation_thresholds() -> tuple[int, float]:
    try:
        min_successes = int(os.environ.get("PPE_AUTO_GRADUATE_SUCCESSES", DEFAULT_MIN_SUCCESSES))
    except ValueError:
        min_successes = DEFAULT_MIN_SUCCESSES
    try:
        min_hours = float(os.environ.get("PPE_AUTO_GRADUATE_MIN_HOURS", DEFAULT_MIN_HOURS))
    except ValueError:
        min_hours = DEFAULT_MIN_HOURS
    return max(1, min_successes), max(1.0, min_hours)


def load_desktop_automation_env(repo: Path) -> dict[str, Any]:
    """Apply PPE_* vars from ppe_operator_desktop_auto.local.cmd (does not override explicit env)."""
    repo = repo.resolve()
    path = repo / "ppe_operator_desktop_auto.local.cmd"
    if not path.is_file():
        return {"loaded": False}
    applied: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {"loaded": False, "reason": "read_failed"}
    for raw in lines:
        line = raw.strip()
        if not line or line.upper().startswith("REM"):
            continue
        if not line.lower().startswith("set "):
            continue
        rest = line[4:].strip()
        if rest.startswith('"') and rest.endswith('"'):
            rest = rest[1:-1]
        if "=" not in rest:
            continue
        key, _, val = rest.partition("=")
        key = key.strip()
        val = val.strip().strip('"')
        if not key:
            continue
        if key not in os.environ or not str(os.environ.get(key) or "").strip():
            os.environ[key] = val
            applied.append(key)
    return {"loaded": True, "applied": applied}


def zero_click_active(repo: Path) -> bool:
    try:
        from scripts.ppe_desktop_zero_click_build import collect_status, zero_click_desired

        if not zero_click_desired(repo):
            return False
        status = collect_status(repo)
        return bool(status.get("watcher_running")) or bool(status.get("watcher_pid"))
    except Exception:
        return False


def evaluate_graduation(repo: Path, state: dict[str, Any] | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    state = state if state is not None else load_graduation_state(repo)
    min_successes, min_hours = graduation_thresholds()
    level = str(state.get("level") or "A").upper()
    success_count = int(state.get("success_count") or 0)
    first_success_at = str(state.get("first_success_at") or "")
    graduated_at = str(state.get("graduated_at") or "")

    elapsed_hours = 0.0
    first_ts = _parse_utc(first_success_at)
    if first_ts is not None:
        elapsed_hours = max(0.0, (datetime.now(timezone.utc) - first_ts).total_seconds() / 3600.0)

    if level == "B" or graduated_at:
        return {
            "level": "B",
            "eligible": False,
            "reason": "already_graduated",
            "success_count": success_count,
            "min_successes": min_successes,
            "elapsed_hours": round(elapsed_hours, 2),
            "min_hours": min_hours,
            "zero_click_active": zero_click_active(repo),
        }

    successes_ok = success_count >= min_successes
    time_ok = elapsed_hours >= min_hours if first_ts is not None else False
    eligible = successes_ok and time_ok

    reasons: list[str] = []
    if not successes_ok:
        reasons.append(f"successes {success_count}/{min_successes}")
    if not time_ok:
        if first_ts is None:
            reasons.append("no successful dispatch yet")
        else:
            reasons.append(f"elapsed {elapsed_hours:.1f}h/{min_hours:.0f}h")

    return {
        "level": "A",
        "eligible": eligible,
        "reason": "; ".join(reasons) if reasons else "thresholds met",
        "success_count": success_count,
        "min_successes": min_successes,
        "elapsed_hours": round(elapsed_hours, 2),
        "min_hours": min_hours,
        "first_success_at": first_success_at or None,
        "zero_click_active": zero_click_active(repo),
    }


def record_automation_success(
    repo: Path,
    *,
    event: str,
    report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Increment success counter when an auto-dispatch action completes OK."""
    repo = repo.resolve()
    if event not in SUCCESS_EVENTS:
        return evaluate_graduation(repo)
    rep = report or {}
    if not rep.get("ok"):
        return evaluate_graduation(repo)

    state = load_graduation_state(repo)
    if str(state.get("level") or "A").upper() == "B":
        return evaluate_graduation(repo, state)

    now = _utc_now()
    if not state.get("first_success_at"):
        state["first_success_at"] = now
    state["success_count"] = int(state.get("success_count") or 0) + 1
    state["last_success_at"] = now
    state["last_event"] = event
    history = state.get("recent") if isinstance(state.get("recent"), list) else []
    history.append(
        {
            "at": now,
            "event": event,
            "action": rep.get("action"),
            "cmd": rep.get("cmd"),
        }
    )
    state["recent"] = history[-20:]
    save_graduation_state(repo, state)
    return evaluate_graduation(repo, state)


def try_graduate_to_level_b(repo: Path) -> dict[str, Any]:
    """Promote to zero-click stack when success + time thresholds met."""
    repo = repo.resolve()
    state = load_graduation_state(repo)
    evaluation = evaluate_graduation(repo, state)
    if not evaluation.get("eligible"):
        return {"graduated": False, "evaluation": evaluation}

    if zero_click_active(repo):
        state["level"] = "B"
        state["graduated_at"] = _utc_now()
        state["graduation_note"] = "zero_click_already_running"
        save_graduation_state(repo, state)
        return {"graduated": True, "evaluation": evaluation, "note": "already_running"}

    from scripts.ppe_desktop_zero_click_build import check_agent_cli, setup, start

    agent = check_agent_cli()
    setup_result = setup(repo, install_logon=bool(agent.get("ok")))
    if not setup_result.get("ok"):
        return {
            "graduated": False,
            "evaluation": evaluation,
            "setup": setup_result,
            "reason": "setup_failed",
        }

    start_result = start(repo)
    if not start_result.get("ok"):
        return {
            "graduated": False,
            "evaluation": evaluation,
            "setup": setup_result,
            "start": start_result,
            "reason": "start_failed",
        }

    state["level"] = "B"
    state["graduated_at"] = _utc_now()
    state["graduation_note"] = "auto_graduate_level_b"
    save_graduation_state(repo, state)
    return {
        "graduated": True,
        "evaluation": evaluation,
        "setup": setup_result,
        "start": start_result,
    }


def maybe_graduate_after_success(
    repo: Path,
    *,
    event: str,
    report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record success and graduate to Level B when thresholds are met."""
    evaluation = record_automation_success(repo, event=event, report=report)
    if not evaluation.get("eligible"):
        return {"graduation": evaluation, "graduated": False}
    result = try_graduate_to_level_b(repo)
    return {"graduation": evaluation, **result}
