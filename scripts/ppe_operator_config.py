"""Repo-local auto-operator settings (docs/SOP/PPE_AUTO_OPERATOR.json)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

OPERATOR_REL = "docs/SOP/PPE_AUTO_OPERATOR.json"
OPERATOR_PROFILES: dict[str, str] = {
    "local": "docs/SOP/PPE_AUTO_OPERATOR.local.json",
    "acp": "docs/SOP/PPE_AUTO_OPERATOR.acp.json",
}


def operator_config_path(repo_root: Path) -> Path:
    explicit = os.environ.get("PPE_OPERATOR_CONFIG", "").strip()
    if explicit:
        p = Path(explicit)
        return (repo_root / p if not p.is_absolute() else p).resolve()
    profile = os.environ.get("PPE_OPERATOR_PROFILE", "").strip().lower()
    rel = OPERATOR_PROFILES.get(profile)
    if rel:
        return (repo_root / rel).resolve()
    return (repo_root / OPERATOR_REL).resolve()


def active_operator_profile(repo_root: Path) -> str:
    cfg = load_operator_config(repo_root)
    if isinstance(cfg.get("profile"), str) and cfg["profile"].strip():
        return cfg["profile"].strip()
    profile = os.environ.get("PPE_OPERATOR_PROFILE", "").strip().lower()
    if profile:
        return profile
    p = operator_config_path(repo_root)
    for name, rel in OPERATOR_PROFILES.items():
        if p.resolve() == (repo_root / rel).resolve():
            return name
    return "default"


def load_operator_config(repo_root: Path) -> dict[str, Any]:
    p = operator_config_path(repo_root)
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8-sig"))


def operator_enabled(repo_root: Path) -> bool:
    cfg = load_operator_config(repo_root)
    return bool(cfg.get("enabled"))


def steward_charter_enabled(repo_root: Path) -> bool:
    env = os.environ.get("PPE_AUTO_STEWARD", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    cfg = load_operator_config(repo_root)
    if not operator_enabled(repo_root):
        return False
    # Local/deterministic operator: skipAcp means no Cursor SDK steward charter.
    if cfg.get("skipAcp", True) is not False:
        return False
    return cfg.get("stewardCharter") is True


def propagate_backlog_enabled(repo_root: Path) -> bool:
    env = os.environ.get("PPE_AUTO_PROPAGATE_QUEUE", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    cfg = load_operator_config(repo_root)
    if operator_enabled(repo_root) and cfg.get("propagateBacklog", True) is not False:
        return True
    return True


def loop_when_idle(repo_root: Path) -> bool:
    cfg = load_operator_config(repo_root)
    if not operator_enabled(repo_root):
        return False
    return bool(cfg.get("loopWhenIdle", False))


def idle_sleep_seconds(repo_root: Path) -> int:
    cfg = load_operator_config(repo_root)
    try:
        return max(30, int(cfg.get("idleSleepSeconds", 120)))
    except (TypeError, ValueError):
        return 120


def continuous_max(repo_root: Path) -> int:
    cfg = load_operator_config(repo_root)
    try:
        return max(1, int(cfg.get("continuousMax", 20)))
    except (TypeError, ValueError):
        return 20


def planned_operator_env(repo_root: Path) -> dict[str, str]:
    """Env assignments from operator config (empty when disabled)."""
    cfg = load_operator_config(repo_root)
    if not cfg.get("enabled"):
        return {}
    out: dict[str, str] = {"PPE_AUTO_ROADMAP": "1"}
    if cfg.get("propagateBacklog", True) is not False:
        out["PPE_AUTO_PROPAGATE_QUEUE"] = "1"
    skip_acp = cfg.get("skipAcp", True) is not False
    if cfg.get("stewardCharter") is True and not skip_acp:
        out["PPE_AUTO_STEWARD"] = "1"
    wm = str(cfg.get("workerMode") or "deterministic").strip()
    if wm:
        out["PPE_WORKER_MODE"] = wm
    if skip_acp:
        out["PPE_SKIP_ACP"] = "1"
    return out


def operator_env_cmd_lines(repo_root: Path) -> list[str]:
    """Lines for cmd.exe: SET \"KEY=value\" (for for /f in .cmd wrappers)."""
    return [f'SET "{k}={v}"' for k, v in planned_operator_env(repo_root).items()]


def apply_operator_env(repo_root: Path) -> dict[str, Any]:
    """Set process env from operator config (does not override explicit env)."""
    cfg = load_operator_config(repo_root)
    if not cfg.get("enabled"):
        return {"applied": False, "reason": "operator config disabled or missing"}

    def _set(key: str, value: str) -> None:
        if key not in os.environ or not str(os.environ.get(key) or "").strip():
            os.environ[key] = value

    for key, value in planned_operator_env(repo_root).items():
        _set(key, value)
    return {"applied": True, "config": cfg}
