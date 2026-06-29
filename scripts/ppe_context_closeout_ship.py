"""Automatic git ship sweep for context window closeout.

Gate → commit → push → open PR (automerge label). No operator merge clicks.
Canon: docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COMMIT_EXCLUDED_PREFIXES: tuple[str, ...] = (
    "artifacts/",
    "_worktrees/",
    ".env",
    ".cursor/projects/",
)
COMMIT_EXCLUDED_EXACT: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        ".env.production",
    }
)


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def is_commit_excluded(path: str) -> bool:
    p = _norm(path)
    if p in COMMIT_EXCLUDED_EXACT:
        return True
    lower = p.lower()
    if "credential" in lower or lower.endswith(".pem") or lower.endswith(".key"):
        return True
    return any(p.startswith(prefix) for prefix in COMMIT_EXCLUDED_PREFIXES)


def committable_dirty_paths(repo: Path) -> list[str]:
    from scripts.repo_layer_paths import git_dirty_paths, is_preflight_dirty_exempt

    return [
        p
        for p in git_dirty_paths(repo)
        if not is_preflight_dirty_exempt(p) and not is_commit_excluded(p)
    ]


def _commit_message_for_paths(paths: list[str]) -> str:
    norm = [_norm(p) for p in paths]
    if norm and all(p.startswith("docs/") for p in norm):
        return "control-plane: context closeout auto-ship (docs)"
    if any(p.startswith("src/") or p.startswith("apps/") for p in norm):
        return "product: context closeout auto-ship"
    if any(p.startswith("tests/") or p.startswith("scripts/") for p in norm):
        return "evidence-plane: context closeout auto-ship"
    return "control-plane: context closeout auto-ship"


def _preflight(repo: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(repo / "scripts" / "frontier_preflight.py"), "--json"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 1) or not proc.stdout.strip():
        return {}
    try:
        import json

        data = json.loads(proc.stdout)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _run_gate(
    repo: Path,
    files: list[str],
    *,
    pre_push: bool = False,
    pytest_profile: str | None = None,
) -> tuple[bool, str]:
    from scripts.run_pushable_gate import run_gate_for_paths

    kwargs: dict[str, Any] = {"pre_push": pre_push}
    if pytest_profile:
        kwargs["pytest_profile"] = pytest_profile  # type: ignore[arg-type]
    rc = run_gate_for_paths(repo, files, **kwargs)
    if rc != 0:
        return False, "gate failed"
    return True, "gate passed"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    from scripts.ppe_operator_git_sync import _git as git_run

    return git_run(repo, *args)


def _ensure_closeout_branch(repo: Path, *, current: str) -> tuple[bool, str, str]:
    from scripts.ppe_operator_git_sync import _short_head

    if current and current != "main":
        return True, current, "already on feature branch"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    branch = f"ops/closeout-{stamp}-{_short_head(repo)}"
    co = _git(repo, "checkout", "-b", branch)
    if co.returncode != 0:
        return False, current, (co.stderr or co.stdout or "checkout failed").strip()
    return True, branch, f"created {branch}"


def _stage_paths(repo: Path, paths: list[str]) -> tuple[bool, str]:
    if not paths:
        return True, "nothing to stage"
    add = _git(repo, "add", "--", *paths)
    if add.returncode != 0:
        return False, (add.stderr or add.stdout or "git add failed").strip()
    return True, f"staged {len(paths)} path(s)"


def _commit(repo: Path, *, message: str) -> tuple[bool, str]:
    commit = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if commit.returncode != 0:
        return False, (commit.stderr or commit.stdout or "git commit failed").strip()
    return True, message


def _unstage_all(repo: Path) -> None:
    _git(repo, "reset", "HEAD")


def _label_automerge(repo: Path, head: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["gh", "pr", "list", "--head", head, "--json", "number", "--limit", "1"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False, "gh not available"
    if proc.returncode != 0 or not proc.stdout.strip():
        return False, "no open PR for head"
    try:
        import json

        rows = json.loads(proc.stdout)
        num = rows[0].get("number") if rows else None
    except (json.JSONDecodeError, IndexError, KeyError):
        return False, "could not parse gh pr list"
    if not num:
        return False, "no PR number"
    label = subprocess.run(
        ["gh", "pr", "edit", str(num), "--add-label", "automerge"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if label.returncode != 0:
        return False, (label.stderr or label.stdout or "add-label failed").strip()
    return True, f"labeled PR #{num} automerge"


def _publish(repo: Path, *, branch: str) -> dict[str, Any]:
    from scripts.ppe_operator_git_sync import _open_pr, push_enabled

    if not push_enabled(repo):
        return {"action": "publish", "skipped": True, "reason": "push disabled"}

    push = _git(repo, "push", "-u", "origin", "HEAD")
    if push.returncode != 0:
        return {
            "action": "publish",
            "ok": False,
            "branch": branch,
            "error": (push.stderr or push.stdout or "git push failed").strip(),
        }

    title = f"ops: context closeout ship ({branch})"
    body = (
        "Auto-shipped by context window closeout (`ppe_context_closeout_ship.py`).\n\n"
        "Merge-on-green applies when CI passes — no operator action required."
    )
    pr_url = _open_pr(repo, head=branch, title=title, body=body)
    label_ok, label_detail = _label_automerge(repo, branch) if pr_url else (False, "no PR")
    return {
        "action": "publish",
        "ok": True,
        "branch": branch,
        "pr_url": pr_url,
        "automerge_label": label_ok,
        "automerge_detail": label_detail,
    }


def run_operational_sweep(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Commit dirty shippable work, push, open PR. Idempotent when tree is clean."""
    repo = repo.resolve()
    report: dict[str, Any] = {
        "action": "operational_sweep",
        "ok": True,
        "dry_run": dry_run,
        "steps": [],
        "parked": [],
        "blocked": False,
    }

    def step(name: str, payload: dict[str, Any]) -> None:
        row = {"step": name, **payload}
        report["steps"].append(row)
        if payload.get("ok") is False and not payload.get("optional"):
            report["ok"] = False
        if payload.get("blocked"):
            report["blocked"] = True

    pf = _preflight(repo)
    branch = str(pf.get("branch") or "")
    wt = str(pf.get("working_tree") or "")
    report["preflight"] = {"branch": branch, "working_tree": wt, "blocker": pf.get("blocker")}

    if branch == "HEAD":
        step(
            "branch",
            {
                "ok": False,
                "blocked": True,
                "reason": "detached HEAD — park manually",
            },
        )
        return report

    fetch = _git(repo, "fetch", "origin")
    step(
        "fetch",
        {
            "ok": fetch.returncode == 0,
            "optional": True,
            "detail": (fetch.stderr or fetch.stdout or "").strip()[:200],
        },
    )

    if pf.get("blocker") and "unmerged" in str(pf.get("blocker") or "").lower():
        step(
            "conflicts",
            {
                "ok": False,
                "blocked": True,
                "reason": pf.get("blocker"),
            },
        )
        return report

    dirty = committable_dirty_paths(repo)
    if pf.get("mixed_plane_dirty") and dirty:
        step(
            "mixed_plane",
            {
                "ok": False,
                "blocked": True,
                "reason": "mixed-plane dirty — parked for recovery thread",
                "paths": dirty[:12],
            },
        )
        report["parked"] = dirty
        return report

    if wt == "clean" or not dirty:
        from scripts.ppe_operator_git_sync import _ahead_count, _current_branch, publish_ahead

        current = _current_branch(repo) or branch
        ahead = _ahead_count(repo, branch=current)
        if ahead > 0:
            if dry_run:
                step("publish_ahead", {"ok": True, "dry_run": True, "branch": current, "ahead": ahead})
            else:
                pub = publish_ahead(repo)
                step("publish_ahead", pub)
                if pub.get("ok") and pub.get("pr_url"):
                    head = str(pub.get("pushed_ref") or current)
                    label_ok, label_detail = _label_automerge(repo, head)
                    step(
                        "automerge_label",
                        {"ok": label_ok, "optional": not label_ok, "detail": label_detail},
                    )
        else:
            step("clean", {"ok": True, "reason": "working tree clean; nothing to ship"})
        return report

    if dry_run:
        step(
            "ship",
            {
                "ok": True,
                "dry_run": True,
                "paths": dirty,
                "message": _commit_message_for_paths(dirty),
            },
        )
        return report

    ok_branch, work_branch, branch_detail = _ensure_closeout_branch(repo, current=branch)
    step("branch", {"ok": ok_branch, "branch": work_branch, "detail": branch_detail})
    if not ok_branch:
        report["blocked"] = True
        return report

    ok_stage, stage_detail = _stage_paths(repo, dirty)
    step("stage", {"ok": ok_stage, "detail": stage_detail, "paths": dirty})
    if not ok_stage:
        return report

    gate_ok, gate_detail = _run_gate(repo, dirty, pre_push=False)
    step("gate", {"ok": gate_ok, "detail": gate_detail})
    if not gate_ok:
        _unstage_all(repo)
        report["parked"] = dirty
        report["blocked"] = True
        return report

    message = _commit_message_for_paths(dirty)
    ok_commit, commit_detail = _commit(repo, message=message)
    step("commit", {"ok": ok_commit, "detail": commit_detail})
    if not ok_commit:
        _unstage_all(repo)
        report["blocked"] = True
        return report

    from scripts.run_pushable_gate import _upstream_ref

    if _upstream_ref(repo):
        pre_ok, pre_detail = _run_gate(repo, dirty, pre_push=True)
    else:
        pre_ok, pre_detail = _run_gate(repo, dirty, pre_push=False)
        if pre_ok:
            from scripts.run_pushable_gate import run_gate_for_paths

            pre_ok = run_gate_for_paths(repo, dirty, pytest_profile="full") == 0
            pre_detail = "full pytest (no upstream yet)"
    step("pre_push_gate", {"ok": pre_ok, "detail": pre_detail})
    if not pre_ok:
        report["blocked"] = True
        return report

    pub = _publish(repo, branch=work_branch)
    step("publish", pub)
    if not pub.get("ok"):
        report["blocked"] = True
    return report
