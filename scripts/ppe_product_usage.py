"""Read MSOS product usage JSONL and summarize for operator tracking."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRODUCT_USAGE_FILENAME = "ppe_product_usage.jsonl"
DEFAULT_REL = Path("data") / PRODUCT_USAGE_FILENAME


def resolve_usage_path(repo: Path) -> Path:
    raw = (os.environ.get("PPE_PRODUCT_USAGE_JSONL") or os.environ.get("PPE_PRODUCT_USAGE_DIR") or "").strip()
    if raw:
        p = Path(raw).expanduser()
        if p.is_dir():
            return p / PRODUCT_USAGE_FILENAME
        return p
    return repo / DEFAULT_REL


def pull_usage_from_container(
    repo: Path,
    *,
    container: str = "msos_web",
    dest: Path | None = None,
) -> Path:
    """Copy product usage JSONL from a running MSOS web container (VPS docker)."""
    target = dest or (repo / DEFAULT_REL)
    target.parent.mkdir(parents=True, exist_ok=True)
    remote = f"{container}:/data/{PRODUCT_USAGE_FILENAME}"
    proc = subprocess.run(
        ["docker", "cp", remote, str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "docker cp failed").strip()
        raise RuntimeError(f"pull failed ({remote} -> {target}): {err}")
    return target


def read_usage_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _parse_iso(ts: str) -> datetime | None:
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def events_in_days(rows: list[dict[str, Any]], days: int) -> list[dict[str, Any]]:
    if days <= 0:
        return rows
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    out: list[dict[str, Any]] = []
    for row in rows:
        ts = str(row.get("created_at_utc") or row.get("timestamp") or "")
        dt = _parse_iso(ts)
        if dt and dt.timestamp() >= cutoff:
            out.append(row)
    return out


def summarize_usage(repo: Path, *, days: int = 7) -> dict[str, Any]:
    path = resolve_usage_path(repo)
    rows = events_in_days(read_usage_events(path), days)
    by_event: Counter[str] = Counter()
    users: set[str] = set()
    for row in rows:
        name = str(row.get("event_name") or row.get("event") or "").strip()
        if name:
            by_event[name] += 1
        email = str(row.get("owner_email") or row.get("user_id") or "").strip().lower()
        if email:
            users.add(email)
    top = by_event.most_common(1)[0][0] if by_event else None
    return {
        "path": str(path),
        "exists": path.is_file(),
        "days": days,
        "total_events": len(rows),
        "unique_users": len(users),
        "by_event": dict(by_event.most_common(10)),
        "top_event": top,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Summarize MSOS product usage JSONL.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--pull-from-docker",
        nargs="?",
        const="msos_web",
        metavar="CONTAINER",
        help="Copy JSONL from docker container (default: msos_web) before summarize",
    )
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if args.pull_from_docker is not None:
        try:
            dest = pull_usage_from_container(repo, container=args.pull_from_docker)
            print(f"ppe_product_usage: pulled {dest} from {args.pull_from_docker}", file=sys.stderr)
        except RuntimeError as exc:
            print(f"ppe_product_usage: {exc}", file=sys.stderr)
            return 1
    summary = summarize_usage(repo, days=args.days)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            f"ppe_product_usage: events={summary['total_events']} users={summary['unique_users']} "
            f"path={summary['path']}"
        )
        if summary.get("by_event"):
            print(f"  by_event: {summary['by_event']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
