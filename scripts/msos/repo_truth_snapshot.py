from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_git(repo_root: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if proc.returncode != 0:
        # best-effort: keep going with a readable placeholder
        return f"<git_error code={proc.returncode} stdout={out!r} stderr={err!r}>"
    return out


def _read_text(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _read_json(p: Path) -> Any | None:
    t = _read_text(p)
    if t is None:
        return None
    try:
        return json.loads(t)
    except Exception:
        return None


@dataclass(frozen=True)
class RepoTruthSnapshot:
    generated_at_utc: str
    branch: str
    head: str
    working_tree_clean: bool | None
    active_phase_manifest: dict[str, Any] | None
    continuity_brief_headline: str | None
    continuity_next_selection_rel: str | None
    snapshot_markdown: str


def _infer_working_tree_clean(repo_root: Path) -> bool | None:
    status = _run_git(repo_root, ["status", "--porcelain"])
    if status.startswith("<git_error"):
        return None
    return status.strip() == ""


def _continuity_headline(repo_root: Path) -> tuple[str | None, str | None]:
    """
    Returns:
      - headline: one line summary (best-effort)
      - next_selection_rel: link target from the brief, if found
    """
    p = repo_root / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md"
    t = _read_text(p)
    if not t:
        return None, None
    headline = None
    next_sel = None
    for line in t.splitlines():
        s = line.strip()
        if s.startswith("**As-of:**"):
            headline = s
        if s.startswith("| Next SELECTION |") and "](" in s:
            # table row: | Next SELECTION | [`foo`](bar) |
            try:
                next_sel = s.split("](", 1)[1].split(")", 1)[0]
            except Exception:
                pass
    return headline, next_sel


def build_repo_truth_snapshot(*, repo_root: Path) -> RepoTruthSnapshot:
    repo_root = repo_root.resolve()
    generated_at_utc = _utc_now_iso()
    branch = _run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    head = _run_git(repo_root, ["rev-parse", "HEAD"])
    working_tree_clean = _infer_working_tree_clean(repo_root)

    manifest = _read_json(repo_root / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json")
    headline, next_sel = _continuity_headline(repo_root)

    snapshot_md = "\n".join(
        [
            "MSOS_REPO_TRUTH_AUTO_START",
            "# PPE / MSOS Repo Truth — Live Mirror (auto-generated)",
            "",
            f"**Generated (UTC):** {generated_at_utc}",
            f"**Branch:** `{branch}`",
            f"**HEAD:** `{head}`",
            f"**Working tree:** {'clean' if working_tree_clean else 'dirty' if working_tree_clean is False else 'unknown'}",
            "",
            "## Quick links (repo)",
            "",
            "- `docs/SOP/AGENT_CONTINUITY_BRIEF.md`",
            "- `docs/SOP/MVP1_FRONTIER.md`",
            "- `docs/SOP/PPE_INTEGRATED_STATUS.md`",
            "- `docs/SOP/HANDOFF.md`",
            "- `docs/SOP/ACTIVE_PHASE_MANIFEST.json`",
            "",
            "## Right now (best-effort)",
            "",
            f"- **Continuity headline:** {headline or 'N/A'}",
            f"- **Next SELECTION (from brief):** `{next_sel}`" if next_sel else "- **Next SELECTION (from brief):** N/A",
            "",
            "## Active phase manifest (raw)",
            "",
            "```json",
            json.dumps(manifest or {}, indent=2, sort_keys=True),
            "```",
            "",
            "_This snapshot is repo-grounded reporting. It is not product canon. Canon lives in PPE Master; repo canon lives in `docs/VISION/PPE_MASTER_MVP1.md`._",
            "",
            "MSOS_REPO_TRUTH_AUTO_END",
            "",
        ]
    )

    return RepoTruthSnapshot(
        generated_at_utc=generated_at_utc,
        branch=branch,
        head=head,
        working_tree_clean=working_tree_clean,
        active_phase_manifest=manifest if isinstance(manifest, dict) else None,
        continuity_brief_headline=headline,
        continuity_next_selection_rel=next_sel,
        snapshot_markdown=snapshot_md,
    )

