"""Desktop: refresh VM phase mirror from git + assess mirror age without SSH."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_vm_phase_mirror import VM_OPERATOR_PHASE_REL, load_vm_phase_mirror, mirror_path

MIRROR_STALE_SECONDS = 1800
MIRROR_FETCH_MIN_INTERVAL_SECONDS = 120
FETCH_STATE_REL = "artifacts/control_plane/VM_MIRROR_FETCH_STATE.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw or raw == "null":
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def mirror_age_seconds(mirror: dict[str, Any] | None) -> float | None:
    if not mirror:
        return None
    as_of = str(mirror.get("as_of") or "").strip()
    ts = _parse_utc(as_of)
    if ts is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - ts).total_seconds())


def mirror_is_populated(mirror: dict[str, Any] | None) -> bool:
    if not mirror:
        return False
    phase = str(mirror.get("phase") or "").strip()
    return bool(phase) and phase.lower() != "null"


def mirror_is_stale(
    mirror: dict[str, Any] | None,
    *,
    stale_seconds: int = MIRROR_STALE_SECONDS,
) -> bool:
    if not mirror_is_populated(mirror):
        return True
    age = mirror_age_seconds(mirror)
    if age is None:
        return True
    return age > max(60, int(stale_seconds))


def _fetch_state_path(repo: Path) -> Path:
    return (repo / FETCH_STATE_REL).resolve()


def _load_fetch_state(repo: Path) -> dict[str, Any]:
    path = _fetch_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_fetch_state(repo: Path, state: dict[str, Any]) -> None:
    path = _fetch_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def maybe_fetch_origin_main(repo: Path, *, force: bool = False) -> dict[str, Any]:
    """Rate-limited git fetch for mirror refresh (desktop only)."""
    repo = repo.resolve()
    prior = _load_fetch_state(repo)
    last_at = _parse_utc(str(prior.get("last_fetch_at") or ""))
    if not force and last_at is not None:
        elapsed = (datetime.now(timezone.utc) - last_at).total_seconds()
        if elapsed < MIRROR_FETCH_MIN_INTERVAL_SECONDS:
            return {"fetched": False, "reason": "fetch_cooldown", "elapsed_s": elapsed}

    proc = _git(repo, "fetch", "origin", "main", "--quiet")
    result: dict[str, Any] = {
        "fetched": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stderr": (proc.stderr or "").strip()[-200:],
    }
    if proc.returncode == 0:
        _save_fetch_state(repo, {"last_fetch_at": _utc_now()})
    return result


def read_mirror_from_git_ref(repo: Path, ref: str = "origin/main") -> dict[str, Any] | None:
    proc = _git(repo, "show", f"{ref}:{VM_OPERATOR_PHASE_REL.replace(chr(92), '/')}")
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def refresh_vm_mirror_from_git(
    repo: Path,
    *,
    force_fetch: bool = False,
    stale_seconds: int = MIRROR_STALE_SECONDS,
) -> dict[str, Any]:
    """Fetch origin/main and write VM_OPERATOR_PHASE.json when local mirror is stale."""
    repo = repo.resolve()
    local = load_vm_phase_mirror(repo)
    report: dict[str, Any] = {
        "local_populated": mirror_is_populated(local),
        "local_stale": mirror_is_stale(local, stale_seconds=stale_seconds),
        "local_age_s": mirror_age_seconds(local),
    }

    if mirror_is_populated(local) and not mirror_is_stale(local, stale_seconds=stale_seconds):
        report["action"] = "skip_fresh_local"
        return report

    fetch = maybe_fetch_origin_main(repo, force=force_fetch)
    report["fetch"] = fetch
    remote = read_mirror_from_git_ref(repo)
    report["remote_populated"] = mirror_is_populated(remote)
    report["remote_age_s"] = mirror_age_seconds(remote)

    if not mirror_is_populated(remote):
        report["action"] = "no_remote_mirror"
        return report

    if mirror_is_populated(local) and not mirror_is_stale(local, stale_seconds=stale_seconds):
        report["action"] = "skip_after_fetch"
        return report

    remote_age = mirror_age_seconds(remote) or 0.0
    local_age = mirror_age_seconds(local) or 1e9
    if remote_age < local_age or not mirror_is_populated(local):
        path = mirror_path(repo)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(remote, indent=2) + "\n", encoding="utf-8")
        report["action"] = "updated_from_git"
        report["path"] = str(path)
    else:
        report["action"] = "keep_local_newer"
    return report


def assess_mirror_health(
    mirror: dict[str, Any] | None,
    *,
    local_verdict: str = "",
    stale_seconds: int = MIRROR_STALE_SECONDS,
) -> dict[str, Any]:
    populated = mirror_is_populated(mirror)
    age = mirror_age_seconds(mirror)
    stale = mirror_is_stale(mirror, stale_seconds=stale_seconds)
    alert = False
    note = ""
    if not populated:
        alert = local_verdict in ("RUN_LOCAL", "IDE_BUILD", "RUN_AUTO")
        note = "VM mirror empty — run git pull or wait for loop host to publish phase."
    elif stale:
        alert = local_verdict in ("RUN_LOCAL", "IDE_BUILD")
        mins = int((age or 0) // 60)
        note = f"VM mirror stale ({mins}m old) — git pull origin main before trusting phase."
    return {
        "populated": populated,
        "stale": stale,
        "age_seconds": age,
        "alert": alert,
        "agent_note": note,
        "phase": str(mirror.get("phase") or "") if mirror else None,
    }
