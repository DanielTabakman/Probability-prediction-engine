"""ACTIVE_RUN.json lifecycle for local relay and ACP wrappers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ACTIVE_RUN_REL = "artifacts/orchestrator/ACTIVE_RUN.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def active_run_path(repo: Path) -> Path:
    return (repo.resolve() / ACTIVE_RUN_REL).resolve()


def write_active_run(
    repo: Path,
    *,
    kind: str,
    plan_path: str,
    slice_id: str | None = None,
    baseline_branch: str = "main",
) -> Path:
    """Record an in-flight local/relay run (mirrors run_phase.cmd marker)."""
    path = active_run_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "kind": kind,
        "plan_path": plan_path.replace("\\", "/"),
        "baseline_branch": baseline_branch,
        "ts_utc": _utc_now(),
    }
    if slice_id:
        payload["slice_id"] = slice_id
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def clear_active_run(repo: Path) -> bool:
    path = active_run_path(repo)
    if not path.is_file():
        return False
    path.unlink(missing_ok=True)
    return True


def load_active_run(repo: Path) -> dict[str, Any] | None:
    path = active_run_path(repo)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def heal_stale_running_manifest(repo: Path) -> bool:
    """Reset manifest RUNNING -> READY when no ACTIVE_RUN marks an in-flight pass."""
    from scripts.ppe_manifest import load_manifest, save_manifest

    try:
        manifest = load_manifest(repo)
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    if str(manifest.get("status") or "").upper() != "RUNNING":
        return False
    if active_run_path(repo).is_file():
        return False
    manifest["status"] = "READY"
    save_manifest(repo, manifest)
    print("ppe_active_run: healed stale manifest RUNNING -> READY (no ACTIVE_RUN)")
    return True
