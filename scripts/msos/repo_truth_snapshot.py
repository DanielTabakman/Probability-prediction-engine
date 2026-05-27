from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)


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


def _parse_prev_snapshot_header(prev_md: str) -> dict[str, str]:
    """
    Best-effort parse of the previous snapshot markdown so the mirror can say
    "what changed since last refresh" without depending on external state.
    """
    out: dict[str, str] = {}
    for ln in prev_md.splitlines():
        s = ln.strip()
        if s.startswith("**Generated (UTC):**"):
            out["generated_at_utc"] = s.split("**Generated (UTC):**", 1)[1].strip()
        elif s.startswith("**Branch:**"):
            out["branch"] = s.split("**Branch:**", 1)[1].strip().strip("`")
        elif s.startswith("**HEAD:**"):
            out["head"] = s.split("**HEAD:**", 1)[1].strip().strip("`")
        if len(out) >= 3:
            break
    return out


def _git_porcelain_status(repo_root: Path) -> tuple[bool | None, list[dict[str, str]]]:
    """
    Returns (working_tree_clean, entries).

    entries: [{path, code, raw}] where code is the 2-char XY porcelain code.
    """
    status = _run_git(repo_root, ["status", "--porcelain"])
    if status.startswith("<git_error"):
        return None, [{"path": "<git_error>", "code": "!!", "raw": status}]
    lines = [ln for ln in status.splitlines() if ln.strip()]
    if not lines:
        return True, []

    entries: list[dict[str, str]] = []
    for ln in lines:
        code = ln[:2] if len(ln) >= 2 else "??"
        # `git status --porcelain` uses a fixed 2-char XY prefix. Some renderers collapse
        # repeated spaces, so avoid relying on a single delimiter column.
        path = ln[2:].strip()
        # Porcelain rename form: "old -> new"
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        entries.append({"path": path, "code": code, "raw": ln})
    return False, entries


def _is_expected_dirty_path(path: str) -> bool:
    p = path.replace("\\", "/").lstrip("./")
    expected_prefixes = (
        "artifacts/",
        ".pytest_cache/",
        "__pycache__/",
        ".ruff_cache/",
        ".mypy_cache/",
    )
    if any(p == pref.rstrip("/") or p.startswith(pref) for pref in expected_prefixes):
        return True
    if p in (".coverage",):
        return True
    if p.endswith(".log") or p.endswith(".sqlite") or p.endswith(".db"):
        return True
    return False


def _first_table_row_value(md: str, *, field: str) -> str | None:
    """
    Best-effort parse of SOP docs that use '| Field | Value |' tables.
    """
    for ln in md.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cols = [c.strip() for c in s.strip("|").split("|")]
        if len(cols) < 2:
            continue
        if cols[0].strip("* ").lower() == field.lower():
            return cols[1].strip()
    return None


def _naming_control_plane_drift_checks(repo_root: Path) -> tuple[bool, list[str]]:
    warnings: list[str] = []
    required_paths = [
        repo_root / "docs" / "SOP" / "GOOGLE_DOCS_CONTROL_PLANE_V1.md",
        repo_root / "scripts" / "sync_msos_repo_truth.py",
        repo_root / "scripts" / "google_docs_sync.py",
        repo_root / "scripts" / "msos" / "repo_truth_snapshot.py",
        repo_root / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json",
        repo_root / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md",
    ]
    for p in required_paths:
        if not p.exists():
            warnings.append(f"Missing expected control-plane file: `{p.as_posix()}`")

    sop = _read_text(repo_root / "docs" / "SOP" / "GOOGLE_DOCS_CONTROL_PLANE_V1.md") or ""
    if "MSOS_REPO_TRUTH_AUTO_START" not in sop or "MSOS_REPO_TRUTH_AUTO_END" not in sop:
        warnings.append("SOP missing marker strings `MSOS_REPO_TRUTH_AUTO_START`/`MSOS_REPO_TRUTH_AUTO_END`.")

    return (len(warnings) > 0), warnings


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
    working_tree_clean, wt_entries = _git_porcelain_status(repo_root)

    manifest = _read_json(repo_root / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json")
    headline, next_sel = _continuity_headline(repo_root)

    # Previous local snapshot (best-effort) for "what changed since last refresh".
    prev_snapshot_path = repo_root / "artifacts" / "msos_repo_truth_snapshot.md"
    prev_md = _read_text(prev_snapshot_path) or ""
    prev = _parse_prev_snapshot_header(prev_md) if prev_md else {}
    prev_head = (prev.get("head") or "").strip()
    prev_generated = (prev.get("generated_at_utc") or "").strip()

    what_changed_lines: list[str] = []
    if prev_head and _SHA_RE.match(prev_head) and _SHA_RE.match(head) and prev_head != head:
        log = _run_git(repo_root, ["log", "--oneline", f"{prev_head}..{head}", "-n", "20"])
        if log and not log.startswith("<git_error"):
            what_changed_lines.append(f"- **Repo commits since last mirror regen:** `{prev_head[:12]}..{head[:12]}`")
            what_changed_lines.extend([f"  - `{ln.strip()}`" for ln in log.splitlines() if ln.strip()])
        else:
            what_changed_lines.append(f"- **Repo HEAD changed since last mirror regen:** `{prev_head}` → `{head}` (commit list unavailable)")
    elif prev_head and prev_head == head:
        what_changed_lines.append(f"- **Repo HEAD unchanged since last mirror regen:** `{head}`")
    else:
        what_changed_lines.append("- **Repo delta since last mirror regen:** unknown (no prior local snapshot found)")

    # Active/selected chapter inference.
    selection_record = None
    manifest_status = None
    if isinstance(manifest, dict):
        selection_record = str(manifest.get("selectionRecord") or "").strip() or None
        manifest_status = str(manifest.get("status") or "").strip() or None

    chapter_value = None
    brief_text = _read_text(repo_root / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md") or ""
    for ln in brief_text.splitlines():
        if ln.strip().startswith("| Chapter |"):
            cols = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cols) >= 2:
                chapter_value = cols[1]
            break

    # Website / deployment witness (best-effort).
    deploy_witness_path = repo_root / "docs" / "SOP" / "VALIDATION_DEPLOY_WITNESS.md"
    deploy_md = _read_text(deploy_witness_path) or ""
    deploy_date = _first_table_row_value(deploy_md, field="Date (UTC)") if deploy_md else None
    deploy_market = _first_table_row_value(deploy_md, field="marketstructureos.com") if deploy_md else None
    deploy_app = _first_table_row_value(deploy_md, field="app.marketstructureos.com") if deploy_md else None

    # Drift checks.
    drift_found, drift_warnings = _naming_control_plane_drift_checks(repo_root)

    # Dirty tree clarity.
    dirty_paths = [e["path"] for e in wt_entries if e.get("path")]
    unexpected_dirty = [p for p in dirty_paths if p and not _is_expected_dirty_path(p)]
    expected_dirty = [p for p in dirty_paths if p and _is_expected_dirty_path(p)]

    is_mid_work = False
    should_block_selection_or_build = False
    if working_tree_clean is False:
        if unexpected_dirty:
            should_block_selection_or_build = True
        else:
            is_mid_work = True

    freshness_verdict = "FRESH"
    master_update_needed = "unknown"
    if headline and "verify after merge" in headline.lower():
        master_update_needed = "unknown (continuity brief indicates HEAD needs verification after merge)"

    blockers: list[str] = []
    if working_tree_clean is False and unexpected_dirty:
        blockers.append("Working tree dirty with non-generated changes.")
    if drift_found:
        blockers.append("Naming/control-plane drift warnings present.")
    if manifest_status == "COMPLETE":
        blockers.append("No active chapter selected (manifest COMPLETE) — steward SELECTION required before BUILD.")

    if should_block_selection_or_build:
        recommended_next_move = "Resolve dirty working tree (commit/stash/revert) before SELECTION/BUILD."
    elif manifest_status == "COMPLETE":
        recommended_next_move = "Run SELECTION and set `docs/SOP/ACTIVE_PHASE_MANIFEST.json` to READY before `run_ppe.cmd`."
    elif manifest_status == "READY":
        recommended_next_move = "Operator can run `run_ppe.cmd` from repo root."
    else:
        recommended_next_move = "Review status and proceed."

    confidence = "high" if (not drift_found and working_tree_clean is not None) else "medium"

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
            "## GOOGLE_DOCS_REFRESH report fields (mirror payload)",
            "",
            f"- **Freshness verdict:** {freshness_verdict}",
            "- **What changed since last refresh:**",
            *what_changed_lines,
            f"- **Active or selected chapter:** {chapter_value or 'unknown'}",
            f"- **Selection record (manifest):** `{selection_record}`" if selection_record else "- **Selection record (manifest):** unknown",
            "- **Validation run:** see `docs/SOP/VALIDATION_EVIDENCE_STATUS.md` (repo) + GitHub CI as applicable",
            "- **Website / deployment witness:**",
            f"  - **Deploy witness date (UTC):** {deploy_date or 'unknown'}",
            f"  - **marketstructureos.com:** {deploy_market or 'unknown'}",
            f"  - **app.marketstructureos.com:** {deploy_app or 'unknown'}",
            f"- **Live Mirror regenerated timestamp:** {generated_at_utc}",
            f"- **Naming/control-plane drift found:** {'YES' if drift_found else 'NO'}",
            f"- **Master update needed:** {master_update_needed}",
            f"- **Known blockers / warnings:** {'; '.join(blockers) if blockers else 'none'}",
            f"- **Recommended next move:** {recommended_next_move}",
            f"- **Confidence:** {confidence}",
            "",
            "## Working tree clarity (dirty-tree diagnosis)",
            "",
            f"- **Dirty files:** {len(dirty_paths)}",
            f"- **Expected dirty:** {len(expected_dirty)}"
            + (f" — {', '.join(f'`{p}`' for p in expected_dirty[:12])}{' …' if len(expected_dirty) > 12 else ''}" if expected_dirty else ""),
            f"- **Unexpected dirty:** {len(unexpected_dirty)}"
            + (
                f" — {', '.join(f'`{p}`' for p in unexpected_dirty[:12])}{' …' if len(unexpected_dirty) > 12 else ''}"
                if unexpected_dirty
                else ""
            ),
            f"- **Mid-work vs unclosed change:** {'mid-work (generated outputs only)' if is_mid_work else 'unclosed change likely' if working_tree_clean is False else 'n/a'}",
            f"- **Should this block SELECTION/BUILD?:** {'YES' if should_block_selection_or_build else 'NO'}",
            "",
            "### Raw git status (porcelain)",
            "",
            "```text",
            "\n".join([e["raw"] for e in wt_entries]) if wt_entries else "(clean)",
            "```",
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
            f"- **Previous mirror regen (local snapshot):** {prev_generated}" if prev_generated else "- **Previous mirror regen (local snapshot):** unknown",
            "",
            "## Active phase manifest (raw)",
            "",
            "```json",
            json.dumps(manifest or {}, indent=2, sort_keys=True),
            "```",
            "",
            "## Naming/control-plane drift details (best-effort)",
            "",
            "```text",
            "\n".join(drift_warnings) if drift_warnings else "none",
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

