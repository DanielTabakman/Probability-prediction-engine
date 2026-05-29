"""Repo-local auto-operator settings (docs/SOP/PPE_AUTO_OPERATOR.json)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

OPERATOR_REL = "docs/SOP/PPE_AUTO_OPERATOR.json"


def operator_config_path(repo_root: Path) -> Path:
    return (repo_root / OPERATOR_REL).resolve()


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
    if operator_enabled(repo_root) and cfg.get("stewardCharter") is True:
        return True
    return False


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
    if cfg.get("stewardCharter") is True:
        _set("PPE_AUTO_STEWARD", "1")
    wm = str(cfg.get("workerMode") or "deterministic").strip()
    if wm:
        _set("PPE_WORKER_MODE", wm)
    if cfg.get("skipAcp", True) is not False:
        _set("PPE_SKIP_ACP", "1")
    return {"applied": True, "config": cfg}
