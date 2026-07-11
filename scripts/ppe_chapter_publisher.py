"""Bounded Git publication: one chapter, one branch, one pull request.

This is the supported replacement for timestamped loop-publish, vm-mirror, and
closeout branches. It is intentionally explicit and fail-closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

CHAPTER_MARKER = "ppe-chapter-id"
STATE_REL = "artifacts/control_plane/CHAPTER_PUBLICATION_STATE.json"
AUTO_PR_PREFIXES = ("ops/loop-publish-", "ops/vm-mirror-", "ops/closeout-")
MAX_AUTO_PRS_OPEN = 5
MAX_AUTO_PRS_30_MIN = 3

RUNTIME_ONLY_EXACT = frozenset(
    {
        "docs/SOP/VM_OPERATOR_PHASE.json",
        "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
        "docs/SOP/PHASE_QUEUE.json",
        "docs/SOP/PHASE_CHAPTER_BACKLOG.json",
        "docs/SOP/PHASE_SELECTION_ROADMAP.json",
        "docs/SOP/AGENT_CONTINUITY_BRIEF.md",
        "docs/SOP/HANDOFF.md",
        "docs/SOP/PPE_INTEGRATED_STATUS.md",
    }
)
RUNTIME_ONLY_PREFIXES = ("artifacts/", "docs/RELEASES/")


@dataclass(frozen=True)
class PublicationDecision:
    allowed: bool
    reason: str
    existing_pr: dict[str, Any] | None = None


def _run(argv: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run(["git", *args], cwd=repo)


def _gh(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run(["gh", *args], cwd=repo)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def slugify_chapter_id(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("chapter id must contain letters or numbers")
    return slug[:72]


def chapter_branch(chapter_id: str) -> str:
    return f"chapter/{slugify_chapter_id(chapter_id)}"


def chapter_marker(chapter_id: str) -> str:
    return f"<!-- {CHAPTER_MARKER}: {slugify_chapter_id(chapter_id)} -->"


def extract_chapter_id(body: str) -> str:
    match = re.search(rf"<!--\s*{re.escape(CHAPTER_MARKER)}:\s*([a-z0-9-]+)\s*-->", body or "", re.I)
    return match.group(1).lower() if match else ""


def is_runtime_only_path(path: str) -> bool:
    p = path.replace("\\", "/").strip()
    if p in RUNTIME_ONLY_EXACT:
        return True
    if any(p.startswith(prefix) for prefix in RUNTIME_ONLY_PREFIXES):
        return True
    if p.startswith("docs/SOP/PHASE_") and p.endswith(".json"):
        return True
    if p.startswith("docs/SOP/") and p.endswith("_EVIDENCE_STATUS.md"):
        return True
    return False


def runtime_only_paths(paths: Iterable[str]) -> list[str]:
    return sorted({p for p in paths if is_runtime_only_path(p)})


def current_branch(repo: Path) -> str:
    proc = _git(repo, "branch", "--show-current")
    return (proc.stdout or "").strip() if proc.returncode == 0 else ""


def head_sha(repo: Path) -> str:
    proc = _git(repo, "rev-parse", "HEAD")
    return (proc.stdout or "").strip() if proc.returncode == 0 else ""


def changed_paths(repo: Path, *, base: str = "origin/main") -> list[str]:
    proc = _git(repo, "diff", "--name-only", f"{base}...HEAD")
    if proc.returncode != 0:
        proc = _git(repo, "diff", "--name-only", "main...HEAD")
    return [line.strip().replace("\\", "/") for line in (proc.stdout or "").splitlines() if line.strip()]


def semantic_hash(repo: Path, *, base: str = "origin/main") -> str:
    proc = _git(repo, "diff", "--binary", f"{base}...HEAD")
    if proc.returncode != 0:
        proc = _git(repo, "diff", "--binary", "main...HEAD")
    return hashlib.sha256((proc.stdout or "").encode("utf-8")).hexdigest()


def list_open_prs(repo: Path) -> list[dict[str, Any]]:
    proc = _gh(
        repo,
        "pr",
        "list",
        "--state",
        "open",
        "--limit",
        "200",
        "--json",
        "number,headRefName,headRefOid,createdAt,title,body,url,isDraft",
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "gh pr list failed").strip())
    data = json.loads(proc.stdout or "[]")
    return data if isinstance(data, list) else []


def is_automatic_pr(pr: dict[str, Any]) -> bool:
    head = str(pr.get("headRefName") or "")
    body = str(pr.get("body") or "")
    return head.startswith(AUTO_PR_PREFIXES) or "Auto-published" in body or "Auto-shipped" in body


def evaluate_circuit_breakers(
    prs: list[dict[str, Any]],
    *,
    chapter_id: str,
    branch: str,
    sha: str,
    now: datetime | None = None,
) -> PublicationDecision:
    now = now or _utc_now()
    chapter = slugify_chapter_id(chapter_id)
    auto_prs = [pr for pr in prs if is_automatic_pr(pr)]
    if len(auto_prs) > MAX_AUTO_PRS_OPEN:
        return PublicationDecision(False, f"circuit_open: {len(auto_prs)} autonomous PRs already open")

    recent = 0
    for pr in auto_prs:
        created = _parse_time(str(pr.get("createdAt") or ""))
        if created and created >= now - timedelta(minutes=30):
            recent += 1
    if recent >= MAX_AUTO_PRS_30_MIN:
        return PublicationDecision(False, f"circuit_open: {recent} autonomous PRs created in 30 minutes")

    same_sha = [pr for pr in prs if sha and str(pr.get("headRefOid") or "") == sha]
    if len(same_sha) > 1:
        return PublicationDecision(False, "circuit_open: duplicate open head SHA")
    if same_sha and str(same_sha[0].get("headRefName") or "") != branch:
        return PublicationDecision(False, "same SHA is already represented by another open PR", same_sha[0])

    same_chapter = [pr for pr in prs if extract_chapter_id(str(pr.get("body") or "")) == chapter]
    if len(same_chapter) > 1:
        return PublicationDecision(False, "circuit_open: multiple open PRs for chapter")
    if same_chapter:
        existing = same_chapter[0]
        if str(existing.get("headRefName") or "") != branch:
            return PublicationDecision(False, "chapter already has an open PR on another branch", existing)
        return PublicationDecision(True, "update_existing_pr", existing)

    return PublicationDecision(True, "create_pr")


def _load_state(repo: Path) -> dict[str, Any]:
    path = repo / STATE_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_state(repo: Path, state: dict[str, Any]) -> None:
    path = repo / STATE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _ensure_branch(repo: Path, *, chapter_id: str, create: bool) -> str:
    current = current_branch(repo)
    desired = chapter_branch(chapter_id)
    if current and current != "main":
        return current
    if not create:
        raise RuntimeError(f"on main; rerun with --create-branch to create {desired}")
    proc = _git(repo, "checkout", "-b", desired)
    if proc.returncode != 0:
        proc = _git(repo, "checkout", desired)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "branch checkout failed").strip())
    return desired


def publish_chapter(
    repo: Path,
    *,
    chapter_id: str,
    title: str,
    body: str = "",
    create_branch_if_main: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    from scripts.ppe_operator_config import chapter_publication_enabled

    if not dry_run and not chapter_publication_enabled():
        return {"ok": False, "blocked": True, "reason": "set PPE_CHAPTER_PUBLISH=1 for explicit publication"}

    branch = _ensure_branch(repo, chapter_id=chapter_id, create=create_branch_if_main)
    paths = changed_paths(repo)
    if not paths:
        return {"ok": True, "skipped": True, "reason": "no durable diff", "branch": branch}
    rejected = runtime_only_paths(paths)
    if rejected:
        return {
            "ok": False,
            "blocked": True,
            "reason": "runtime-only paths cannot be published",
            "runtime_paths": rejected,
        }

    sha = head_sha(repo)
    content_hash = semantic_hash(repo)
    state = _load_state(repo)
    prior = state.get(slugify_chapter_id(chapter_id)) if isinstance(state, dict) else None
    if isinstance(prior, dict) and prior.get("semantic_hash") == content_hash:
        return {"ok": True, "skipped": True, "reason": "semantic content already published", "branch": branch}

    prs = list_open_prs(repo)
    decision = evaluate_circuit_breakers(prs, chapter_id=chapter_id, branch=branch, sha=sha)
    if not decision.allowed:
        return {
            "ok": False,
            "blocked": True,
            "reason": decision.reason,
            "existing_pr": decision.existing_pr,
        }

    marker = chapter_marker(chapter_id)
    pr_body = f"{marker}\n\n{body.strip()}\n\nPublication key: `{slugify_chapter_id(chapter_id)}:{content_hash[:16]}`\n"
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "decision": decision.reason,
            "branch": branch,
            "paths": paths,
            "semantic_hash": content_hash,
            "existing_pr": decision.existing_pr,
        }

    push = _git(repo, "push", "-u", "origin", branch)
    if push.returncode != 0:
        return {"ok": False, "reason": (push.stderr or push.stdout or "git push failed").strip()}

    if decision.existing_pr:
        number = str(decision.existing_pr.get("number") or "")
        proc = _gh(repo, "pr", "edit", number, "--title", title, "--body", pr_body)
        pr_url = str(decision.existing_pr.get("url") or "")
        action = "updated"
    else:
        proc = _gh(repo, "pr", "create", "--base", "main", "--head", branch, "--title", title, "--body", pr_body)
        pr_url = (proc.stdout or "").strip()
        action = "created"
    if proc.returncode != 0:
        return {"ok": False, "reason": (proc.stderr or proc.stdout or "PR operation failed").strip()}

    state[slugify_chapter_id(chapter_id)] = {
        "branch": branch,
        "head_sha": sha,
        "semantic_hash": content_hash,
        "pr_url": pr_url,
        "published_at": _utc_now().isoformat(),
    }
    _save_state(repo, state)
    return {"ok": True, "action": action, "branch": branch, "pr_url": pr_url, "paths": paths}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--chapter-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--create-branch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = publish_chapter(
            Path(args.repo),
            chapter_id=args.chapter_id,
            title=args.title,
            body=args.body,
            create_branch_if_main=args.create_branch,
            dry_run=args.dry_run,
        )
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        result = {"ok": False, "blocked": True, "reason": str(exc)}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
