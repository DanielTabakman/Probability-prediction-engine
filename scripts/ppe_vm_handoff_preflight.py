"""VM loop-host git preflight before finish_ide_build (DESKTOP_CONTINUE / SSH handoff)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _legacy_prepare(repo: Path) -> dict[str, Any]:
    """Minimal handoff when ppe_operator_git_sync is missing or too old."""
    repo = repo.resolve()
    changes: list[str] = []
    git_dir = repo / ".git"
    if (git_dir / "MERGE_HEAD").is_file():
        _git(repo, "merge", "--abort")
        changes.append("merge --abort")

    fetch = _git(repo, "fetch", "origin")
    if fetch.returncode != 0:
        return {
            "action": "legacy_prepare",
            "ok": False,
            "error": (fetch.stderr or fetch.stdout or "git fetch failed").strip(),
            "changes": changes,
        }

    branch_proc = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    branch = (branch_proc.stdout or "").strip() or "main"
    for rel in ("docs/SOP/PHASE_QUEUE.json", "docs/SOP/ACTIVE_PHASE_MANIFEST.json"):
        proc = _git(repo, "checkout", "origin/main", "--", rel)
        if proc.returncode == 0:
            changes.append(f"reset {rel}")

    if branch.startswith("build/") or branch.startswith("build/auto/"):
        co = _git(repo, "checkout", "-f", "main")
        if co.returncode != 0:
            co = _git(repo, "checkout", "main")
        if co.returncode == 0:
            changes.append("checkout main")
        hard = _git(repo, "reset", "--hard", "origin/main")
        ok_reset = hard.returncode == 0
        if ok_reset:
            changes.append("reset --hard origin/main")
        if not ok_reset:
            return {
                "action": "legacy_prepare",
                "ok": False,
                "error": (hard.stderr or hard.stdout or "reset failed").strip(),
                "changes": changes,
            }
    else:
        pull = _git(repo, "pull", "--ff-only", "origin", "main")
        if pull.returncode != 0:
            hard = _git(repo, "reset", "--hard", "origin/main")
            if hard.returncode != 0:
                return {
                    "action": "legacy_prepare",
                    "ok": False,
                    "error": (pull.stderr or pull.stdout or "pull failed").strip(),
                    "changes": changes,
                }
            changes.append("reset --hard origin/main (after ff-only failed)")
        else:
            changes.append("pull --ff-only origin main")

    return {"action": "legacy_prepare", "ok": True, "changes": changes, "branch": branch}


def prepare_vm_handoff(repo: Path) -> dict[str, Any]:
    """Prepare loop-host git state; uses git_sync when available, else legacy git steps."""
    repo = repo.resolve()
    try:
        from scripts.ppe_operator_git_sync import prepare_loop_host_for_handoff

        return prepare_loop_host_for_handoff(repo)
    except ImportError:
        return _legacy_prepare(repo)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="VM handoff git preflight")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    result = prepare_vm_handoff(args.repo_root.resolve())
    if args.json:
        import json

        print(json.dumps(result, indent=2))
    elif not result.get("ok"):
        print(f"ppe_vm_handoff_preflight: failed — {result.get('error')}", file=sys.stderr)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
