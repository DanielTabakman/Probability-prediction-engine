"""Operator instance identity — labels clones for multi-loop hosts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterator

INSTANCES_EXAMPLE_REL = "docs/SOP/PPE_OPERATOR_INSTANCES.example.json"
INSTANCES_LOCAL_REL = "docs/SOP/PPE_OPERATOR_INSTANCES.local.json"
MULTI_STATUS_REL = "artifacts/orchestrator/MULTI_OPERATOR_STATUS.json"


def operator_instance_id() -> str:
    raw = os.environ.get("PPE_OPERATOR_INSTANCE", "").strip()
    return raw or "default"


def _config_search_roots(repo_root: Path) -> list[Path]:
    roots: list[Path] = [repo_root.resolve()]
    coord = os.environ.get("PPE_COORDINATOR_REPO", "").strip()
    if coord:
        c = Path(coord).expanduser().resolve()
        if c not in roots:
            roots.append(c)
    return roots


def instances_config_path(coordinator: Path) -> Path:
    env = os.environ.get("PPE_OPERATOR_INSTANCES_PATH", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    local = (coordinator / INSTANCES_LOCAL_REL).resolve()
    if local.is_file():
        return local
    return (coordinator / INSTANCES_EXAMPLE_REL).resolve()


def _read_instances_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"version": 1, "instances": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "instances": []}
    return data if isinstance(data, dict) else {"version": 1, "instances": []}


def load_instances_config(repo_root: Path) -> dict[str, Any]:
    for base in _config_search_roots(repo_root):
        path = instances_config_path(base)
        if path.is_file():
            return _read_instances_file(path)
    return {"version": 1, "instances": []}


def _norm_repo(path: str | Path) -> str:
    p = Path(path).expanduser()
    try:
        p = p.resolve()
    except OSError:
        p = p.absolute()
    return os.path.normcase(str(p)).replace("\\", "/")


def _resolve_config_repo_root(coordinator: Path, root: str) -> Path:
    raw = str(root or ".").strip() or "."
    p = Path(raw)
    if p.is_absolute():
        return p.resolve()
    return (coordinator / p).resolve()


def _iter_configured_instances(repo_root: Path) -> Iterator[tuple[Path, dict[str, Any], Path]]:
    seen: set[str] = set()
    for base in _config_search_roots(repo_root):
        cfg = _read_instances_file(instances_config_path(base))
        for item in cfg.get("instances") or []:
            if not isinstance(item, dict):
                continue
            resolved = _resolve_config_repo_root(base, str(item.get("repoRoot") or "."))
            key = _norm_repo(resolved)
            if key in seen:
                continue
            seen.add(key)
            yield base, item, resolved


def _instance_from_row(item: dict[str, Any], resolved: Path, *, env_id: str) -> dict[str, Any]:
    return {
        "id": str(item.get("id") or env_id or "default"),
        "label": str(item.get("label") or item.get("id") or "primary"),
        "repoRoot": _norm_repo(resolved),
        "ntfyTag": str(item.get("ntfyTag") or "").strip() or None,
        "enabled": item.get("enabled", True) is not False,
    }


def resolve_instance_for_repo(repo_root: Path) -> dict[str, Any]:
    """Return instance metadata for a repo root (from config or default)."""
    repo = repo_root.resolve()
    env_id = operator_instance_id()
    repo_key = _norm_repo(repo)
    for _base, item, resolved in _iter_configured_instances(repo):
        if _norm_repo(resolved) == repo_key:
            return _instance_from_row(item, resolved, env_id=env_id)
    if env_id != "default":
        return {
            "id": env_id,
            "label": env_id,
            "repoRoot": repo_key,
            "ntfyTag": None,
            "enabled": True,
        }
    return {
        "id": "default",
        "label": "primary",
        "repoRoot": repo_key,
        "ntfyTag": None,
        "enabled": True,
    }


def list_enabled_instances(coordinator_repo: Path) -> list[dict[str, Any]]:
    """Instances from config; always includes the coordinator repo if missing."""
    coordinator = coordinator_repo.resolve()
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    env_id = operator_instance_id()
    for _base, item, resolved in _iter_configured_instances(coordinator):
        if item.get("enabled") is False:
            continue
        key = _norm_repo(resolved)
        if key in seen:
            continue
        seen.add(key)
        out.append(_instance_from_row(item, resolved, env_id=env_id))
    if _norm_repo(coordinator) not in seen:
        out.insert(0, resolve_instance_for_repo(coordinator))
    return out


def loop_lock_path(repo_root: Path) -> Path:
    """Per-repo loop singleton lock (allows multiple clones on one host)."""
    inst = resolve_instance_for_repo(repo_root)
    inst_id = str(inst.get("id") or "default")
    if inst_id == "default":
        return (repo_root / "artifacts/orchestrator/LOOP_SINGLETON.lock").resolve()
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in inst_id)
    return (repo_root / "artifacts/orchestrator" / f"LOOP_SINGLETON_{safe}.lock").resolve()
