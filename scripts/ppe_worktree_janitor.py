"""Report (and optionally remove) stale git worktrees — human approves, not relay."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_REL = "artifacts/control_plane/WORKTREE_JANITOR_REPORT.json"
SAFE_PREFIXES = ("_worktrees/",)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_worktree_list(stdout: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in stdout.splitlines():
        if not line.strip():
            if current:
                entries.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            current["path"] = line[9:].strip()
        elif line.startswith("HEAD "):
            current["head"] = line[5:].strip()
        elif line.startswith("branch "):
            current["branch"] = line[7:].strip().replace("refs/heads/", "")
        elif line == "detached":
            current["detached"] = "true"
        elif line == "bare":
            current["bare"] = "true"
    if current:
        entries.append(current)
    return entries


def _repo_rel_path(repo: Path, worktree_path: str) -> str:
    try:
        wt = Path(worktree_path).resolve()
        rel = wt.relative_to(repo.resolve())
        return rel.as_posix()
    except ValueError:
        return worktree_path.replace("\\", "/")


def assess_worktrees(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    proc = _git(repo, "worktree", "list", "--porcelain")
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or "git worktree list failed").strip()}

    main_proc = _git(repo, "rev-parse", "--show-toplevel")
    main_root = (main_proc.stdout or "").strip()
    entries = _parse_worktree_list(proc.stdout or "")
    candidates: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []

    for entry in entries:
        path = str(entry.get("path") or "")
        if not path:
            continue
        rel = _repo_rel_path(repo, path)
        is_main = path.replace("\\", "/") == main_root.replace("\\", "/")
        branch = str(entry.get("branch") or "")
        item = {
            "path": path,
            "rel": rel,
            "branch": branch or "(detached)",
            "head": entry.get("head"),
            "is_main": is_main,
        }
        if is_main:
            kept.append({**item, "reason": "main worktree"})
            continue
        if any(rel.startswith(prefix) for prefix in SAFE_PREFIXES):
            candidates.append({**item, "safe_to_remove": True, "reason": "under _worktrees/"})
        elif branch.startswith(("product/", "build/")):
            candidates.append({**item, "safe_to_remove": False, "reason": "product/build branch — review first"})
        else:
            candidates.append({**item, "safe_to_remove": False, "reason": "outside _worktrees — review first"})

    return {
        "ok": True,
        "as_of": _utc_now(),
        "candidates": candidates,
        "kept": kept,
        "safe_count": sum(1 for c in candidates if c.get("safe_to_remove")),
    }


def format_report(payload: dict[str, Any]) -> str:
    lines = ["Worktree janitor report", ""]
    if not payload.get("ok"):
        lines.append(f"ERROR: {payload.get('error')}")
        return "\n".join(lines)
    safe = [c for c in payload.get("candidates") or [] if c.get("safe_to_remove")]
    review = [c for c in payload.get("candidates") or [] if not c.get("safe_to_remove")]
    lines.append(f"Safe to remove ({len(safe)}):")
    if safe:
        for item in safe[:20]:
            lines.append(f"  - {item.get('rel')} [{item.get('branch')}]")
    else:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"Review first ({len(review)}):")
    if review:
        for item in review[:10]:
            lines.append(f"  - {item.get('rel')} [{item.get('branch')}] — {item.get('reason')}")
    else:
        lines.append("  (none)")
    lines.append("")
    lines.append("Remove one: python scripts/ppe_worktree_janitor.py --remove <rel-path>")
    return "\n".join(lines)


def remove_worktree(repo: Path, rel_path: str) -> dict[str, Any]:
    repo = repo.resolve()
    rel = rel_path.replace("\\", "/").strip().lstrip("/")
    if not rel.startswith("_worktrees/"):
        return {"ok": False, "error": "only _worktrees/* paths allowed without --force"}
    target = (repo / rel).resolve()
    if not target.is_dir():
        return {"ok": False, "error": f"not found: {rel}"}
    proc = _git(repo, "worktree", "remove", "--force", str(target))
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout or "git worktree remove failed").strip()}
    return {"ok": True, "removed": rel}


def write_report(repo: Path, payload: dict[str, Any]) -> Path:
    path = repo / REPORT_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="List stale git worktrees (human approves removal)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help="Write WORKTREE_JANITOR_REPORT.json")
    ap.add_argument("--remove", metavar="REL", help="Remove one _worktrees/ path (e.g. _worktrees/foo)")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    if args.remove:
        result = remove_worktree(repo, args.remove)
        print(json.dumps(result, indent=2) if args.json else result)
        return 0 if result.get("ok") else 1

    payload = assess_worktrees(repo)
    if args.write:
        write_report(repo, payload)
    text = json.dumps(payload, indent=2) if args.json else format_report(payload)
    print(text)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
