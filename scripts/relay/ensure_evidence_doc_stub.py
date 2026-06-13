"""Create PENDING evidence-doc stubs when a relay chapter is selected (closeout hardening)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_phase_plan


def _closeout_from_plan(plan: dict[str, Any]) -> dict[str, Any] | None:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and isinstance(sl.get("closeout"), dict):
            return sl["closeout"]
    return None


def _slice_table_rows(plan: dict[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        sid = str(sl.get("sliceId") or "").strip()
        if not sid:
            continue
        plane = str(sl.get("declaredPlane") or sl.get("layerPreset") or "—").strip()
        rows.append((sid, plane))
    return rows


def build_evidence_stub_md(
    *,
    chapter_id: str,
    chapter_title: str,
    phase_plan_path: str,
    sprint_spec: str,
    slice_rows: list[tuple[str, str]],
) -> str:
    plan_name = Path(phase_plan_path).name
    sprint_name = Path(sprint_spec).name if sprint_spec else sprint_spec
    table_lines = ["| Slice | Status | Notes |", "|-------|--------|-------|"]
    for sid, plane in slice_rows:
        table_lines.append(f"| {sid} | PENDING | {plane} |")
    table = "\n".join(table_lines)
    return f"""# {chapter_title} — evidence status

**Chapter:** `{chapter_id}`
**Status:** **PENDING**
**Phase plan:** [`{plan_name}`]({phase_plan_path})
**Sprint:** [`{sprint_name}`]({sprint_spec})

{table}

## Share checklist (operator)

- [ ] Chapter COMPLETE on `main` after PR merge
- [ ] Evidence doc updated on closeout
"""


def ensure_evidence_doc_stub(repo_root: Path, phase_plan_path: str) -> dict[str, Any]:
    """Write a PENDING evidence stub when the plan closeout block names a missing doc."""
    repo = repo_root.resolve()
    norm_plan = str(phase_plan_path or "").replace("\\", "/").strip()
    if not norm_plan:
        return {"skipped": True, "reason": "empty phase_plan_path"}

    try:
        plan = load_phase_plan(repo, norm_plan)
    except (FileNotFoundError, OSError) as exc:
        return {"skipped": True, "reason": f"plan load failed: {exc}"}

    closeout = _closeout_from_plan(plan)
    if not closeout:
        return {"skipped": True, "reason": "no closeout block"}

    evidence_rel = str(closeout.get("evidenceDoc") or "").replace("\\", "/").strip()
    if not evidence_rel:
        return {"skipped": True, "reason": "closeout missing evidenceDoc"}

    path = repo / evidence_rel
    if path.is_file():
        return {"skipped": True, "reason": "exists", "path": evidence_rel}

    chapter_id = str(closeout.get("chapterId") or plan.get("name") or "chapter").strip()
    chapter_title = str(closeout.get("chapterTitle") or chapter_id).strip()
    sprint_spec = str(
        closeout.get("sprintSpec") or plan.get("sprintSpecPath") or ""
    ).replace("\\", "/").strip()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_evidence_stub_md(
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            phase_plan_path=norm_plan,
            sprint_spec=sprint_spec,
            slice_rows=_slice_table_rows(plan),
        ),
        encoding="utf-8",
    )
    return {"created": True, "path": evidence_rel}
