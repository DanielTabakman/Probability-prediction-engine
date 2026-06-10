"""Auto git pull/push for desktop loop host (no manual phone/laptop sync)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
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


def _env_disabled(key: str) -> bool:
    return os.environ.get(key, "").strip().lower() in ("0", "false", "no", "off")


def _git_sync_cfg(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
    except Exception:
        cfg = {}
    raw = cfg.get("gitSync")
    return raw if isinstance(raw, dict) else {}


def git_sync_enabled(repo: Path) -> bool:
    if _env_disabled("PPE_GIT_SYNC"):
        return False
    g = _git_sync_cfg(repo)
    return g.get("enabled", True) is not False


def pull_enabled(repo: Path) -> bool:
    if not git_sync_enabled(repo):
        return False
    if _env_disabled("PPE_GIT_SYNC_PULL"):
        return False
    return _git_sync_cfg(repo).get("pullEachPass", True) is not False


def push_enabled(repo: Path) -> bool:
    if not git_sync_enabled(repo):
        return False
    if _env_disabled("PPE_GIT_SYNC_PUSH"):
        return False
    return _git_sync_cfg(repo).get("pushAfterCommit", True) is not False


def publish_each_pass_enabled(repo: Path) -> bool:
    if not push_enabled(repo):
        return False
    g = _git_sync_cfg(repo)
    if g.get("publishEachPass") is False:
        return False
    return bool(g.get("publishEachPass", True))


def _current_branch(repo: Path) -> str:
    proc = _git(repo, "branch", "--show-current")
    return (proc.stdout or "").strip() if proc.returncode == 0 else ""


def _short_head(repo: Path) -> str:
    proc = _git(repo, "rev-parse", "--short", "HEAD")
    return (proc.stdout or "").strip() if proc.returncode == 0 else "local"


def _ahead_count(repo: Path, *, branch: str, remote: str = "origin") -> int:
    for ref in (f"{remote}/{branch}", branch):
        proc = _git(repo, "rev-list", "--count", f"{ref}..HEAD")
        if proc.returncode == 0:
            try:
                return int((proc.stdout or "0").strip() or "0")
            except ValueError:
                pass
    return 0


def _dirty_paths(repo: Path) -> list[str]:
    proc = _git(repo, "status", "--porcelain")
    if proc.returncode != 0:
        return []
    paths: list[str] = []
    for line in (proc.stdout or "").splitlines():
        if len(line) < 4:
            continue
        p = line[3:].strip().replace("\\", "/")
        if p and not p.startswith("_worktrees/"):
            paths.append(p)
    return paths


def ensure_main_on_loop_host(repo: Path) -> dict[str, Any]:
    """When loop host is on a clean ops/* branch, checkout main so pullEachPass works."""
    repo = repo.resolve()
    cfg = _git_sync_cfg(repo)
    if cfg.get("checkoutMainWhenOpsBranch", True) is False:
        return {"action": "checkout", "skipped": True, "reason": "disabled"}
    target = (str(cfg.get("pullBranch") or "main")).strip() or "main"
    current = _current_branch(repo)
    if not current or current == target:
        return {"action": "checkout", "skipped": True, "reason": "already on pull branch"}
    if not current.startswith("ops/"):
        return {"action": "checkout", "skipped": True, "reason": f"branch {current!r} not ops/*"}
    if _dirty_paths(repo):
        return {"action": "checkout", "skipped": True, "reason": "dirty working tree", "branch": current}
    fetch = _git(repo, "fetch", "origin")
    if fetch.returncode != 0:
        return {
            "action": "checkout",
            "ok": False,
            "error": (fetch.stderr or fetch.stdout or "git fetch failed").strip(),
        }
    runner = "run_ppe_desktop_operator.cmd"
    probe = _git(repo, "show", f"origin/{target}:{runner}")
    if probe.returncode != 0:
        return {
            "action": "checkout",
            "skipped": True,
            "reason": f"origin/{target} missing {runner} (stay on ops branch until merge)",
            "branch": current,
        }
    co = _git(repo, "checkout", target)
    if co.returncode != 0:
        return {
            "action": "checkout",
            "ok": False,
            "branch": current,
            "error": (co.stderr or co.stdout or "git checkout failed").strip(),
        }
    pull = _git(repo, "pull", "--ff-only", "origin", target)
    ok = pull.returncode == 0
    return {
        "action": "checkout",
        "checked_out": True,
        "ok": ok,
        "from": current,
        "branch": target,
        "stdout": (pull.stdout or co.stdout or "").strip(),
        "error": None if ok else (pull.stderr or pull.stdout or "git pull failed").strip(),
    }


def pull_main(repo: Path, *, branch: str | None = None) -> dict[str, Any]:
    """Fetch and fast-forward pull when on the configured branch and tree allows it."""
    repo = repo.resolve()
    if not pull_enabled(repo):
        return {"action": "pull", "skipped": True, "reason": "disabled"}

    ensure = ensure_main_on_loop_host(repo)
    if ensure.get("checked_out"):
        return ensure

    target = (branch or str(_git_sync_cfg(repo).get("pullBranch") or "main")).strip() or "main"
    current = _current_branch(repo)
    if current != target:
        return {
            "action": "pull",
            "skipped": True,
            "reason": f"checkout is {current!r}, not {target!r}",
        }

    dirty = _dirty_paths(repo)
    if dirty:
        return {
            "action": "pull",
            "skipped": True,
            "reason": "dirty working tree",
            "dirty": dirty[:8],
        }

    fetch = _git(repo, "fetch", "origin")
    if fetch.returncode != 0:
        return {
            "action": "pull",
            "ok": False,
            "error": (fetch.stderr or fetch.stdout or "git fetch failed").strip(),
        }

    pull = _git(repo, "pull", "--ff-only", "origin", target)
    ok = pull.returncode == 0
    result: dict[str, Any] = {
        "action": "pull",
        "ok": ok,
        "branch": target,
        "stdout": (pull.stdout or "").strip(),
    }
    if not ok:
        result["error"] = (pull.stderr or pull.stdout or "git pull failed").strip()
    return result


def _gh_available() -> bool:
    try:
        proc = subprocess.run(["gh", "--version"], capture_output=True, text=True, check=False)
        return proc.returncode == 0
    except FileNotFoundError:
        return False


def _open_pr(repo: Path, *, head: str, base: str = "main", title: str, body: str) -> str | None:
    if not _gh_available():
        print("ppe_operator_git_sync: gh not available; skip PR", file=sys.stderr)
        return None
    existing = subprocess.run(
        ["gh", "pr", "list", "--head", head, "--json", "url", "--limit", "1"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if existing.returncode == 0 and existing.stdout.strip():
        try:
            data = json.loads(existing.stdout)
            if data:
                return str(data[0].get("url") or "")
        except json.JSONDecodeError:
            pass
    proc = subprocess.run(
        ["gh", "pr", "create", "--base", base, "--head", head, "--title", title, "--body", body],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return None
    return (proc.stdout or "").strip()


def publish_ahead(repo: Path) -> dict[str, Any]:
    """Push unpushed commits; open PR when not on main (or when publishing from main)."""
    repo = repo.resolve()
    if not push_enabled(repo):
        return {"action": "push", "skipped": True, "reason": "disabled"}

    current = _current_branch(repo)
    if not current:
        return {"action": "push", "skipped": True, "reason": "detached HEAD"}

    ahead = _ahead_count(repo, branch=current)
    if ahead == 0:
        upstream = _git(repo, "rev-parse", "--abbrev-ref", "@{upstream}")
        if upstream.returncode == 0:
            up_branch = (upstream.stdout or "").strip().replace("origin/", "")
            ahead = _ahead_count(repo, branch=up_branch or current)
        if ahead == 0:
            return {"action": "push", "skipped": True, "reason": "nothing ahead"}

    publish_branch = current
    pushed_ref = current
    if current == "main":
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        publish_branch = f"ops/loop-publish-{stamp}-{_short_head(repo)}"
        push = _git(repo, "push", "origin", f"HEAD:refs/heads/{publish_branch}")
        pushed_ref = publish_branch
    else:
        push = _git(repo, "push", "-u", "origin", "HEAD")

    if push.returncode != 0:
        return {
            "action": "push",
            "ok": False,
            "branch": publish_branch,
            "error": (push.stderr or push.stdout or "git push failed").strip(),
        }

    pr_url = None
    if _git_sync_cfg(repo).get("openPrOnPush", True) is not False:
        pr_url = _open_pr(
            repo,
            head=pushed_ref,
            title=f"ops: loop publish {pushed_ref}",
            body="Auto-published by desktop loop host (ppe_operator_git_sync).",
        )

    return {
        "action": "push",
        "ok": True,
        "branch": publish_branch,
        "pushed_ref": pushed_ref,
        "pr_url": pr_url,
        "stdout": (push.stdout or "").strip(),
    }


def maybe_auto_publish(repo: Path) -> dict[str, Any]:
    """Push + open PR when this branch has unpushed commits (loop/agent work)."""
    repo = repo.resolve()
    if not publish_each_pass_enabled(repo):
        return {"action": "auto_publish", "skipped": True, "reason": "disabled"}
    current = _current_branch(repo)
    if not current or current == "main":
        return {"action": "auto_publish", "skipped": True, "reason": "not a feature branch"}
    if _dirty_paths(repo):
        return {
            "action": "auto_publish",
            "skipped": True,
            "reason": "dirty working tree — commit before auto-publish",
            "branch": current,
            "dirty": _dirty_paths(repo)[:5],
        }
    ahead = _ahead_count(repo, branch=current)
    if ahead == 0:
        return {"action": "auto_publish", "skipped": True, "reason": "nothing ahead", "branch": current}
    pub = publish_ahead(repo)
    pub["action"] = "auto_publish"
    return pub


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Desktop operator git sync")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--auto-publish", action="store_true", help="Push+PR when branch has unpushed commits")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    results: list[dict[str, Any]] = []
    if args.pull:
        results.append(pull_main(repo))
    if args.publish:
        results.append(publish_ahead(repo))
    if args.auto_publish:
        results.append(maybe_auto_publish(repo))
    if not results:
        ap.error("specify --pull, --publish, and/or --auto-publish")
        return 2

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"ppe_operator_git_sync: {json.dumps(r)}")

    ok = all(r.get("ok", True) or r.get("skipped") for r in results)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
