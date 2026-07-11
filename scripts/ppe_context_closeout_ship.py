"""Bounded context closeout: commit onto the active chapter branch and update its PR.

The closeout path no longer creates timestamped branches, replacement PRs, or
automerge labels. Publication is delegated to `ppe_chapter_publisher.py`.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

COMMIT_EXCLUDED_PREFIXES: tuple[str, ...] = (
    "artifacts/",
    "_worktrees/",
    ".env",
    ".cursor/projects/",
)
COMMIT_EXCLUDED_EXACT: frozenset[str] = frozenset({".env", ".env.local", ".env.production"})


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
        return "control-plane: context closeout"
    if any(p.startswith("src/") or p.startswith("apps/") for p in norm):
        return "product: context closeout"
    if any(p.startswith("tests/") or p.startswith("scripts/") for p in norm):
        return "evidence-plane: context closeout"
    return "control-plane: context closeout"


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
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


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
        kwargs["pytest_profile"] = pytest_profile
    rc = run_gate_for_paths(repo, files, **kwargs)
    return (rc == 0, "gate passed" if rc == 0 else "gate failed")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)


def _current_branch(repo: Path) -> str:
    proc = _git(repo, "branch", "--show-current")
    return (proc.stdout or "").strip() if proc.returncode == 0 else ""


def _ahead_count(repo: Path, branch: str) -> int:
    for ref in (f"origin/{branch}", "origin/main", "main"):
        proc = _git(repo, "rev-list", "--count", f"{ref}..HEAD")
        if proc.returncode == 0:
            try:
                return int((proc.stdout or "0").strip() or "0")
            except ValueError:
                continue
    return 0


def _load_manifest(repo: Path) -> dict[str, Any]:
    path = repo / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def infer_chapter_id(repo: Path, preflight: dict[str, Any] | None = None) -> str:
    explicit = os.environ.get("PPE_ACTIVE_CHAPTER_ID", "").strip()
    if explicit:
        return explicit
    pf = preflight or {}
    for key in ("chapter_id", "chapter_name", "phase_plan_path"):
        value = str(pf.get(key) or "").strip()
        if value:
            return value
    manifest = _load_manifest(repo)
    for key in ("chapterId", "chapterName", "phasePlanPath", "phasePlan"):
        value = str(manifest.get(key) or "").strip()
        if value:
            return value
    branch = _current_branch(repo)
    if branch and branch not in ("main", "master"):
        return branch
    return "context-closeout"


def _ensure_chapter_branch(repo: Path, *, current: str, chapter_id: str) -> tuple[bool, str, str]:
    from scripts.ppe_chapter_publisher import chapter_branch

    if current and current not in ("main", "master", "HEAD"):
        return True, current, "using active feature branch"
    branch = chapter_branch(chapter_id)
    co = _git(repo, "checkout", "-b", branch)
    if co.returncode != 0:
        co = _git(repo, "checkout", branch)
    if co.returncode != 0:
        return False, current, (co.stderr or co.stdout or "checkout failed").strip()
    return True, branch, f"using stable chapter branch {branch}"


def _stage_paths(repo: Path, paths: list[str]) -> tuple[bool, str]:
    if not paths:
        return True, "nothing to stage"
    add = _git(repo, "add", "--", *paths)
    if add.returncode != 0:
        return False, (add.stderr or add.stdout or "git add failed").strip()
    return True, f"staged {len(paths)} path(s)"


def _commit(repo: Path, *, message: str) -> tuple[bool, str]:
    proc = _git(repo, "commit", "-m", message)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "git commit failed").strip()
    return True, message


def _unstage_all(repo: Path) -> None:
    _git(repo, "reset", "HEAD")


def _publish(
    repo: Path,
    *,
    chapter_id: str,
    branch: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    from scripts.ppe_chapter_publisher import publish_chapter

    return publish_chapter(
        repo,
        chapter_id=chapter_id,
        title=f"Chapter: {chapter_id}",
        body=(
            "Context closeout updated the existing chapter publication. "
            "No timestamp branch or replacement PR was created."
        ),
        create_branch_if_main=False,
        dry_run=dry_run,
    )


def run_operational_sweep(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Commit shippable work and update exactly one chapter PR."""
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
        report["steps"].append({"step": name, **payload})
        if payload.get("ok") is False and not payload.get("optional"):
            report["ok"] = False
        if payload.get("blocked"):
            report["blocked"] = True

    pf = _preflight(repo)
    branch = str(pf.get("branch") or _current_branch(repo) or "")
    wt = str(pf.get("working_tree") or "")
    chapter_id = infer_chapter_id(repo, pf)
    report["preflight"] = {
        "branch": branch,
        "working_tree": wt,
        "blocker": pf.get("blocker"),
        "chapter_id": chapter_id,
    }

    if branch == "HEAD":
        step("branch", {"ok": False, "blocked": True, "reason": "detached HEAD"})
        return report

    if pf.get("blocker") and "unmerged" in str(pf.get("blocker") or "").lower():
        step("conflicts", {"ok": False, "blocked": True, "reason": pf.get("blocker")})
        return report

    dirty = committable_dirty_paths(repo)
    if pf.get("mixed_plane_dirty") and dirty:
        try:
            from scripts.ppe_parked_work import write_parked_work

            write_parked_work(repo, reason="mixed_plane", thread_role="closeout", note="context closeout blocked")
        except Exception:
            pass
        step(
            "mixed_plane",
            {
                "ok": False,
                "blocked": True,
                "reason": "mixed-plane dirty; parked for deliberate reconciliation",
                "paths": dirty[:12],
            },
        )
        report["parked"] = dirty
        return report

    if wt == "clean" or not dirty:
        current = _current_branch(repo) or branch
        ahead = _ahead_count(repo, current)
        if ahead > 0:
            pub = _publish(repo, chapter_id=chapter_id, branch=current, dry_run=dry_run)
            step("chapter_publish", pub)
        else:
            step("clean", {"ok": True, "reason": "working tree clean; nothing to publish"})
        return report

    if dry_run:
        step(
            "ship",
            {
                "ok": True,
                "dry_run": True,
                "chapter_id": chapter_id,
                "paths": dirty,
                "message": _commit_message_for_paths(dirty),
            },
        )
        return report

    ok_branch, work_branch, branch_detail = _ensure_chapter_branch(repo, current=branch, chapter_id=chapter_id)
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

    ok_commit, commit_detail = _commit(repo, message=_commit_message_for_paths(dirty))
    step("commit", {"ok": ok_commit, "detail": commit_detail})
    if not ok_commit:
        _unstage_all(repo)
        report["blocked"] = True
        return report

    pre_ok, pre_detail = _run_gate(repo, dirty, pre_push=True)
    step("pre_push_gate", {"ok": pre_ok, "detail": pre_detail})
    if not pre_ok:
        report["blocked"] = True
        return report

    pub = _publish(repo, chapter_id=chapter_id, branch=work_branch)
    step("chapter_publish", pub)
    if not pub.get("ok"):
        report["blocked"] = True
    return report
