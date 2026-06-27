"""Retarget stacked GitHub PRs to main after a parent slice merges.

Used by:
- `.github/workflows/retarget-stacked-prs.yml` (on parent merge to main)
- `ppe_operator_git_sync.py` (periodic scan when desktop loop runs)
- Laptop operators: `python scripts/retarget_stacked_prs.py --scan`

Canon: docs/SOP/GITHUB_ZERO_TOUCH_MERGE.md § Stacked PRs
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

DEFAULT_MAIN = "main"


def _gh_available() -> bool:
    try:
        proc = subprocess.run(["gh", "--version"], capture_output=True, text=True, check=False)
        return proc.returncode == 0
    except FileNotFoundError:
        return False


def gh_json(repo: Path, args: list[str]) -> Any | None:
    if not _gh_available():
        return None
    proc = subprocess.run(args, cwd=repo, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def find_merged_pr_to_main(
    repo: Path,
    parent_branch: str,
    *,
    main: str = DEFAULT_MAIN,
) -> dict[str, Any] | None:
    """Return the most recent merged PR from parent_branch -> main, if any."""
    branch = parent_branch.strip()
    if not branch or branch == main:
        return None
    rows = gh_json(
        repo,
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--base",
            main,
            "--head",
            branch,
            "--limit",
            "1",
            "--json",
            "number,title,mergedAt,url",
        ],
    )
    if not rows or not isinstance(rows, list):
        return None
    row = rows[0]
    return row if isinstance(row, dict) else None


def list_open_prs_with_base(repo: Path, base_branch: str) -> list[dict[str, Any]]:
    base = base_branch.strip()
    rows = gh_json(
        repo,
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--base",
            base,
            "--limit",
            "50",
            "--json",
            "number,baseRefName,headRefName,url,isDraft",
        ],
    )
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict)]


def list_open_prs_not_on_main(repo: Path, *, main: str = DEFAULT_MAIN) -> list[dict[str, Any]]:
    rows = gh_json(
        repo,
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,baseRefName,headRefName,url,isDraft",
        ],
    )
    if not isinstance(rows, list):
        return []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("baseRefName") or "") == main:
            continue
        out.append(row)
    return out


def _comment_body(*, parent_branch: str, merged_pr: int | None, main: str) -> str:
    merged = f"#{merged_pr}" if merged_pr else "to `main`"
    return (
        f"Retargeted base to `{main}` after parent branch `{parent_branch}` merged {merged}. "
        "CI will re-run; merge-on-green applies when checks pass and the `automerge` label is present."
    )


def retarget_pull_request(
    repo: Path,
    pr_number: int,
    *,
    main: str = DEFAULT_MAIN,
    parent_branch: str | None = None,
    merged_pr: int | None = None,
    dry_run: bool = False,
    try_update_branch: bool = True,
) -> dict[str, Any]:
    """Point an open PR at main and optionally refresh its branch from base."""
    result: dict[str, Any] = {
        "number": pr_number,
        "ok": False,
        "dry_run": dry_run,
        "main": main,
    }
    if dry_run:
        result["ok"] = True
        result["action"] = "would_retarget"
        return result

    edit = subprocess.run(
        ["gh", "pr", "edit", str(pr_number), "--base", main],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if edit.returncode != 0:
        result["error"] = (edit.stderr or edit.stdout or "gh pr edit failed").strip()
        return result

    result["retargeted"] = True
    if parent_branch:
        comment = subprocess.run(
            ["gh", "pr", "comment", str(pr_number), "--body", _comment_body(
                parent_branch=parent_branch,
                merged_pr=merged_pr,
                main=main,
            )],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if comment.returncode != 0:
            result["comment_warning"] = (comment.stderr or comment.stdout or "comment failed").strip()

    if try_update_branch:
        update = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/update-branch",
                "-X",
                "PUT",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if update.returncode == 0:
            result["branch_updated"] = True
        else:
            result["branch_update_skipped"] = (update.stderr or update.stdout or "update-branch failed").strip()

    result["ok"] = True
    return result


def retarget_children_of_branch(
    repo: Path,
    parent_branch: str,
    *,
    main: str = DEFAULT_MAIN,
    merged_pr: int | None = None,
    dry_run: bool = False,
    try_update_branch: bool = True,
    list_children: Callable[[Path, str], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Retarget every open PR whose base is parent_branch."""
    parent = parent_branch.strip()
    if not parent or parent == main:
        return {
            "action": "retarget_children",
            "ok": True,
            "skipped": True,
            "reason": "parent is main or empty",
            "retargeted": [],
        }

    list_fn = list_children or list_open_prs_with_base
    children = list_fn(repo, parent)
    retargeted: list[dict[str, Any]] = []
    for child in children:
        if child.get("isDraft"):
            retargeted.append(
                {
                    "number": child.get("number"),
                    "ok": False,
                    "skipped": True,
                    "reason": "draft",
                }
            )
            continue
        num = child.get("number")
        if num is None:
            continue
        retargeted.append(
            retarget_pull_request(
                repo,
                int(num),
                main=main,
                parent_branch=parent,
                merged_pr=merged_pr,
                dry_run=dry_run,
                try_update_branch=try_update_branch,
            )
        )

    ok = all(r.get("ok") or r.get("skipped") for r in retargeted) if retargeted else True
    return {
        "action": "retarget_children",
        "ok": ok,
        "parent_branch": parent,
        "merged_pr": merged_pr,
        "retargeted": retargeted,
    }


def scan_and_retarget_stacked_prs(
    repo: Path,
    *,
    main: str = DEFAULT_MAIN,
    dry_run: bool = False,
    try_update_branch: bool = True,
) -> dict[str, Any]:
    """Retarget any open PR stacked on a branch that already merged to main."""
    repo = repo.resolve()
    if not _gh_available():
        return {"action": "scan_retarget", "ok": False, "error": "gh not available"}

    stacked = list_open_prs_not_on_main(repo, main=main)
    if not stacked:
        return {"action": "scan_retarget", "ok": True, "retargeted": [], "scanned": 0}

    by_parent: dict[str, list[dict[str, Any]]] = {}
    for pr in stacked:
        base = str(pr.get("baseRefName") or "").strip()
        if not base:
            continue
        by_parent.setdefault(base, []).append(pr)

    results: list[dict[str, Any]] = []
    for parent, _children in sorted(by_parent.items()):
        merged = find_merged_pr_to_main(repo, parent, main=main)
        if not merged:
            results.append(
                {
                    "parent_branch": parent,
                    "ok": True,
                    "skipped": True,
                    "reason": "parent not merged to main",
                }
            )
            continue
        merged_num = merged.get("number")
        results.append(
            retarget_children_of_branch(
                repo,
                parent,
                main=main,
                merged_pr=int(merged_num) if merged_num is not None else None,
                dry_run=dry_run,
                try_update_branch=try_update_branch,
            )
        )

    ok = all(r.get("ok") for r in results)
    return {
        "action": "scan_retarget",
        "ok": ok,
        "scanned_parents": len(by_parent),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Retarget stacked PRs to main after parent merge")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--main", default=DEFAULT_MAIN, help="Target base branch (default: main)")
    ap.add_argument("--parent-branch", default="", help="Parent branch that just merged")
    ap.add_argument("--merged-pr", type=int, default=0, help="Merged parent PR number (for comment)")
    ap.add_argument("--scan", action="store_true", help="Scan all open stacked PRs")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-update-branch", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    try_update = not args.no_update_branch

    if args.scan:
        report = scan_and_retarget_stacked_prs(
            repo,
            main=args.main,
            dry_run=args.dry_run,
            try_update_branch=try_update,
        )
    elif args.parent_branch.strip():
        report = retarget_children_of_branch(
            repo,
            args.parent_branch.strip(),
            main=args.main,
            merged_pr=args.merged_pr or None,
            dry_run=args.dry_run,
            try_update_branch=try_update,
        )
    else:
        ap.error("Provide --parent-branch or --scan")

    print(json.dumps(report, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
