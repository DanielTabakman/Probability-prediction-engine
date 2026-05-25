"""Build deterministic MSOS Repo Truth markdown from repo steering docs."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FRONTIER_REL = "docs/SOP/MVP1_FRONTIER.md"
BRIEF_REL = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
CANON_REL = "docs/VISION/PPE_MASTER_MVP1.md"
INTEGRATED_REL = "docs/SOP/PPE_INTEGRATED_STATUS.md"
HANDOFF_REL = "docs/SOP/HANDOFF.md"
CONTINUITY_JSON_REL = "artifacts/control_plane/continuity_brief.json"

MARKER_START = "MSOS_REPO_TRUTH_AUTO_START"
MARKER_END = "MSOS_REPO_TRUTH_AUTO_END"

# Stable section IDs for index (ChatGPT: search "§N" or heading text).
SECTION_INDEX: list[tuple[str, str, str]] = [
    ("0", "INDEX", "Table of contents — start here"),
    ("1", "WHAT_THIS_DOCUMENT_IS", "Purpose, audience, what is included"),
    ("2", "ROLES_CHATGPT_CURSOR_REPO", "Who writes which doc; hard rules"),
    ("3", "SOURCE_OF_TRUTH", "Precedence when docs disagree"),
    ("4", "SNAPSHOT_METADATA", "As-of time, git HEAD, sync slice"),
    ("5", "RIGHT_NOW", "Active BUILD, execution focus, next SELECTION"),
    ("6", "LAST_CLOSED_CHAPTER", "Most recent chapter closeout"),
    ("7", "CLOSED_CHAPTERS", "All archived MVP1 chapters (summary table)"),
    ("8", "ENGINEERING_GATES", "pytest, dual smoke status"),
    ("9", "STEWARD_PARALLEL", "VPS CTA, paid-interest, non-repo work"),
    ("10", "MVP1_PHASE_PLACEMENT", "Phases 1–6 as-built in repo"),
    ("11", "MVP1_CONTRACT_15A", "Product contract vs implementation status"),
    ("12", "CHATGPT_DOC_MAP", "Which repo file to open for which question"),
    ("13", "REPO_PATH_INDEX", "Canonical paths (copy into prompts)"),
]


@dataclass
class SnapshotMeta:
    generated_at: str
    head_sha: str | None
    slice_id: str | None
    pytest_count: int | None
    dual_smoke_run_ids: list[str]
    section15a_drift_warnings: list[str]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_head(repo: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _strip_trailing_separators(text: str) -> str:
    """Remove trailing markdown horizontal rules from extracted doc sections."""
    return re.sub(r"\n*---\s*\n*$", "", text.strip())


def extract_execution_focus(frontier_text: str) -> str:
    m = re.search(
        r"### Current execution focus \(MVP1 framing\)\s*\n(.*?)(?=\n### |\Z)",
        frontier_text,
        flags=re.DOTALL,
    )
    if not m:
        return "_Could not parse execution focus from MVP1_FRONTIER.md._"
    lines = [ln.rstrip() for ln in m.group(1).strip().splitlines()]
    return "\n".join(lines)


def extract_section15a_table(canon_text: str) -> tuple[str, list[dict[str, str]]]:
    """Return markdown table body and parsed rows from §15A."""
    chunk = canon_text[canon_text.find("15A") :] if "15A" in canon_text else canon_text
    m = re.search(
        r"(\| Contract element \| Status \| Notes \|\s*\n\|[-| :]+\|\s*\n(?:\|[^\n]+\|\s*\n)+)",
        chunk,
        flags=re.IGNORECASE,
    )
    if not m:
        return "_§15A table not found in PPE_MASTER_MVP1.md._\n", []

    table_block = m.group(1).strip()
    rows: list[dict[str, str]] = []
    lines = table_block.splitlines()
    if len(lines) < 2:
        return table_block + "\n", rows
    headers = [c.strip() for c in lines[0].strip("|").split("|")]
    for line in lines[2:]:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= len(headers):
            rows.append(dict(zip(headers, cells, strict=False)))
    return table_block + "\n", rows


def parse_brief_chapter(brief_text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, pat in (
        ("chapter", r"\|\s*Chapter\s*\|\s*([^|]+)\|"),
        ("status", r"\|\s*Status\s*\|\s*([^|]+)\|"),
        ("closed", r"\|\s*Closed\s*\|\s*([^|]+)\|"),
        ("next_selection", r"\|\s*Next SELECTION\s*\|\s*([^|]+)\|"),
        ("evidence", r"\|\s*Evidence\s*\|\s*([^|]+)\|"),
    ):
        m = re.search(pat, brief_text, flags=re.IGNORECASE)
        if m:
            out[key] = m.group(1).strip()
    return out


def extract_engineering_gates(integrated_text: str) -> str:
    m = re.search(
        r"## Engineering gates\s*\n(.*?)(?=\n## |\Z)",
        integrated_text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return "_See docs/SOP/PPE_INTEGRATED_STATUS.md § Engineering gates._"
    return _strip_trailing_separators(m.group(1))


def extract_steward_parallel(integrated_text: str) -> str:
    m = re.search(
        r"## Steward parallel checklist\s*\n(.*?)(?=\n## |\Z)",
        integrated_text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return "_See docs/SOP/PPE_INTEGRATED_STATUS.md § Steward parallel._"
    return _strip_trailing_separators(m.group(1))


def extract_next_build(integrated_text: str) -> str:
    m = re.search(
        r"## Next BUILD \(agent lane\)\s*\n\n(.*?)(?=\n## |\Z)",
        integrated_text,
        flags=re.DOTALL,
    )
    if not m:
        return "_Await steward SELECTION — see MVP1_FRONTIER.md._"
    return m.group(1).strip()


def extract_archived_chapters_table(integrated_text: str) -> str:
    m = re.search(
        r"## Archived chapters\s*\n\n(\| Chapter \|.*?(?=\n\n\*\*Post|\n## |\Z))",
        integrated_text,
        flags=re.DOTALL,
    )
    if not m:
        return "_See docs/SOP/PPE_INTEGRATED_STATUS.md § Archived chapters._"
    return _strip_trailing_separators(m.group(1))


def extract_mvp1_phase_placement(frontier_text: str) -> str:
    m = re.search(
        r"### MVP1 Phase placement \(repo-truth\).*?\n(.*?)(?=\n### MVP1 gap|\Z)",
        frontier_text,
        flags=re.DOTALL,
    )
    if not m:
        return "_See docs/SOP/MVP1_FRONTIER.md § MVP1 Phase placement._"
    text = m.group(1).strip()
    # Cap length for Google Doc readability
    lines = text.splitlines()
    if len(lines) > 45:
        text = "\n".join(lines[:45]) + "\n\n_…truncated; full detail in repo MVP1_FRONTIER.md_"
    return text


def build_index_section() -> str:
    lines = [
        "| § | Section ID | What you get |",
        "|---|------------|--------------|",
    ]
    for num, sec_id, desc in SECTION_INDEX:
        lines.append(f"| {num} | `{sec_id}` | {desc} |")
    lines.append("")
    lines.append(
        "**How to use this index (ChatGPT):** Ask about a topic → find the § row above → "
        "scroll to the matching `## §N — SECTION_ID` heading. Do not read the whole doc linearly."
    )
    return "\n".join(lines)


def build_chatgpt_doc_map() -> str:
    return """| If you need… | Read in repo (authoritative) | Not in MSOS |
|--------------|------------------------------|-------------|
| Product vision, MVP1 contract, scope boundaries | `docs/VISION/PPE_MASTER_MVP1.md` | MSOS mirrors §15A only |
| What to build next (slice queue) | `docs/SOP/MVP1_FRONTIER.md` | MSOS summarizes "right now" |
| Cross-chapter status one-pager | `docs/SOP/PPE_INTEGRATED_STATUS.md` | MSOS copies tables |
| Session handoff gate | `docs/SOP/HANDOFF.md` | — |
| How Google Docs roles work | `docs/SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md` | — |
| Implementation code | `src/viz/`, `tests/` | — |
| Update **PPE Master** (Google) | You (ChatGPT) from repo — **never** MSOS | Cursor owns MSOS |
| Update **MSOS** (this doc) | Cursor `sync_msos_repo_truth_v1` after closeout | You do not edit MSOS |"""


def build_repo_path_index() -> str:
    return """**Control plane**
- `docs/VISION/PPE_MASTER_MVP1.md` — product canon (import target when Google Master changes)
- `docs/SOP/MVP1_FRONTIER.md` — live steering / slice queue
- `docs/SOP/PPE_INTEGRATED_STATUS.md` — archived chapters + gates
- `docs/SOP/HANDOFF.md` — handoff gate block
- `docs/SOP/AGENT_CONTINUITY_BRIEF.md` — generated; Cursor loads first
- `docs/SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md` — MSOS vs Master roles

**Next steward step (typical)**
- `docs/SOP/POST_MVP1_ONBOARDING_HOW_IT_WORKS_SELECTION.md` — deferred SELECTION prep

**Evidence (last closed chapter example)**
- `docs/SOP/MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md`

**Product surface**
- `src/viz/app.py` — BTC Implied Lab UI
- `src/viz/mvp1_decision_surface.py` — candidate / watch_only / no_trade
- `src/viz/frozen_evaluation_store.py` — freeze + review persistence

**Automation**
- `scripts/sync_msos_repo_truth.py` — regenerates this doc block
- `scripts/post_relay_continue.py` — closeout + MSOS chain"""


def load_continuity_json(repo: Path) -> dict[str, Any] | None:
    p = repo / CONTINUITY_JSON_REL
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return None


def build_snapshot_markdown(
    repo_root: Path,
    *,
    closeout: dict[str, Any] | None = None,
) -> tuple[str, SnapshotMeta]:
    repo = repo_root.resolve()
    generated_at = _iso_now()
    head = git_head(repo)

    continuity = load_continuity_json(repo)
    closeout = closeout or (continuity or {}).get("closeout") or {}
    slice_id = closeout.get("slice_id")
    pytest_count = closeout.get("pytest_count")
    dual_ids = list(closeout.get("dual_smoke_run_ids") or [])

    paths = {
        "frontier": repo / FRONTIER_REL,
        "brief": repo / BRIEF_REL,
        "canon": repo / CANON_REL,
        "integrated": repo / INTEGRATED_REL,
        "handoff": repo / HANDOFF_REL,
    }
    texts = {
        k: p.read_text(encoding="utf-8-sig") if p.is_file() else ""
        for k, p in paths.items()
    }

    execution_focus = extract_execution_focus(texts["frontier"])
    section15a_md, _rows = extract_section15a_table(texts["canon"])
    brief_chapter = parse_brief_chapter(texts["brief"])
    archived_table = extract_archived_chapters_table(texts["integrated"])
    eng_gates = extract_engineering_gates(texts["integrated"])
    steward_parallel = extract_steward_parallel(texts["integrated"])
    next_build = extract_next_build(texts["integrated"])
    phase_placement = extract_mvp1_phase_placement(texts["frontier"])

    drift_warnings: list[str] = []
    if closeout.get("chapter_title") and brief_chapter.get("chapter"):
        if closeout["chapter_title"].strip() not in brief_chapter["chapter"]:
            drift_warnings.append(
                f"closeout chapter_title {closeout['chapter_title']!r} "
                f"vs brief {brief_chapter['chapter']!r}"
            )

    meta = SnapshotMeta(
        generated_at=generated_at,
        head_sha=head,
        slice_id=slice_id,
        pytest_count=pytest_count,
        dual_smoke_run_ids=dual_ids,
        section15a_drift_warnings=drift_warnings,
    )

    chapter_lines = []
    if brief_chapter:
        for k, label in (
            ("chapter", "Chapter"),
            ("status", "Status"),
            ("closed", "Closed"),
            ("next_selection", "Next SELECTION"),
            ("evidence", "Evidence"),
        ):
            if k in brief_chapter:
                chapter_lines.append(f"- **{label}:** {brief_chapter[k]}")
    elif closeout:
        chapter_lines.append(
            f"- **Chapter:** {closeout.get('chapter_title', '—')} — "
            f"**{closeout.get('chapter_status', '—')}** {closeout.get('closed_date', '')}"
        )
    else:
        chapter_lines.append("- _No AGENT_CONTINUITY_BRIEF chapter table found._")

    health_extra = []
    if pytest_count is not None:
        health_extra.append(f"- **pytest (closeout spec):** {pytest_count} passed")
    if dual_ids:
        health_extra.append(f"- **dual smoke (closeout):** {', '.join(dual_ids)}")

    md = f"""# MSOS Repo Truth — live mirror (auto-generated)

**Document version:** v1 iteration · **Sync:** `sync_msos_repo_truth_v1` · **Regenerated:** {generated_at}

---

## §0 — INDEX

{build_index_section()}

---

## §1 — WHAT_THIS_DOCUMENT_IS

**MSOS Repo Truth** is the **as-built, repo-grounded status document** for the Probability Prediction Engine (PPE) / Market Structure OS program. It answers: *what exists in the repository today*, *what chapter just closed*, *what is blocked*, and *where to look next*.

**This document is NOT:**
- Product canon (use **PPE Master** Google Doc or `docs/VISION/PPE_MASTER_MVP1.md`)
- A slice queue for Cursor BUILD (use `docs/SOP/MVP1_FRONTIER.md`)
- A place for ChatGPT to edit (Cursor replaces the block between markers)

**This document INCLUDES (sections §0–§13):**
- Index for fast navigation
- Role split (ChatGPT vs Cursor vs repo)
- Current execution focus and next SELECTION
- Closed chapters summary
- Engineering gates (pytest, smoke)
- Steward parallel (VPS, paid-interest)
- MVP1 phase placement (what landed in `src/`)
- §15A contract-vs-repo table (excerpt)
- Doc map and repo path index

**Maintained by:** Cursor automation after relay chapter closeout. **You (ChatGPT)** update **PPE Master** from repo when canon/audit changes.

---

## §2 — ROLES_CHATGPT_CURSOR_REPO

| Actor | PPE Master (Google) | MSOS Repo Truth (this doc) | Repo `docs/` |
|--------|---------------------|----------------------------|--------------|
| **Cursor** | Read only | Write auto block only | Closeout patches `docs/SOP/*` |
| **ChatGPT / founder** | Write (canon, audit, strategy) | Do not edit | Import Master → `PPE_MASTER_MVP1.md` when needed |
| **Disputes** | Steward decides | Report only | **Pushed repo wins**; frontier wins queue |

**ChatGPT typical workflow:** Read this doc §5–§7 for status → open repo paths from §12 for depth → update PPE Master → optional re-import to `PPE_MASTER_MVP1.md`.

---

## §3 — SOURCE_OF_TRUTH

Order (highest first):

1. Pushed repo + accepted docs on `main`
2. `docs/VISION/PPE_MASTER_MVP1.md` (MVP1 product canon)
3. `docs/SOP/MVP1_FRONTIER.md` (live slice queue — wins if HANDOFF drifts)
4. `docs/SOP/PPE_INTEGRATED_STATUS.md` (cross-chapter one-pager)
5. `docs/SOP/HANDOFF.md`
6. `docs/SOP/OPERATING_RULES.md`

MSOS is a **mirror** for convenience; if MSOS disagrees with repo files, **trust the repo**.

---

## §4 — SNAPSHOT_METADATA

| Field | Value |
|-------|-------|
| **As-of (UTC)** | {generated_at} |
| **Git HEAD** | `{head or "unknown"}` |
| **Closeout slice** | `{slice_id or "n/a"}` |
| **Drift warnings** | {", ".join(drift_warnings) if drift_warnings else "none"} |

---

## §5 — RIGHT_NOW

### Execution focus (from MVP1_FRONTIER)

{execution_focus}

### Active BUILD

{next_build}

{chr(10).join(health_extra) if health_extra else ""}

---

## §6 — LAST_CLOSED_CHAPTER

{chr(10).join(chapter_lines)}

---

## §7 — CLOSED_CHAPTERS

{archived_table}

---

## §8 — ENGINEERING_GATES

{eng_gates}

---

## §9 — STEWARD_PARALLEL

{steward_parallel}

---

## §10 — MVP1_PHASE_PLACEMENT

{phase_placement}

---

## §11 — MVP1_CONTRACT_15A

Excerpt from `docs/VISION/PPE_MASTER_MVP1.md` §15A (repo-truth table). Target spec remains §15 in Master.

{section15a_md}

---

## §12 — CHATGPT_DOC_MAP

{build_chatgpt_doc_map()}

---

## §13 — REPO_PATH_INDEX

{build_repo_path_index()}

---

_End of auto block · Markers: `{MARKER_START}` / `{MARKER_END}` · SOP: `docs/SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md`_
"""
    return md, meta


def write_snapshot_artifact(repo_root: Path, markdown: str, meta: SnapshotMeta) -> Path:
    repo = repo_root.resolve()
    out_dir = repo / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "msos_repo_truth_snapshot.md"
    md_path.write_text(markdown, encoding="utf-8")

    cp_dir = repo / "artifacts" / "control_plane"
    cp_dir.mkdir(parents=True, exist_ok=True)
    sidecar = {
        "generated_at": meta.generated_at,
        "head_sha": meta.head_sha,
        "slice_id": meta.slice_id,
        "pytest_count": meta.pytest_count,
        "dual_smoke_run_ids": meta.dual_smoke_run_ids,
        "section15a_drift_warnings": meta.section15a_drift_warnings,
        "snapshot_path": md_path.as_posix(),
        "section_index": [{"id": s[1], "title": s[2]} for s in SECTION_INDEX],
    }
    (cp_dir / "msos_snapshot_meta.json").write_text(
        json.dumps(sidecar, indent=2),
        encoding="utf-8",
    )
    return md_path


def compose_google_doc_markdown(snapshot_md: str) -> str:
    """Wrap snapshot with stable doc shell + sync markers for Google Docs."""
    body = snapshot_md.strip()
    return f"""# MSOS Repo Truth

**As-built mirror** of the Probability Prediction Engine repository — for **ChatGPT** and operators.

- **Start here:** open the auto block below → **§0 — INDEX** → jump to the section you need.
- **You (ChatGPT):** update **PPE Master** from repo; **do not edit** this document (Cursor maintains it).
- **Control plane SOP (repo):** `docs/SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md`

{MARKER_START}

{body}

{MARKER_END}
"""


def build_and_write(repo_root: Path, *, closeout: dict[str, Any] | None = None) -> tuple[str, SnapshotMeta, Path]:
    md, meta = build_snapshot_markdown(repo_root, closeout=closeout)
    path = write_snapshot_artifact(repo_root, md, meta)
    return md, meta, path
