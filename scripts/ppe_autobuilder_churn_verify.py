"""Verify that Autobuilder GitHub churn has stopped for an observation window."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_chapter_publisher import AUTO_PR_PREFIXES


def _run(argv: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)


def _parse_time(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def is_churn_pr(pr: dict[str, Any]) -> bool:
    head = str(pr.get("headRefName") or "")
    body = str(pr.get("body") or "")
    return head.startswith(AUTO_PR_PREFIXES) or "Auto-published VM phase mirror" in body


def verify(repo: Path, *, hours: float = 24.0, now: datetime | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=max(0.0, hours))
    proc = _run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "all",
            "--limit",
            "500",
            "--json",
            "number,headRefName,createdAt,title,body,url,state",
        ],
        cwd=repo,
    )
    if proc.returncode != 0:
        return {"ok": False, "reason": (proc.stderr or proc.stdout or "gh pr list failed").strip()}
    rows = json.loads(proc.stdout or "[]")
    churn: list[dict[str, Any]] = []
    for pr in rows if isinstance(rows, list) else []:
        created = _parse_time(str(pr.get("createdAt") or ""))
        if created and created >= cutoff and is_churn_pr(pr):
            churn.append(pr)

    tracked = _run(["git", "status", "--porcelain", "--", "docs/SOP/VM_OPERATOR_PHASE.json"], cwd=repo)
    tracked_dirty = bool((tracked.stdout or "").strip())
    return {
        "ok": not churn and not tracked_dirty,
        "hours": hours,
        "cutoff": cutoff.isoformat(),
        "churn_pr_count": len(churn),
        "churn_prs": churn,
        "tracked_runtime_mirror_dirty": tracked_dirty,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--hours", type=float, default=24.0)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = verify(Path(args.repo), hours=args.hours)
    except (json.JSONDecodeError, OSError) as exc:
        result = {"ok": False, "reason": str(exc)}
    print(json.dumps(result, indent=2) if args.json else result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
