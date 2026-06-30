"""Research archive depth counters for collectors in the pipeline registry."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research_pipeline_registry import collectors  # noqa: E402

DAY_DIR = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEALTH_JSON_REL = "artifacts/control_plane/RESEARCH_ARCHIVE_HEALTH.json"
DEFAULT_STALE_HOURS = 36


def _latest_snapshot(root: Path, file_glob: str) -> tuple[str | None, str | None, float | None]:
    latest_mtime: float | None = None
    latest_rel: str | None = None
    for path in root.glob(file_glob):
        if not path.is_file():
            continue
        mtime = path.stat().st_mtime
        if latest_mtime is None or mtime > latest_mtime:
            latest_mtime = mtime
            latest_rel = str(path)
    if latest_mtime is None:
        return None, None, None
    iso = (
        datetime.fromtimestamp(latest_mtime, tz=UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    return iso, latest_rel, latest_mtime


def _calendar_days(root: Path) -> set[str]:
    days: set[str] = set()
    if not root.is_dir():
        return days
    for path in root.iterdir():
        if path.is_dir() and DAY_DIR.match(path.name):
            days.add(path.name)
    return days


def _count_files(root: Path, file_glob: str) -> int:
    if not root.is_dir():
        return 0
    return sum(1 for _ in root.glob(file_glob))


def collector_health(repo: Path, spec: dict[str, Any]) -> dict[str, Any]:
    archive_rel = str(spec.get("archive_root") or "")
    root = repo / archive_rel
    file_glob = str(spec.get("file_glob") or "**/*")
    min_days = int(spec.get("min_calendar_days") or 0)
    stale_hours = float(spec.get("stale_hours") or DEFAULT_STALE_HOURS)
    days = _calendar_days(root)
    have = len(days)
    ready = have >= min_days if min_days > 0 else have > 0
    last_utc, last_path, last_mtime = _latest_snapshot(root, file_glob)
    hours_since: float | None = None
    stale = False
    if last_mtime is not None:
        hours_since = round((datetime.now(tz=UTC).timestamp() - last_mtime) / 3600.0, 2)
        stale = hours_since > stale_hours
    elif min_days > 0:
        stale = True
    return {
        "id": str(spec.get("id") or ""),
        "label": str(spec.get("label") or spec.get("id") or ""),
        "archive_root": archive_rel,
        "calendar_days": have,
        "min_calendar_days": min_days,
        "file_count": _count_files(root, file_glob),
        "ready": ready,
        "latest_day": max(days) if days else None,
        "last_snapshot_utc": last_utc,
        "last_snapshot_path": last_path,
        "hours_since_snapshot": hours_since,
        "stale_hours": stale_hours,
        "stale": stale,
    }


def build_archive_health(repo: Path) -> dict[str, Any]:
    try:
        specs = collectors(repo)
    except FileNotFoundError:
        specs = []
    items = [collector_health(repo, spec) for spec in specs]
    return {
        "version": 1,
        "as_of_utc": datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "collectors": items,
    }


def _console_safe(text: str) -> str:
    """Avoid Windows cp1252 console crashes on registry labels with ↔."""
    return text.replace("\u2194", "<->")


def format_health_line(item: dict[str, Any]) -> str:
    have = int(item.get("calendar_days") or 0)
    need = int(item.get("min_calendar_days") or 0)
    label = _console_safe(str(item.get("label") or item.get("id") or "collector"))
    tail = " - STALE" if item.get("stale") else ""
    if not item.get("stale") and item.get("last_snapshot_utc"):
        tail = f" - last {item.get('last_snapshot_utc')}"
    return f"{label}: {have}/{need} days{tail}"


def write_archive_health(repo: Path) -> Path:
    payload = build_archive_health(repo)
    out = repo / HEALTH_JSON_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Research archive depth counters")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--write", action="store_true", help="Write artifacts/control_plane/RESEARCH_ARCHIVE_HEALTH.json")
    ap.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    payload = build_archive_health(repo)
    if args.write:
        write_archive_health(repo)
    if args.json or not args.write:
        print(json.dumps(payload, indent=2))
    elif args.write:
        for item in payload.get("collectors") or []:
            print(format_health_line(item))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
