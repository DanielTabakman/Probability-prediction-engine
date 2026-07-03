"""Desktop: refresh VM phase mirror from git + assess mirror age without SSH."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_vm_phase_mirror import (
    IN_FLIGHT_PHASES,
    MIRROR_HEARTBEAT_PUBLISH_SECONDS,
    VM_OPERATOR_PHASE_REL,
    load_vm_phase_mirror,
    mirror_path,
)

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
    ts = _parse_utc(str(mirror.get("as_of") or ""))
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


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def maybe_fetch_origin_main(repo: Path, *, force: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    prior_path = repo / FETCH_STATE_REL
    prior: dict[str, Any] = {}
    if prior_path.is_file():
        try:
            prior = json.loads(prior_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior = {}
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
        prior_path.parent.mkdir(parents=True, exist_ok=True)
        prior_path.write_text(
            json.dumps({"last_fetch_at": _utc_now()}, indent=2) + "\n",
            encoding="utf-8",
        )
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

    report["fetch"] = maybe_fetch_origin_main(repo, force=force_fetch)
    remote = read_mirror_from_git_ref(repo)
    report["remote_populated"] = mirror_is_populated(remote)
    report["remote_age_s"] = mirror_age_seconds(remote)

    if not mirror_is_populated(remote):
        report["action"] = "no_remote_mirror"
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


def mirror_is_in_flight(mirror: dict[str, Any] | None) -> bool:
    if not mirror:
        return False
    phase = str(mirror.get("phase") or "").strip()
    return phase in IN_FLIGHT_PHASES


def assess_mirror_health(
    mirror: dict[str, Any] | None,
    *,
    local_verdict: str = "",
    stale_seconds: int = MIRROR_STALE_SECONDS,
) -> dict[str, Any]:
    populated = mirror_is_populated(mirror)
    age = mirror_age_seconds(mirror)
    stale = mirror_is_stale(mirror, stale_seconds=stale_seconds)
    in_flight = mirror_is_in_flight(mirror)
    heartbeat_overdue = (
        populated
        and in_flight
        and age is not None
        and age > max(60, int(MIRROR_HEARTBEAT_PUBLISH_SECONDS))
    )
    untrusted = not populated or (stale and not in_flight) or (populated and age is None)
    alert = False
    note = ""
    if not populated:
        alert = local_verdict in ("RUN_LOCAL", "IDE_BUILD", "RUN_AUTO")
        note = "VM mirror empty — git pull origin main or wait for loop host publish."
    elif untrusted:
        alert = local_verdict in ("RUN_LOCAL", "IDE_BUILD")
        mins = int((age or 0) // 60)
        note = f"VM mirror stale ({mins}m old) — git pull origin main before trusting phase."
    elif heartbeat_overdue:
        alert = local_verdict in ("RUN_LOCAL", "IDE_BUILD")
        mins = int((age or 0) // 60)
        note = (
            f"VM in-flight mirror heartbeat overdue ({mins}m) — "
            "git pull origin main or wait for loop host publish."
        )
    return {
        "populated": populated,
        "stale": stale,
        "untrusted": untrusted,
        "heartbeat_overdue": heartbeat_overdue,
        "in_flight": in_flight,
        "age_seconds": age,
        "alert": alert,
        "agent_note": note,
        "phase": str(mirror.get("phase") or "") if mirror else None,
    }


def sync_desktop_mirror_from_main(repo: Path) -> dict[str, Any]:
    """Desktop: nudge mirror PR merges, pull main, refresh local VM phase mirror."""
    repo = repo.resolve()
    report: dict[str, Any] = {"action": "sync_desktop_mirror"}
    try:
        from scripts.ppe_operator_git_sync import check_and_nudge_merges, pull_main

        report["merge"] = check_and_nudge_merges(repo)
        report["pull"] = pull_main(repo)
    except Exception as exc:
        report["merge_pull_error"] = str(exc)
    report["refresh"] = refresh_vm_mirror_from_git(repo, force_fetch=True)
    mirror = load_vm_phase_mirror(repo)
    report["health"] = assess_mirror_health(mirror, local_verdict="RUN_LOCAL")
    pull = report.get("pull") if isinstance(report.get("pull"), dict) else {}
    if report.get("merge_pull_error"):
        report["ok"] = False
    elif pull.get("skipped"):
        report["ok"] = False
        report["pull_blocked"] = pull.get("reason") or pull.get("error") or "pull skipped"
    else:
        report["ok"] = bool(pull.get("ok"))
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(description="VM phase mirror refresh (desktop git pull path)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--sync-desktop", action="store_true", help="Merge mirror PRs, pull main, refresh local mirror")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.sync_desktop:
        report = sync_desktop_mirror_from_main(repo)
        if args.json:
            print(json.dumps(report, indent=2))
        elif not report.get("ok"):
            print(f"ppe_operator_vm_mirror_refresh: sync failed — {report.get('pull_blocked') or report.get('merge_pull_error')}")
        else:
            health = report.get("health") or {}
            print(
                f"ppe_operator_vm_mirror_refresh: ok phase={health.get('phase')} "
                f"untrusted={health.get('untrusted')} heartbeat_overdue={health.get('heartbeat_overdue')}"
            )
        return 0 if report.get("ok") else 1

    ap.error("specify --sync-desktop")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
