"""Classify and safely clean Autobuilder-generated pull requests.

Dry-run is the default. `--apply` may close only exact duplicate head SHAs,
VM-mirror PRs, or timestamped loop-publish PRs whose changed files are entirely
runtime/control-state paths. Unique diffs are never auto-closed.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from scripts.ppe_chapter_publisher import AUTO_PR_PREFIXES, is_runtime_only_path


@dataclass
class Classification:
    number: int
    head: str
    head_sha: str
    url: str
    category: str
    safe_to_close: bool
    reason: str
    files: list[str]
    retained_number: int | None = None


def _run(argv: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)


def _gh_json(repo: Path, *args: str) -> Any:
    proc = _run(["gh", *args], cwd=repo)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "gh command failed").strip())
    return json.loads(proc.stdout or "null")


def list_open_prs(repo: Path) -> list[dict[str, Any]]:
    data = _gh_json(
        repo,
        "pr",
        "list",
        "--state",
        "open",
        "--limit",
        "500",
        "--json",
        "number,headRefName,headRefOid,createdAt,title,body,url",
    )
    return data if isinstance(data, list) else []


def changed_files(repo: Path, number: int) -> list[str]:
    data = _gh_json(repo, "pr", "view", str(number), "--json", "files")
    rows = data.get("files") if isinstance(data, dict) else []
    return [str(row.get("path") or "") for row in rows or [] if str(row.get("path") or "")]


def is_machine_pr(pr: dict[str, Any]) -> bool:
    head = str(pr.get("headRefName") or "")
    body = str(pr.get("body") or "")
    return head.startswith(AUTO_PR_PREFIXES) or "Auto-published" in body or "Auto-shipped" in body


def classify(prs: list[dict[str, Any]], file_map: dict[int, list[str]]) -> list[Classification]:
    by_sha: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pr in prs:
        sha = str(pr.get("headRefOid") or "")
        if sha:
            by_sha[sha].append(pr)

    duplicate_retained: dict[int, int] = {}
    for rows in by_sha.values():
        if len(rows) < 2:
            continue
        ordered = sorted(rows, key=lambda row: int(row.get("number") or 0), reverse=True)
        retained = int(ordered[0].get("number") or 0)
        for row in ordered[1:]:
            duplicate_retained[int(row.get("number") or 0)] = retained

    results: list[Classification] = []
    for pr in prs:
        number = int(pr.get("number") or 0)
        head = str(pr.get("headRefName") or "")
        sha = str(pr.get("headRefOid") or "")
        files = file_map.get(number, [])
        url = str(pr.get("url") or "")

        if number in duplicate_retained:
            results.append(
                Classification(
                    number,
                    head,
                    sha,
                    url,
                    "duplicate_head_sha",
                    True,
                    "same head SHA is represented by a newer open PR",
                    files,
                    duplicate_retained[number],
                )
            )
            continue

        if head.startswith("ops/vm-mirror-"):
            results.append(
                Classification(number, head, sha, url, "vm_mirror", True, "runtime mirror PR", files)
            )
            continue

        if head.startswith("ops/loop-publish-") or head.startswith("ops/closeout-"):
            if files and all(is_runtime_only_path(path) for path in files):
                results.append(
                    Classification(
                        number,
                        head,
                        sha,
                        url,
                        "runtime_only_timestamp_branch",
                        True,
                        "timestamped PR contains only runtime/control-state files",
                        files,
                    )
                )
            else:
                results.append(
                    Classification(
                        number,
                        head,
                        sha,
                        url,
                        "unique_or_mixed_timestamp_branch",
                        False,
                        "contains durable or unknown changes; reconcile manually",
                        files,
                    )
                )
            continue

        results.append(
            Classification(number, head, sha, url, "non_machine_or_unique", False, "not safe for automatic cleanup", files)
        )
    return results


def close_pr(repo: Path, row: Classification, *, delete_branch: bool) -> dict[str, Any]:
    comment = (
        "Auto-closed by `ppe_autobuilder_pr_cleanup.py`: "
        f"{row.reason}. Durable/unique work is not auto-closed."
    )
    proc = _run(["gh", "pr", "close", str(row.number), "--comment", comment], cwd=repo)
    if proc.returncode != 0:
        return {"number": row.number, "ok": False, "error": (proc.stderr or proc.stdout).strip()}
    deleted = False
    if delete_branch and row.head:
        delete = _run(["git", "push", "origin", "--delete", row.head], cwd=repo)
        deleted = delete.returncode == 0
    return {"number": row.number, "ok": True, "branch_deleted": deleted}


def run_cleanup(repo: Path, *, apply: bool = False, delete_branches: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    prs = [pr for pr in list_open_prs(repo) if is_machine_pr(pr)]
    file_map: dict[int, list[str]] = {}
    for pr in prs:
        number = int(pr.get("number") or 0)
        try:
            file_map[number] = changed_files(repo, number)
        except RuntimeError:
            file_map[number] = []
    rows = classify(prs, file_map)
    actions: list[dict[str, Any]] = []
    if apply:
        for row in rows:
            if row.safe_to_close:
                actions.append(close_pr(repo, row, delete_branch=delete_branches))
    return {
        "ok": all(action.get("ok") for action in actions) if actions else True,
        "dry_run": not apply,
        "counts": {
            "machine_prs": len(rows),
            "safe_to_close": sum(1 for row in rows if row.safe_to_close),
            "manual_reconciliation": sum(1 for row in rows if not row.safe_to_close),
        },
        "classifications": [asdict(row) for row in rows],
        "actions": actions,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--delete-branches", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_cleanup(Path(args.repo), apply=args.apply, delete_branches=args.delete_branches)
    except (RuntimeError, json.JSONDecodeError) as exc:
        result = {"ok": False, "reason": str(exc)}
    print(json.dumps(result, indent=2) if args.json else result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
