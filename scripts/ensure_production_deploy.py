#!/usr/bin/env python3
"""Ensure production VPS deploy runs for the current origin/main HEAD.

Used by agents after PR merge so marketstructureos.com is not left on an old
image when Deploy VPS witness flakes or a push-triggered run was cancelled.

Usage:
  python scripts/ensure_production_deploy.py --trigger --wait
  python scripts/ensure_production_deploy.py --wait --sha abc1234
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from typing import Any

WORKFLOW_FILE = "deploy-vps.yml"
DEFAULT_BRANCH = "main"
DEFAULT_TIMEOUT_S = 1200
POLL_INTERVAL_S = 15


def _run(cmd: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def resolve_main_sha(explicit: str | None) -> str | None:
    if explicit:
        return explicit.strip()
    proc = _run(["git", "rev-parse", f"origin/{DEFAULT_BRANCH}"])
    if proc.returncode != 0:
        print(proc.stderr or "git rev-parse origin/main failed", file=sys.stderr)
        return None
    return proc.stdout.strip()


def list_deploy_runs(limit: int = 10) -> list[dict[str, Any]]:
    proc = _run(
        [
            "gh",
            "run",
            "list",
            f"--workflow={WORKFLOW_FILE}",
            f"--branch={DEFAULT_BRANCH}",
            f"--limit={limit}",
            "--json",
            "databaseId,headSha,status,conclusion,url,displayTitle,createdAt",
        ]
    )
    if proc.returncode != 0:
        print(proc.stderr or "gh run list failed", file=sys.stderr)
        return []
    return json.loads(proc.stdout or "[]")


def find_run_for_sha(runs: list[dict[str, Any]], sha: str) -> dict[str, Any] | None:
    for row in runs:
        if str(row.get("headSha") or "") == sha:
            return row
    return None


def trigger_deploy() -> bool:
    proc = _run(["gh", "workflow", "run", WORKFLOW_FILE, "--ref", DEFAULT_BRANCH])
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout or "gh workflow run failed", file=sys.stderr)
        return False
    return True


def wait_for_run(run_id: str, *, timeout_s: int) -> tuple[bool, str]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        proc = _run(
            [
                "gh",
                "run",
                "view",
                run_id,
                "--json",
                "status,conclusion,url",
            ]
        )
        if proc.returncode != 0:
            time.sleep(POLL_INTERVAL_S)
            continue
        row = json.loads(proc.stdout)
        status = str(row.get("status") or "")
        conclusion = row.get("conclusion")
        url = str(row.get("url") or "")
        if status in ("queued", "in_progress", "waiting", "pending"):
            time.sleep(POLL_INTERVAL_S)
            continue
        if conclusion == "success":
            return True, url
        return False, url or f"run {run_id} ended with {conclusion!r}"
    return False, f"timed out after {timeout_s}s waiting for run {run_id}"


def newest_run_id_after_dispatch(before_ids: set[str], *, attempts: int = 12) -> str | None:
    for _ in range(attempts):
        runs = list_deploy_runs(limit=5)
        for row in runs:
            rid = str(row.get("databaseId") or "")
            if rid and rid not in before_ids:
                return rid
        time.sleep(5)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure Deploy VPS ran for origin/main HEAD")
    parser.add_argument("--sha", help="Expected main commit (default: origin/main)")
    parser.add_argument("--trigger", action="store_true", help="Dispatch deploy when HEAD not yet deployed")
    parser.add_argument("--wait", action="store_true", help="Wait for deploy workflow to finish")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    args = parser.parse_args()

    sha = resolve_main_sha(args.sha)
    if not sha:
        return 2

    runs = list_deploy_runs()
    match = find_run_for_sha(runs, sha)
    if match and match.get("conclusion") == "success":
        print(f"Deploy VPS already succeeded for {sha[:7]} — {match.get('url')}")
        return 0
    if match and match.get("status") in ("queued", "in_progress", "waiting", "pending"):
        run_id = str(match["databaseId"])
        print(f"Deploy VPS already in progress for {sha[:7]} — {match.get('url')}")
        if args.wait:
            ok, detail = wait_for_run(run_id, timeout_s=args.timeout)
            print(detail)
            return 0 if ok else 1
        return 0

    if not args.trigger:
        print(
            f"No successful Deploy VPS for {sha[:7]}. Re-run with --trigger (and optionally --wait).",
            file=sys.stderr,
        )
        return 1

    before_ids = {str(r.get("databaseId") or "") for r in runs}
    if not trigger_deploy():
        return 1
    print(f"Dispatched Deploy VPS for {DEFAULT_BRANCH} @ {sha[:7]}")

    run_id = newest_run_id_after_dispatch(before_ids)
    if not run_id:
        print("Could not resolve new workflow run id after dispatch", file=sys.stderr)
        return 1

    if not args.wait:
        proc = _run(["gh", "run", "view", run_id, "--json", "url"])
        url = ""
        if proc.returncode == 0:
            url = json.loads(proc.stdout).get("url") or ""
        print(url or f"run id {run_id}")
        return 0

    ok, detail = wait_for_run(run_id, timeout_s=args.timeout)
    print(detail)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
