"""Assess local runtime VM phase state without using Git as a transport.

The historical API names remain for compatibility, but refresh/sync no longer
fetch, merge, pull, or read phase state from Git. Direct loop-host status/SSH is
authoritative; this module reads the gitignored runtime artifact when present.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_vm_phase_mirror import (
    IN_FLIGHT_PHASES,
    MIRROR_HEARTBEAT_PUBLISH_SECONDS,
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


def maybe_fetch_origin_main(repo: Path, *, force: bool = False) -> dict[str, Any]:
    """Compatibility shim: runtime phase state is never fetched from Git."""
    del repo, force
    return {"fetched": False, "skipped": True, "reason": "runtime_state_not_in_git"}


def read_mirror_from_git_ref(repo: Path, ref: str = "origin/main") -> dict[str, Any] | None:
    """Compatibility shim retained for callers during migration."""
    del repo, ref
    return None


def refresh_vm_mirror_from_git(
    repo: Path,
    *,
    force_fetch: bool = False,
    stale_seconds: int = MIRROR_STALE_SECONDS,
) -> dict[str, Any]:
    """Read and assess the local runtime artifact; never mutate it from Git."""
    del force_fetch
    repo = repo.resolve()
    local = load_vm_phase_mirror(repo)
    report: dict[str, Any] = {
        "local_populated": mirror_is_populated(local),
        "local_stale": mirror_is_stale(local, stale_seconds=stale_seconds),
        "local_age_s": mirror_age_seconds(local),
        "path": str(mirror_path(repo)),
        "transport": "runtime_local",
    }
    report["action"] = "runtime_local" if mirror_is_populated(local) else "runtime_state_missing"
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
        note = "VM runtime state missing — query the loop host through direct status/SSH."
    elif untrusted:
        alert = local_verdict in ("RUN_LOCAL", "IDE_BUILD")
        mins = int((age or 0) // 60)
        note = f"VM runtime state stale ({mins}m old) — query direct status/SSH before trusting phase."
    elif heartbeat_overdue:
        alert = local_verdict in ("RUN_LOCAL", "IDE_BUILD")
        mins = int((age or 0) // 60)
        note = f"VM in-flight runtime heartbeat overdue ({mins}m) — inspect the loop host directly."
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
        "transport": "runtime_local",
    }


def sync_desktop_mirror_from_main(repo: Path) -> dict[str, Any]:
    """Compatibility entrypoint: assess runtime state without Git operations."""
    repo = repo.resolve()
    refresh = refresh_vm_mirror_from_git(repo)
    mirror = load_vm_phase_mirror(repo)
    health = assess_mirror_health(mirror, local_verdict="RUN_LOCAL")
    return {
        "action": "assess_runtime_state",
        "refresh": refresh,
        "health": health,
        "ok": bool(health.get("populated")),
        "transport": "runtime_local",
    }


def maybe_sync_desktop_mirror_after_ship(repo: Path, *, pre_push: bool = False) -> dict[str, Any]:
    """Post-ship Git synchronization is obsolete for runtime phase state."""
    del repo
    if not pre_push:
        return {"skipped": True, "reason": "not_post_ship"}
    if os.environ.get("PPE_MIRROR_SYNC_AFTER_SHIP", "1").strip().lower() in ("0", "false", "no"):
        return {"skipped": True, "reason": "disabled"}
    return {"skipped": True, "reason": "runtime_state_not_in_git"}


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(description="Assess local VM runtime phase state")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--sync-desktop", action="store_true", help="Compatibility alias: assess runtime state")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.sync_desktop:
        report = sync_desktop_mirror_from_main(repo)
        if args.json:
            print(json.dumps(report, indent=2))
        elif not report.get("ok"):
            print("ppe_operator_vm_mirror_refresh: runtime state unavailable — use direct status/SSH")
        elif not args.quiet:
            health = report.get("health") or {}
            print(
                f"ppe_operator_vm_mirror_refresh: phase={health.get('phase')} "
                f"untrusted={health.get('untrusted')} heartbeat_overdue={health.get('heartbeat_overdue')}"
            )
        return 0 if report.get("ok") else 1

    ap.error("specify --sync-desktop")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
