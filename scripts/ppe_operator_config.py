"""Repo-local auto-operator settings (docs/SOP/PPE_AUTO_OPERATOR*.json)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

OPERATOR_REL = "docs/SOP/PPE_AUTO_OPERATOR.json"
OPERATOR_PROFILE_REL: dict[str, str] = {
    "local": "docs/SOP/PPE_AUTO_OPERATOR.local.json",
    "acp": "docs/SOP/PPE_AUTO_OPERATOR.acp.json",
}


def operator_config_path(repo_root: Path) -> Path:
    repo = repo_root.resolve()
    profile = (os.environ.get("PPE_OPERATOR_PROFILE") or "").strip().lower()
    if profile in OPERATOR_PROFILE_REL:
        profile_path = (repo / OPERATOR_PROFILE_REL[profile]).resolve()
        if profile_path.is_file():
            return profile_path
    return (repo / OPERATOR_REL).resolve()


def load_operator_config(repo_root: Path) -> dict[str, Any]:
    p = operator_config_path(repo_root)
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _guards_config(cfg: dict[str, Any]) -> dict[str, Any]:
    raw = cfg.get("guards")
    if isinstance(raw, dict):
        return raw
    return {}


def guards_enabled(repo_root: Path) -> bool:
    env = os.environ.get("PPE_OPERATOR_GUARDS", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    cfg = load_operator_config(repo_root)
    g = _guards_config(cfg)
    if g.get("enabled") is False:
        return False
    return bool(g.get("enabled", True))


def operator_enabled(repo_root: Path) -> bool:
    cfg = load_operator_config(repo_root)
    return bool(cfg.get("enabled"))


def skip_acp_from_config(cfg: dict[str, Any]) -> bool:
    return cfg.get("skipAcp", True) is not False


def steward_charter_enabled(repo_root: Path) -> bool:
    env = os.environ.get("PPE_AUTO_STEWARD", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    cfg = load_operator_config(repo_root)
    if not operator_enabled(repo_root) or cfg.get("stewardCharter") is not True:
        return False
    if skip_acp_from_config(cfg):
        return False
    return True


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


def guard_stop_sleep_seconds(repo_root: Path) -> int:
    cfg = load_operator_config(repo_root)
    try:
        return max(60, int(cfg.get("guardStopSleepSeconds", 300)))
    except (TypeError, ValueError):
        return 300


def keep_loop_alive_on_guard_stop(repo_root: Path) -> bool:
    cfg = load_operator_config(repo_root)
    if cfg.get("keepLoopAliveOnGuardStop") is False:
        return False
    return bool(cfg.get("keepLoopAliveOnGuardStop", True))


def auto_remote_build_enabled(repo_root: Path) -> bool:
    """When True, mobile watch auto-starts agent CLI on IDE_BUILD (no phone 'build' tap)."""
    env = os.environ.get("PPE_AUTO_REMOTE_BUILD", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    cfg = load_operator_config(repo_root)
    return cfg.get("autoRemoteBuild", True) is not False


def continuous_max(repo_root: Path) -> int:
    cfg = load_operator_config(repo_root)
    try:
        return max(1, int(cfg.get("continuousMax", 20)))
    except (TypeError, ValueError):
        return 20


def apply_operator_env(repo_root: Path) -> dict[str, Any]:
    """Set process env from operator config (does not override explicit env)."""
    cfg = load_operator_config(repo_root)
    if not cfg.get("enabled"):
        return {"applied": False, "reason": "operator config disabled or missing"}

    def _set(key: str, value: str) -> None:
        if key not in os.environ or not str(os.environ.get(key) or "").strip():
            os.environ[key] = value

    _set("PPE_AUTO_ROADMAP", "1")
    if cfg.get("propagateBacklog", True) is not False:
        _set("PPE_AUTO_PROPAGATE_QUEUE", "1")
    skip_acp = skip_acp_from_config(cfg)
    if skip_acp:
        _set("PPE_SKIP_ACP", "1")
    if cfg.get("stewardCharter") is True and not skip_acp:
        _set("PPE_AUTO_STEWARD", "1")
    wm = str(cfg.get("workerMode") or "deterministic").strip()
    if wm:
        _set("PPE_WORKER_MODE", wm)
    profile = (os.environ.get("PPE_OPERATOR_PROFILE") or cfg.get("profile") or "").strip()
    if profile:
        _set("PPE_OPERATOR_PROFILE", profile)
    if auto_remote_build_enabled(repo_root):
        _set("PPE_AUTO_REMOTE_BUILD", "1")
    return {"applied": True, "config": cfg, "config_path": str(operator_config_path(repo_root))}
