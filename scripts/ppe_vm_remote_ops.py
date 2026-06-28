"""VM-side remote ops: commit staged control-plane docs and loop-publish (never push main directly)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    from scripts.ppe_operator_git_sync import _git as git_sync_git

    return git_sync_git(repo, *args)


def commit_staged_sop(repo: Path, *, message: str) -> dict[str, object]:
    repo = repo.resolve()
    proc = _git(repo, "diff", "--cached", "--name-only")
    staged = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    if not staged:
        return {"action": "commit", "skipped": True, "reason": "nothing staged"}
    if not all(p.replace("\\", "/").startswith("docs/SOP/") for p in staged):
        return {
            "action": "commit",
            "skipped": True,
            "reason": "staged paths outside docs/SOP — refuse auto-commit",
            "staged": staged,
        }
    commit = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if commit.returncode != 0:
        return {
            "action": "commit",
            "ok": False,
            "error": (commit.stderr or commit.stdout or "git commit failed").strip(),
            "staged": staged,
        }
    return {"action": "commit", "ok": True, "staged": staged, "message": message}


def commit_and_publish(repo: Path, *, message: str) -> dict[str, object]:
    repo = repo.resolve()
    report: dict[str, object] = {"repo": str(repo), "steps": []}
    report["steps"].append(commit_staged_sop(repo, message=message))
    from scripts.ppe_operator_git_sync import publish_ahead

    pub = publish_ahead(repo)
    report["steps"].append(pub)
    report["ok"] = pub.get("ok") is True or pub.get("skipped") is True
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="VM remote ops (commit SOP + loop publish)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pub = sub.add_parser("commit-and-publish", help="Commit staged docs/SOP and loop-publish")
    pub.add_argument(
        "--message",
        default="ops: loop publish control-plane steering",
        help="Commit message for staged docs/SOP",
    )

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.cmd == "commit-and-publish":
        result = commit_and_publish(repo, message=str(args.message))
    else:
        ap.error(f"unknown command {args.cmd!r}")
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for step in result.get("steps") or []:
            if isinstance(step, dict):
                action = step.get("action", "?")
                if step.get("skipped"):
                    print(f"ppe_vm_remote_ops: {action} skipped ({step.get('reason')})")
                elif step.get("ok") is False:
                    print(f"ppe_vm_remote_ops: {action} failed ({step.get('error')})")
                elif action == "push" and step.get("pr_url"):
                    print(f"ppe_vm_remote_ops: published {step.get('pushed_ref')} -> {step.get('pr_url')}")
                elif action == "commit" and step.get("ok"):
                    print(f"ppe_vm_remote_ops: committed {len(step.get('staged') or [])} SOP file(s)")
                elif action == "push" and step.get("ok"):
                    print(f"ppe_vm_remote_ops: pushed {step.get('pushed_ref')}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
