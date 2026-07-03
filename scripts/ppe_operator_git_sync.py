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


def _subprocess_timeout() -> int | None:
    raw = os.environ.get("PPE_GIT_CMD_TIMEOUT", "120").strip().lower()
    if raw in ("0", "none", "off", "false", "no"):
        return None
    try:
        return max(1, int(raw))
    except ValueError:
        return 120


def _run_cmd(
    argv: list[str],
    *,
    cwd: Path,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            argv,
            returncode=124,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=f"command timed out after {exc.timeout}s",
        )


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run_cmd(["git", *args], cwd=repo, timeout=_subprocess_timeout())


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


def merge_each_pass_enabled(repo: Path) -> bool:
    if not git_sync_enabled(repo):
        return False
    if _env_disabled("PPE_GIT_SYNC_MERGE"):
        return False
    g = _git_sync_cfg(repo)
    if g.get("mergeEachPass") is False:
        return False
    return bool(g.get("mergeEachPass", True))


def retarget_stacked_enabled(repo: Path) -> bool:
    if not git_sync_enabled(repo):
        return False
    if _env_disabled("PPE_GIT_SYNC_RETARGET"):
        return False
    g = _git_sync_cfg(repo)
    if g.get("retargetStackedPrs") is False:
        return False
    return bool(g.get("retargetStackedPrs", True))


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


def _dirty_paths(repo: Path, *, for_loop_host: bool = False) -> list[str]:
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
    try:
        from scripts.repo_layer_paths import is_preflight_dirty_exempt

        paths = [p for p in paths if not is_preflight_dirty_exempt(p)]
    except ImportError:
        if for_loop_host:
            pass
    return paths


_LOOP_HOST_TRANSIENT_PREFIXES: tuple[str, ...] = (
    "ops/",
    "build/auto/",
    "control-plane/",
    "charter/",
    "fix/",
)

VM_MIRROR_PUBLISH_PREFIX = "ops/vm-mirror-"
VM_OPERATOR_PHASE_REL = "docs/SOP/VM_OPERATOR_PHASE.json"


def _loop_host_transient_branch(current: str, target: str) -> bool:
    if not current or current == target:
        return False
    return any(current.startswith(prefix) for prefix in _LOOP_HOST_TRANSIENT_PREFIXES)


def ensure_main_on_loop_host(repo: Path) -> dict[str, Any]:
    """When loop host is on a transient branch, checkout main so pullEachPass works."""
    repo = repo.resolve()
    cfg = _git_sync_cfg(repo)
    if cfg.get("checkoutMainWhenOpsBranch", True) is False:
        return {"action": "checkout", "skipped": True, "reason": "disabled"}
    target = (str(cfg.get("pullBranch") or "main")).strip() or "main"
    current = _current_branch(repo)
    if not current or current == target:
        return {"action": "checkout", "skipped": True, "reason": "already on pull branch"}
    if not _loop_host_transient_branch(current, target):
        return {"action": "checkout", "skipped": True, "reason": f"branch {current!r} not loop-host transient"}
    dirty = _dirty_paths(repo, for_loop_host=True)
    if dirty:
        return {"action": "checkout", "skipped": True, "reason": "dirty working tree", "branch": current, "dirty": dirty}
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


def _gh_json(repo: Path, args: list[str]) -> Any | None:
    if not _gh_available():
        return None
    proc = subprocess.run(args, cwd=repo, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _pr_has_automerge(labels: list[Any]) -> bool:
    return any(isinstance(label, dict) and label.get("name") == "automerge" for label in labels)


def _default_merge_head_prefixes(cfg: dict[str, Any]) -> tuple[str, ...]:
    raw = cfg.get("mergeHeadPrefixes")
    if isinstance(raw, list) and raw:
        return tuple(str(p) for p in raw if str(p).strip())
    return _LOOP_HOST_TRANSIENT_PREFIXES + ("ops/",)


def _head_eligible_for_automerge(head: str, cfg: dict[str, Any]) -> bool:
    if head.startswith(VM_MIRROR_PUBLISH_PREFIX):
        return True
    return any(head.startswith(prefix) for prefix in _default_merge_head_prefixes(cfg))


def _merge_ready(pr: dict[str, Any]) -> bool:
    mergeable = str(pr.get("mergeable") or "").upper()
    state = str(pr.get("mergeStateStatus") or "").upper()
    if mergeable == "CONFLICTING" or state == "DIRTY":
        return False
    if state == "CLEAN":
        return True
    return mergeable == "MERGEABLE" and state in ("", "UNKNOWN", "BEHIND")


def close_conflicting_mirror_prs(repo: Path) -> dict[str, Any]:
    """Close stale vm-mirror PRs that conflict with main (unblocks fresh mirror publish)."""
    repo = repo.resolve()
    if not _gh_available():
        return {"action": "close_mirror_prs", "skipped": True, "reason": "gh not available"}

    cfg = _git_sync_cfg(repo)
    base = (str(cfg.get("pullBranch") or "main")).strip() or "main"
    prs = _gh_json(
        repo,
        [
            "gh",
            "pr",
            "list",
            "--base",
            base,
            "--state",
            "open",
            "--limit",
            "30",
            "--json",
            "number,headRefName,mergeable,mergeStateStatus,url",
        ],
    )
    if prs is None:
        return {"action": "close_mirror_prs", "ok": False, "error": "gh pr list failed"}

    closed: list[dict[str, Any]] = []
    for pr in prs:
        if not isinstance(pr, dict):
            continue
        head = str(pr.get("headRefName") or "")
        if not head.startswith(VM_MIRROR_PUBLISH_PREFIX):
            continue
        mergeable = str(pr.get("mergeable") or "").upper()
        state = str(pr.get("mergeStateStatus") or "").upper()
        if mergeable != "CONFLICTING" and state != "DIRTY":
            continue
        num = pr.get("number")
        if num is None:
            continue
        comment = (
            "Auto-closed: vm-mirror PR conflicts with main — superseded; "
            "loop host will publish a fresh mirror."
        )
        close_proc = subprocess.run(
            ["gh", "pr", "close", str(num), "--comment", comment],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if close_proc.returncode == 0:
            closed.append({"number": num, "head": head, "url": str(pr.get("url") or "")})

    return {"action": "close_mirror_prs", "ok": True, "closed": closed}


def check_and_nudge_merges(repo: Path) -> dict[str, Any]:
    """Ensure automerge label on loop PRs and squash-merge when GitHub reports merge-ready."""
    repo = repo.resolve()
    mirror_close = close_conflicting_mirror_prs(repo)
    if not merge_each_pass_enabled(repo):
        return {
            "action": "check_merge",
            "skipped": True,
            "reason": "disabled",
            "close_mirror_prs": mirror_close,
        }
    if not _gh_available():
        return {"action": "check_merge", "skipped": True, "reason": "gh not available"}

    cfg = _git_sync_cfg(repo)
    base = (str(cfg.get("pullBranch") or "main")).strip() or "main"
    prs = _gh_json(
        repo,
        [
            "gh",
            "pr",
            "list",
            "--base",
            base,
            "--state",
            "open",
            "--limit",
            "30",
            "--json",
            "number,headRefName,mergeable,mergeStateStatus,isDraft,labels,title,url",
        ],
    )
    if prs is None:
        return {"action": "check_merge", "ok": False, "error": "gh pr list failed"}
    if not prs:
        return {"action": "check_merge", "ok": True, "merged": [], "pending": [], "blocked": []}

    prs = sorted(
        prs,
        key=lambda item: (
            0
            if isinstance(item, dict)
            and str(item.get("headRefName") or "").startswith(VM_MIRROR_PUBLISH_PREFIX)
            else 1
        ),
    )

    merged: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    add_label = cfg.get("mergeAddAutomergeLabel", True) is not False

    for pr in prs:
        if not isinstance(pr, dict):
            continue
        num = pr.get("number")
        head = str(pr.get("headRefName") or "")
        url = str(pr.get("url") or "")
        if pr.get("isDraft"):
            pending.append({"number": num, "head": head, "url": url, "reason": "draft"})
            continue

        labels = pr.get("labels") or []
        has_label = _pr_has_automerge(labels if isinstance(labels, list) else [])
        eligible = has_label or _head_eligible_for_automerge(head, cfg)
        if not eligible:
            continue

        if not has_label and add_label and num is not None:
            label_proc = subprocess.run(
                ["gh", "pr", "edit", str(num), "--add-label", "automerge"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
            if label_proc.returncode != 0:
                pending.append(
                    {
                        "number": num,
                        "head": head,
                        "url": url,
                        "reason": (label_proc.stderr or label_proc.stdout or "add-label failed").strip(),
                    }
                )
                continue

        if not _merge_ready(pr):
            reason = str(pr.get("mergeStateStatus") or pr.get("mergeable") or "waiting on checks")
            if str(pr.get("mergeable") or "").upper() == "CONFLICTING":
                blocked.append({"number": num, "head": head, "url": url, "reason": "conflicts"})
            else:
                pending.append({"number": num, "head": head, "url": url, "reason": reason})
            continue

        merge_proc = subprocess.run(
            ["gh", "pr", "merge", str(num), "--squash"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if merge_proc.returncode == 0:
            merged.append({"number": num, "head": head, "url": url})
            continue
        pending.append(
            {
                "number": num,
                "head": head,
                "url": url,
                "reason": (merge_proc.stderr or merge_proc.stdout or "merge failed").strip(),
            }
        )

    result: dict[str, Any] = {
        "action": "check_merge",
        "ok": True,
        "merged": merged,
        "pending": pending,
        "blocked": blocked,
        "close_mirror_prs": mirror_close,
    }
    if merged and pull_enabled(repo):
        pull_after = pull_main(repo)
        result["pull_after_merge"] = pull_after
    return result


def check_and_retarget_stacked_prs(repo: Path) -> dict[str, Any]:
    """Retarget open PRs still based on a branch that already merged to main."""
    repo = repo.resolve()
    if not retarget_stacked_enabled(repo):
        return {"action": "retarget_stacked", "skipped": True, "reason": "disabled"}
    if not _gh_available():
        return {"action": "retarget_stacked", "skipped": True, "reason": "gh not available"}

    from scripts.retarget_stacked_prs import scan_and_retarget_stacked_prs

    cfg = _git_sync_cfg(repo)
    main = (str(cfg.get("pullBranch") or "main")).strip() or "main"
    return scan_and_retarget_stacked_prs(repo, main=main)


def _open_pr(
    repo: Path,
    *,
    head: str,
    base: str = "main",
    title: str,
    body: str,
    labels: list[str] | None = None,
) -> str | None:
    if not _gh_available():
        print("ppe_operator_git_sync: gh not available; skip PR", file=sys.stderr)
        return None
    timeout = _subprocess_timeout()
    existing = _run_cmd(
        ["gh", "pr", "list", "--head", head, "--json", "url", "--limit", "1"],
        cwd=repo,
        timeout=timeout,
    )
    if existing.returncode == 0 and existing.stdout.strip():
        try:
            data = json.loads(existing.stdout)
            if data:
                url = str(data[0].get("url") or "")
                if url and labels:
                    for label in labels:
                        _run_cmd(
                            ["gh", "pr", "edit", head, "--add-label", label],
                            cwd=repo,
                            timeout=timeout,
                        )
                return url
        except json.JSONDecodeError:
            pass
    create_args = ["gh", "pr", "create", "--base", base, "--head", head, "--title", title, "--body", body]
    if labels:
        for label in labels:
            create_args.extend(["--label", label])
    proc = _run_cmd(create_args, cwd=repo, timeout=timeout)
    if proc.returncode == 124:
        print("ppe_operator_git_sync: gh pr create timed out", file=sys.stderr)
        return None
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

    if push.returncode == 124:
        return {
            "action": "push",
            "ok": False,
            "branch": publish_branch,
            "error": (push.stderr or "git push timed out").strip(),
            "timed_out": True,
        }
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


def _mirror_differs_from_origin_main(repo: Path) -> bool:
    _git(repo, "fetch", "origin", "main", "--quiet")
    proc = _git(repo, "diff", "--name-only", f"origin/main...HEAD", "--", VM_OPERATOR_PHASE_REL)
    if proc.returncode == 0 and (proc.stdout or "").strip():
        return True
    proc2 = _git(repo, "diff", "--name-only", "origin/main", "--", VM_OPERATOR_PHASE_REL)
    return bool((proc2.stdout or "").strip())


def _publish_vm_mirror_worktree(repo: Path, *, phase: str) -> dict[str, Any]:
    """Publish mirror JSON from working tree without checking out main (relay branch safe)."""
    import shutil
    import tempfile

    repo = repo.resolve()
    mirror_src = repo / VM_OPERATOR_PHASE_REL
    if not mirror_src.is_file():
        return {"action": "vm_mirror_worktree", "skipped": True, "reason": "no_mirror_file"}

    _git(repo, "fetch", "origin", "main", "--quiet")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    publish_branch = f"{VM_MIRROR_PUBLISH_PREFIX}{stamp}-{_short_head(repo)}"
    phase_label = (phase or "unknown").replace("_", " ")
    wt_root = Path(tempfile.mkdtemp(prefix="ppe-vm-mirror-"))
    try:
        add = _git(repo, "worktree", "add", "-B", publish_branch, str(wt_root), "origin/main")
        if add.returncode != 0:
            return {
                "action": "vm_mirror_worktree",
                "ok": False,
                "error": (add.stderr or add.stdout or "worktree add failed").strip(),
            }
        mirror_dst = wt_root / VM_OPERATOR_PHASE_REL
        mirror_dst.parent.mkdir(parents=True, exist_ok=True)
        mirror_dst.write_text(mirror_src.read_text(encoding="utf-8"), encoding="utf-8")
        stage = _git(wt_root, "add", "--", VM_OPERATOR_PHASE_REL)
        if stage.returncode != 0:
            return {"action": "vm_mirror_worktree", "ok": False, "error": "git add failed"}
        commit = _git(wt_root, "commit", "-m", f"ops: vm phase mirror {phase_label}")
        if commit.returncode != 0:
            err = (commit.stderr or commit.stdout or "").strip()
            if "nothing to commit" in err.lower():
                return {"action": "vm_mirror_worktree", "skipped": True, "reason": "nothing_to_commit"}
            return {"action": "vm_mirror_worktree", "ok": False, "error": err}
        push = _git(wt_root, "push", "-u", "origin", publish_branch)
        if push.returncode != 0:
            return {
                "action": "vm_mirror_worktree",
                "ok": False,
                "branch": publish_branch,
                "error": (push.stderr or push.stdout or "git push failed").strip(),
            }
    finally:
        _git(repo, "worktree", "remove", "--force", str(wt_root))
        shutil.rmtree(wt_root, ignore_errors=True)

    pr_url = None
    if _git_sync_cfg(repo).get("openPrOnPush", True) is not False:
        pr_url = _open_pr(
            repo,
            head=publish_branch,
            title=f"ops: vm phase mirror {phase_label}",
            body=(
                "Auto-published VM phase mirror (`docs/SOP/VM_OPERATOR_PHASE.json`) from loop host "
                "(worktree off main).\n\nMirror-only — safe to automerge when checks pass."
            ),
            labels=["automerge"],
        )
    return {
        "action": "vm_mirror_worktree",
        "ok": True,
        "branch": publish_branch,
        "pushed_ref": publish_branch,
        "pr_url": pr_url,
        "mirror_only": True,
        "off_main": True,
    }


def publish_vm_mirror_ahead(repo: Path, *, phase: str = "unknown") -> dict[str, Any]:
    """Push VM phase mirror commit from main; open automerge PR for desktop git pull."""
    repo = repo.resolve()
    if not push_enabled(repo):
        return {"action": "vm_mirror_push", "skipped": True, "reason": "disabled"}

    current = _current_branch(repo)
    if current == "main":
        ahead = _ahead_count(repo, branch="main")
        if ahead > 0:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            publish_branch = f"{VM_MIRROR_PUBLISH_PREFIX}{stamp}-{_short_head(repo)}"
            push = _git(repo, "push", "origin", f"HEAD:refs/heads/{publish_branch}")
            if push.returncode == 124:
                return {
                    "action": "vm_mirror_push",
                    "ok": False,
                    "branch": publish_branch,
                    "error": (push.stderr or "git push timed out").strip(),
                    "timed_out": True,
                }
            if push.returncode != 0:
                return {
                    "action": "vm_mirror_push",
                    "ok": False,
                    "branch": publish_branch,
                    "error": (push.stderr or push.stdout or "git push failed").strip(),
                }

            pr_url = None
            if _git_sync_cfg(repo).get("openPrOnPush", True) is not False:
                phase_label = (phase or "unknown").replace("_", " ")
                pr_url = _open_pr(
                    repo,
                    head=publish_branch,
                    title=f"ops: vm phase mirror {phase_label}",
                    body=(
                        "Auto-published VM phase mirror (`docs/SOP/VM_OPERATOR_PHASE.json`) from loop host.\n\n"
                        "Mirror-only — safe to automerge when checks pass."
                    ),
                    labels=["automerge"],
                )

            return {
                "action": "vm_mirror_push",
                "ok": True,
                "branch": publish_branch,
                "pushed_ref": publish_branch,
                "pr_url": pr_url,
                "mirror_only": True,
                "stdout": (push.stdout or "").strip(),
            }
        if _mirror_differs_from_origin_main(repo) or (repo / VM_OPERATOR_PHASE_REL).is_file():
            return _publish_vm_mirror_worktree(repo, phase=phase)
        return {"action": "vm_mirror_push", "skipped": True, "reason": "nothing ahead"}

    if (repo / VM_OPERATOR_PHASE_REL).is_file():
        return _publish_vm_mirror_worktree(repo, phase=phase)
    return {"action": "vm_mirror_push", "skipped": True, "reason": f"not on main ({current!r})"}


RUNTIME_SOP_EXACT: frozenset[str] = frozenset(
    {
        "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
        "docs/SOP/PHASE_QUEUE.json",
        "docs/SOP/PHASE_CHAPTER_BACKLOG.json",
        "docs/SOP/PHASE_SELECTION_ROADMAP.json",
        "docs/SOP/assets/msos_module_map.html",
    }
)


def is_runtime_sop_path(path: str) -> bool:
    p = path.replace("\\", "/").strip()
    if p in RUNTIME_SOP_EXACT:
        return True
    if p.startswith("docs/SOP/PHASE_") and p.endswith(".json"):
        return True
    if p.startswith("docs/SOP/") and p.endswith("_EVIDENCE_STATUS.md"):
        return True
    if p.startswith("docs/SOP/") and p.endswith("_SELECTION.md"):
        return False
    if p.startswith("docs/SOP/") and p in {
        "docs/SOP/AGENT_CONTINUITY_BRIEF.md",
        "docs/SOP/HANDOFF.md",
        "docs/SOP/MVP1_FRONTIER.md",
        "docs/SOP/PPE_INTEGRATED_STATUS.md",
    }:
        return True
    return False


def _runtime_sop_only_dirty(repo: Path) -> bool:
    dirty = _dirty_paths(repo)
    if not dirty:
        return True
    for p in dirty:
        if p.startswith("artifacts/"):
            continue
        if is_runtime_sop_path(p):
            continue
        if p.startswith("docs/RELEASES/"):
            continue
        return False
    return True


def reset_runtime_sop_drift_from_origin(repo: Path) -> dict[str, Any]:
    """Discard uncommitted control-plane drift on the loop host so main sync can proceed."""
    repo = repo.resolve()
    target = (str(_git_sync_cfg(repo).get("pullBranch") or "main")).strip() or "main"
    current = _current_branch(repo)
    dirty = _dirty_paths(repo, for_loop_host=True)
    reset_paths = sorted(
        {
            p
            for p in dirty
            if is_runtime_sop_path(p) or p.startswith("docs/RELEASES/")
        }
    )
    if not reset_paths:
        return {"action": "reset_runtime_sop", "skipped": True, "reason": "no runtime SOP drift"}
    if not _loop_host_transient_branch(current, target) and not _runtime_sop_only_dirty(repo):
        return {
            "action": "reset_runtime_sop",
            "skipped": True,
            "reason": f"branch {current!r} has non-runtime product dirty paths",
            "dirty": dirty[:8],
        }

    fetch = _git(repo, "fetch", "origin")
    if fetch.returncode != 0:
        return {
            "action": "reset_runtime_sop",
            "ok": False,
            "error": (fetch.stderr or fetch.stdout or "git fetch failed").strip(),
        }

    changes: list[str] = []
    for rel in reset_paths:
        proc = _git(repo, "checkout", f"origin/{target}", "--", rel)
        if proc.returncode == 0:
            changes.append(f"reset {rel} from origin/{target}")
    return {
        "action": "reset_runtime_sop",
        "ok": True,
        "branch": current,
        "changes": changes,
    }


def _git_operation_in_progress(repo: Path) -> bool:
    git_dir = repo / ".git"
    if (git_dir / "MERGE_HEAD").is_file():
        return True
    if (git_dir / "rebase-merge").is_dir() or (git_dir / "rebase-apply").is_dir():
        return True
    return False


def _detach_main_worktrees(repo: Path) -> list[dict[str, Any]]:
    """Detach orchestrator worktrees holding main so checkout can succeed."""
    try:
        from scripts.ppe_vm_bootstrap import detach_worktrees_holding_branch

        return detach_worktrees_holding_branch(repo, "main")
    except ImportError:
        return []


def _handoff_light_recover(repo: Path) -> dict[str, Any]:
    """Minimal VM recovery when prepare_handoff fails (worktrees, locks, hygiene)."""
    repo = repo.resolve()
    steps: list[dict[str, Any]] = []
    detached = _detach_main_worktrees(repo)
    if detached:
        steps.append({"action": "detach_main_worktrees", "detached": detached})
    try:
        from scripts.ppe_vm_bootstrap import (
            ensure_on_main,
            heal_operator_artifacts,
            heal_stale_relay_state,
            loop_host_git_hygiene,
        )

        steps.append(ensure_on_main(repo))
        steps.append(loop_host_git_hygiene(repo))
        steps.append(heal_stale_relay_state(repo))
        steps.append(heal_operator_artifacts(repo))
    except ImportError as exc:
        return {"action": "handoff_light_recover", "ok": False, "error": str(exc), "steps": steps}
    ok = all(s.get("ok", True) or s.get("skipped") for s in steps if isinstance(s, dict))
    return {"action": "handoff_light_recover", "ok": ok, "steps": steps}


def prepare_loop_host_for_handoff(repo: Path) -> dict[str, Any]:
    """Prepare loop-host git state before DESKTOP_CONTINUE / finish_ide_build.

    Clears stale merge state, resets runtime SOP drift, returns transient build
    branches to origin/main, then fast-forwards pull. Safe only on the VM loop
    host after desktop IDE BUILD has merged.
    """
    repo = repo.resolve()
    target = (str(_git_sync_cfg(repo).get("pullBranch") or "main")).strip() or "main"
    changes: list[str] = []
    from_branch = _current_branch(repo)

    detached = _detach_main_worktrees(repo)
    if detached:
        ok_detach = all(d.get("detached") for d in detached)
        changes.append(f"detach_main_worktrees ({len(detached)} worktree(s))")
        if not ok_detach:
            errors = [d.get("error") for d in detached if d.get("error")]
            if errors:
                changes.append(f"detach_errors: {'; '.join(str(e) for e in errors[:3])}")

    if _git_operation_in_progress(repo):
        _git(repo, "merge", "--abort")
        changes.append("merge --abort")

    sop = reset_runtime_sop_drift_from_origin(repo)
    changes.extend(sop.get("changes") or [])

    current = _current_branch(repo)
    if _loop_host_transient_branch(current, target):
        fetch = _git(repo, "fetch", "origin")
        if fetch.returncode != 0:
            return {
                "action": "prepare_handoff",
                "ok": False,
                "from_branch": from_branch,
                "changes": changes,
                "error": (fetch.stderr or fetch.stdout or "git fetch failed").strip(),
            }
        co = _git(repo, "checkout", "-f", target)
        if co.returncode != 0:
            co = _git(repo, "checkout", target)
        hard = _git(repo, "reset", "--hard", f"origin/{target}")
        ok_reset = hard.returncode == 0
        if ok_reset:
            changes.append(f"reset --hard origin/{target} (from transient {current})")
        current = _current_branch(repo)
    elif current == target:
        dirty = _dirty_paths(repo)
        if dirty and _runtime_sop_only_dirty(repo):
            sop2 = reset_runtime_sop_drift_from_origin(repo)
            changes.extend(sop2.get("changes") or [])

    fetch = _git(repo, "fetch", "origin")
    if fetch.returncode != 0:
        return {
            "action": "prepare_handoff",
            "ok": False,
            "from_branch": from_branch,
            "branch": _current_branch(repo),
            "changes": changes,
            "error": (fetch.stderr or fetch.stdout or "git fetch failed").strip(),
        }

    if _current_branch(repo) != target:
        co = _git(repo, "checkout", target)
        if co.returncode != 0:
            return {
                "action": "prepare_handoff",
                "ok": False,
                "from_branch": from_branch,
                "branch": _current_branch(repo),
                "changes": changes,
                "error": (co.stderr or co.stdout or "git checkout failed").strip(),
            }
        changes.append(f"checkout {target}")

    pull = _git(repo, "pull", "--ff-only", "origin", target)
    ok = pull.returncode == 0
    result: dict[str, Any] = {
        "action": "prepare_handoff",
        "ok": ok,
        "from_branch": from_branch,
        "branch": _current_branch(repo),
        "changes": changes,
        "stdout": (pull.stdout or "").strip(),
    }
    if not ok:
        result["error"] = (pull.stderr or pull.stdout or "git pull failed").strip()
    return result


def prepare_handoff_with_auto_recover(repo: Path) -> dict[str, Any]:
    """prepare_handoff; on failure run light recover + ensure stack + retry once."""
    repo = repo.resolve()
    first = prepare_loop_host_for_handoff(repo)
    if first.get("ok"):
        first["auto_recover"] = False
        return first

    recover = _handoff_light_recover(repo)
    retry = prepare_loop_host_for_handoff(repo)
    retry["auto_recover"] = True
    retry["first_attempt"] = {
        "ok": first.get("ok"),
        "error": first.get("error"),
        "changes": first.get("changes"),
    }
    retry["recover"] = recover
    if retry.get("ok"):
        return retry

    try:
        from scripts.ppe_vm_bootstrap import bootstrap

        bootstrap(
            repo,
            sync_progress=False,
            heal=True,
            queue_repair=False,
            run_local=False,
            ensure_stack=True,
            detach_main_worktrees=True,
            ensure_main=True,
        )
        final = prepare_loop_host_for_handoff(repo)
        final["auto_recover"] = True
        final["bootstrap_retry"] = True
        final["first_attempt"] = retry.get("first_attempt")
        final["recover"] = recover
        return final
    except ImportError:
        retry["bootstrap_retry"] = False
        return retry


def maybe_auto_publish(repo: Path) -> dict[str, Any]:
    """Push + open PR when this branch has unpushed commits (loop/agent work)."""
    repo = repo.resolve()
    if not publish_each_pass_enabled(repo):
        return {"action": "auto_publish", "skipped": True, "reason": "disabled"}
    current = _current_branch(repo)
    if not current or current == "main":
        return {"action": "auto_publish", "skipped": True, "reason": "not a feature branch"}
    dirty = _dirty_paths(repo)
    if dirty and not _runtime_sop_only_dirty(repo):
        return {
            "action": "auto_publish",
            "skipped": True,
            "reason": "dirty working tree — commit product/control changes before auto-publish",
            "branch": current,
            "dirty": dirty[:5],
        }
    ahead = _ahead_count(repo, branch=current)
    if ahead == 0:
        pr_url = None
        if _git_sync_cfg(repo).get("openPrOnPush", True) is not False and _gh_available():
            pr_url = _open_pr(
                repo,
                head=current,
                title=f"ops: {current}",
                body="Auto-published by desktop loop host (ppe_operator_git_sync).",
            )
        if pr_url:
            return {
                "action": "auto_publish",
                "ok": True,
                "skipped": False,
                "reason": "PR ensured (branch already pushed)",
                "branch": current,
                "pr_url": pr_url,
            }
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
    ap.add_argument(
        "--check-merge",
        action="store_true",
        help="Label loop PRs automerge and squash-merge when CI is green",
    )
    ap.add_argument(
        "--retarget-stacked",
        action="store_true",
        help="Retarget child PRs to main when parent branch already merged",
    )
    ap.add_argument(
        "--reset-runtime-sop",
        action="store_true",
        help="Discard loop-host runtime SOP/RELEASES drift from origin before pull",
    )
    ap.add_argument(
        "--prepare-handoff",
        action="store_true",
        help="Loop host only: abort merges, reset runtime SOP drift, return to main, pull",
    )
    ap.add_argument(
        "--prepare-handoff-auto",
        action="store_true",
        help="Like --prepare-handoff; on failure detach worktrees, heal, ensure stack, retry",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    results: list[dict[str, Any]] = []
    if args.prepare_handoff_auto:
        results.append(prepare_handoff_with_auto_recover(repo))
    elif args.prepare_handoff:
        results.append(prepare_loop_host_for_handoff(repo))
    if args.pull:
        results.append(pull_main(repo))
    if args.publish:
        results.append(publish_ahead(repo))
    if args.auto_publish:
        results.append(maybe_auto_publish(repo))
    if args.check_merge:
        results.append(check_and_nudge_merges(repo))
    if args.retarget_stacked:
        results.append(check_and_retarget_stacked_prs(repo))
    if args.reset_runtime_sop:
        results.append(reset_runtime_sop_drift_from_origin(repo))
    if not results:
        ap.error(
            "specify --pull, --prepare-handoff, --prepare-handoff-auto, --reset-runtime-sop, "
            "--publish, --auto-publish, --check-merge, and/or --retarget-stacked"
        )
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
