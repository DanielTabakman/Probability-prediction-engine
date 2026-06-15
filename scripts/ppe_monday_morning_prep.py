"""Monday morning prep — safe autoclean + easy autofix before the 8am report."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

PREP_LOG_REL = "artifacts/control_plane/MONDAY_MORNING_PREP_LATEST.json"


def _utc_now() -> str:
    from datetime import timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _report_hour() -> int:
    raw = os.environ.get("PPE_MONDAY_REPORT_HOUR", "8").strip()
    try:
        return max(0, min(23, int(raw)))
    except ValueError:
        return 8


def _report_minute() -> int:
    raw = os.environ.get("PPE_MONDAY_REPORT_MINUTE", "0").strip()
    try:
        return max(0, min(59, int(raw)))
    except ValueError:
        return 0


def wait_until_report_time(*, hour: int | None = None, minute: int | None = None) -> float:
    """Sleep until local report time; return seconds waited (0 if already past)."""
    target_h = _report_hour() if hour is None else hour
    target_m = _report_minute() if minute is None else minute
    now = datetime.now()
    target = now.replace(hour=target_h, minute=target_m, second=0, microsecond=0)
    if now >= target:
        return 0.0
    secs = (target - now).total_seconds()
    print(
        f"ppe_monday_morning_prep: waiting until {target_h:02d}:{target_m:02d} local "
        f"({secs / 60:.0f} min) before report",
        flush=True,
    )
    time.sleep(secs)
    return secs


def _record(step: str, result: Any, actions: list[dict[str, Any]]) -> None:
    entry: dict[str, Any] = {"step": step}
    if isinstance(result, dict):
        entry.update(result)
    else:
        entry["result"] = result
    actions.append(entry)


def run_monday_prep(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Safe autoclean and easy autofix — no product BUILD or steward API."""
    repo = repo.resolve()
    actions: list[dict[str, Any]] = []
    summary_parts: list[str] = []

    from scripts.ppe_workflow_radar import auto_cleanup_orphans

    cleanup = auto_cleanup_orphans(repo, dry_run=dry_run)
    if cleanup:
        summary_parts.append(f"{len(cleanup)} orphan cleanup(s)")
    _record("orphan_cleanup", {"count": len(cleanup), "actions": [a.to_dict() for a in cleanup]}, actions)

    if not dry_run:
        try:
            from scripts.ppe_manifest import load_manifest
            from scripts.ppe_preflight import maybe_clear_stale_active_run

            manifest = load_manifest(repo)
            cleared = maybe_clear_stale_active_run(repo, manifest)
            if cleared:
                summary_parts.append("cleared stale ACTIVE_RUN")
                _record("stale_active_run", {"cleared": cleared}, actions)
        except (ImportError, FileNotFoundError, json.JSONDecodeError) as exc:
            _record("stale_active_run", {"skipped": str(exc)}, actions)

    if not dry_run:
        try:
            from scripts.ppe_queue_health import run_queue_health

            qh = run_queue_health(repo, apply=True)
            if qh.get("fix_count"):
                summary_parts.append(f"{qh['fix_count']} queue repair(s)")
            _record("queue_health", qh, actions)
        except (ImportError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
            _record("queue_health", {"skipped": str(exc)}, actions)

    if not dry_run:
        try:
            from scripts.ppe_propagate_queue import maybe_propagate_queue

            prop = maybe_propagate_queue(repo, apply=True)
            if prop.get("applied"):
                summary_parts.append("backlog propagate")
            _record("propagate_queue", prop, actions)
        except ImportError as exc:
            _record("propagate_queue", {"skipped": str(exc)}, actions)

    if not dry_run:
        try:
            from scripts.ppe_post_build_watcher import try_finish_pending_ide_build

            finish = try_finish_pending_ide_build(repo)
            if finish.get("started"):
                summary_parts.append("post-build finish started")
            elif not finish.get("skipped"):
                _record("post_build_finish", finish, actions)
            else:
                _record("post_build_finish", finish, actions)
        except ImportError as exc:
            _record("post_build_finish", {"skipped": str(exc)}, actions)

    if not dry_run:
        try:
            from scripts.ppe_autobuilder import (
                PHASE_CLOSEOUT_PENDING,
                PHASE_STACK_DOWN,
                collect_autobuilder_status,
                action_ensure,
                action_finish_pending,
            )

            status = collect_autobuilder_status(repo)
            phase = str(status.get("phase") or "")
            if phase == PHASE_STACK_DOWN:
                out = action_ensure(repo)
                summary_parts.append("operator stack ensured")
                _record("autobuilder_ensure", out, actions)
            elif phase == PHASE_CLOSEOUT_PENDING:
                out = action_finish_pending(repo)
                summary_parts.append("closeout finish attempted")
                _record("autobuilder_finish", out, actions)
            else:
                _record("autobuilder", {"skipped": True, "phase": phase}, actions)
        except (ImportError, FileNotFoundError, OSError) as exc:
            _record("autobuilder", {"skipped": str(exc)}, actions)

    report = {
        "generated_at_utc": _utc_now(),
        "dry_run": dry_run,
        "summary": "; ".join(summary_parts) if summary_parts else "nothing to fix",
        "steps": actions,
    }
    if not dry_run:
        out = repo / PREP_LOG_REL
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def cmd_prep(repo: Path, *, dry_run: bool = False) -> int:
    report = run_monday_prep(repo, dry_run=dry_run)
    print(f"ppe_monday_morning_prep: {report['summary']}")
    return 0


def cmd_wait(repo: Path) -> int:
    _ = repo
    waited = wait_until_report_time()
    if waited <= 0:
        print("ppe_monday_morning_prep: report time already reached — continuing")
    else:
        print(f"ppe_monday_morning_prep: waited {waited / 60:.1f} min")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Monday morning prep (autoclean + easy autofix)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)

    p_prep = sub.add_parser("prep", help="Orphan cleanup + safe operator repairs")
    p_prep.add_argument("--dry-run", action="store_true")

    sub.add_parser("wait", help="Sleep until local report time (default 08:00)")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    try:
        from scripts.ppe_operator_config import apply_operator_env

        apply_operator_env(repo)
    except Exception:
        pass

    if args.command == "prep":
        return cmd_prep(repo, dry_run=args.dry_run)
    if args.command == "wait":
        return cmd_wait(repo)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
