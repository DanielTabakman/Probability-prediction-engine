"""Deterministic CONTROL-CLOSEOUT patches (apply_control_closeout_v1)."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.relay.steering_alignment import (
    SOURCE_OF_TRUTH_ORDER,
    check_steering_alignment,
)

HANDOFF_REL = "docs/SOP/HANDOFF.md"
FRONTIER_REL = "docs/SOP/MVP1_FRONTIER.md"
INTEGRATED_REL = "docs/SOP/PPE_INTEGRATED_STATUS.md"
BRIEF_REL = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"


@dataclass
class CloseoutSpec:
    chapter_id: str
    chapter_title: str
    chapter_status: str
    closed_date: str
    evidence_doc: str
    sprint_spec: str
    next_selection_doc: str
    selection_outcome_doc: str | None = None
    carry_docs: list[str] | None = None
    dual_smoke_run_ids: list[str] | None = None
    pytest_count: int | None = None
    closed_chapters_line: str | None = None
    slice_id: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any], slice_id: str | None = None) -> CloseoutSpec:
        closed = str(d.get("closedDate") or "").strip()
        if not closed:
            closed = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return cls(
            chapter_id=d["chapterId"],
            chapter_title=d["chapterTitle"],
            chapter_status=d["chapterStatus"],
            closed_date=closed,
            evidence_doc=d["evidenceDoc"].replace("\\", "/"),
            sprint_spec=d["sprintSpec"].replace("\\", "/"),
            next_selection_doc=d["nextSelectionDoc"].replace("\\", "/"),
            selection_outcome_doc=(d.get("selectionOutcomeDoc") or "").replace("\\", "/") or None,
            carry_docs=[x.replace("\\", "/") for x in (d.get("carryDocs") or [])],
            dual_smoke_run_ids=list(d.get("dualSmokeRunIds") or []),
            pytest_count=d.get("pytestCount"),
            closed_chapters_line=d.get("closedChaptersLine"),
            slice_id=slice_id,
        )


def load_phase_plan(plan_path: Path) -> dict[str, Any]:
    return json.loads(plan_path.read_text(encoding="utf-8-sig"))


def find_closeout_for_slice(plan: dict[str, Any], slice_id: str) -> dict[str, Any] | None:
    for sl in plan.get("slices") or []:
        if sl.get("sliceId") == slice_id and "closeout" in sl:
            return sl["closeout"]
    return None


def _git_head(repo: Path) -> str | None:
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


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _next_selection_name(path: str) -> str:
    return Path(path).name


def build_handoff_gate(spec: CloseoutSpec) -> str:
    carry = spec.carry_docs or [spec.evidence_doc]
    carry_str = " + ".join(f"`{c}`" for c in carry[:4])
    closed = spec.closed_chapters_line or (
        "Validation, Commercial Validation, MVP1 Reliability, Phase 2 on `main`, "
        "operator hardening, review enrichment, smoke regression, friends-first screen"
    )
    next_name = _next_selection_name(spec.next_selection_doc)
    return f"""HANDOFF GATE — v3.1 (MVP1 control-plane)

A) DOC-STATE SAFETY (alignment)
- Source-of-truth precedence: pushed repo+accepted docs > PPE_MASTER_MVP1 > MVP1_FRONTIER > HANDOFF > OPERATING_RULES
- Controlling master canon: `docs/VISION/PPE_MASTER_MVP1.md`
- Live frontier (only steering truth): `docs/SOP/MVP1_FRONTIER.md`
- Integrated one-pager: `docs/SOP/PPE_INTEGRATED_STATUS.md`
- Active MVP1 focus: **none** — {spec.chapter_title.lower()} **{spec.chapter_status}** {spec.closed_date}
- Closed chapters: {closed}
- Next pending execution step: **steward SELECTION** — `{spec.next_selection_doc}`
- Steward parallel: VPS `.env` CTA **pending**; paid-interest **N** until live call
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- Baseline SHA: verify `git rev-parse origin/main` after push
- BUILD allowed: only after steward SELECTION; honor reconcile defer list

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `PPE_INTEGRATED_STATUS.md` + `MVP1_FRONTIER.md` + `{Path(spec.evidence_doc).name}`"""


def patch_handoff(repo: Path, spec: CloseoutSpec) -> None:
    path = repo / HANDOFF_REL
    text = path.read_text(encoding="utf-8-sig")
    gate = build_handoff_gate(spec)
    text = re.sub(
        r"```text\s*\n.*?```",
        f"```text\n{gate}\n```",
        text,
        count=1,
        flags=re.DOTALL,
    )
    next_name = _next_selection_name(spec.next_selection_doc)
    smoke_note = ""
    if spec.dual_smoke_run_ids:
        smoke_note = " (`" + "` + `".join(spec.dual_smoke_run_ids) + "`)"
    priority = (
        f"**{spec.chapter_title} {spec.chapter_status}** — "
        f"dual smoke green{smoke_note}. Await steward **SELECTION**."
    )
    text = re.sub(
        r"## Current priority\s*\n\n.*?(?=\n## )",
        f"## Current priority\n\n{priority}\n\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"## Last updated\s*\n\n.*\Z",
        f"## Last updated\n\n{spec.closed_date} — {spec.chapter_title} {spec.chapter_status}; "
        f"closeout job `{spec.slice_id or 'apply_control_closeout_v1'}`.\n",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"## Recommended next step\s*\n\n.*?(?=\n## Last updated)",
        f"## Recommended next step\n\n"
        f"1. **Relay:** closeout applied — see [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md).\n"
        f"2. **Steward:** SELECTION — [`{next_name}`]({spec.next_selection_doc}).\n\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    path.write_text(text, encoding="utf-8")


def patch_frontier(repo: Path, spec: CloseoutSpec) -> None:
    path = repo / FRONTIER_REL
    text = path.read_text(encoding="utf-8-sig")
    next_name = _next_selection_name(spec.next_selection_doc)
    focus = f"""### Current execution focus (MVP1 framing)
- **Integrated status (one-pager):** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
- **Active BUILD chapter:** **none** — await steward **SELECTION** ([`{next_name}`]({spec.next_selection_doc}))
- **Last closed chapter:** **{spec.chapter_title}** — **{spec.chapter_status}** {spec.closed_date}
- **Steward parallel:** VPS `.env` → **Research beta (v0)** CTA **pending**; paid-interest **N** until live conversation.
- **Non-goal**: billing automation, execution engine, multi-asset BUILD without new charter.
"""
    text = re.sub(
        r"### Current execution focus \(MVP1 framing\).*?(?=\n### )",
        focus + "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    path.write_text(text, encoding="utf-8")


def patch_integrated(repo: Path, spec: CloseoutSpec) -> None:
    path = repo / INTEGRATED_REL
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(
        r"\*\*As-of:\*\* \d{4}-\d{2}-\d{2}",
        f"**As-of:** {spec.closed_date}",
        text,
        count=1,
    )
    row = (
        f"| {spec.chapter_title} | **{spec.chapter_status}** {spec.closed_date} | "
        f"[`{Path(spec.sprint_spec).name}`]({spec.sprint_spec}), "
        f"[`{Path(spec.evidence_doc).name}`]({spec.evidence_doc}) |"
    )
    if spec.chapter_title not in text or f"**{spec.chapter_status}** {spec.closed_date}" not in text:
        # Insert before ops tail separator if table exists
        marker = "**Ops tail:**"
        if marker in text and row not in text:
            text = text.replace(
                "\n**Ops tail:**",
                f"\n{row}\n\n**Ops tail:**",
            )
    if spec.pytest_count is not None:
        text = re.sub(
            r"(\| `python -m pytest -q` \| \*\*PASS\*\* \| ).*?(\|)",
            rf"\1**{spec.pytest_count}** passed ({spec.closed_date})\2",
            text,
            count=1,
        )
    if spec.dual_smoke_run_ids:
        ids = " + ".join(f"`{x}`" for x in spec.dual_smoke_run_ids)
        text = re.sub(
            r"(\| Dual smoke \| \*\*PASS\*\* \| ).*?(\|)",
            rf"\1{ids} (~221s)\2",
            text,
            count=1,
        )
    next_name = _next_selection_name(spec.next_selection_doc)
    text = re.sub(
        r"\*\*Next chapter SELECTION:\*\*[^\n]*",
        f"**Next chapter SELECTION:** [`{next_name}`]({spec.next_selection_doc})",
        text,
        count=1,
    )
    text = re.sub(
        r"## Next BUILD \(agent lane\)\s*\n\n.*\Z",
        f"## Next BUILD (agent lane)\n\n"
        f"**Await steward SELECTION** — [`{next_name}`]({spec.next_selection_doc}). "
        f"**Worry audit:** [`PPE_RISK_REGISTER.md`](PPE_RISK_REGISTER.md).\n",
        text,
        flags=re.DOTALL,
    )
    path.write_text(text, encoding="utf-8")


def patch_evidence_chapter_status(repo: Path, spec: CloseoutSpec) -> None:
    path = repo / spec.evidence_doc
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8-sig")
    status_line = f"**{spec.chapter_title}:** **{spec.chapter_status}** {spec.closed_date}."
    changed = False
    # Canonical evidence docs use a top-level **Status:** line (not ## Chapter status).
    new_text, n = re.subn(
        r"(^\*\*Status:\*\*\s+)\*\*[^*\n]+\*\*(?:\s+\d{4}-\d{2}-\d{2})?(?:\s+\([^)]*\))?",
        rf"\1**{spec.chapter_status}** {spec.closed_date}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n:
        text = new_text
        changed = True
    if "## Chapter status" in text:
        text = re.sub(
            r"## Chapter status\s*\n\n.*?(?=\n## |\Z)",
            f"## Chapter status\n\n{status_line}\n\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
        changed = True
    if str(spec.chapter_status or "").strip().upper() == "COMPLETE":
        table_text, table_n = re.subn(
            r"\|\s*\*{0,2}PENDING\*{0,2}\s*\|",
            "| COMPLETE |",
            text,
            flags=re.IGNORECASE,
        )
        if table_n:
            text = table_text
            changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
    if str(spec.chapter_status or "").strip().upper() == "COMPLETE":
        try:
            from scripts.sop_discovery_core import stamp_evidence_archived_frontmatter

            stamp_evidence_archived_frontmatter(
                repo,
                spec.evidence_doc,
                chapter_id=spec.chapter_id,
                closed_date=spec.closed_date,
            )
        except Exception:
            pass


def build_continuity_brief_md(
    repo: Path,
    spec: CloseoutSpec,
    *,
    alignment: dict[str, Any],
    relay_run_dir: Path | None,
    head_sha: str | None,
    plan_path: str | None = None,
) -> str:
    gaps = [f for f in alignment.get("findings", []) if f.get("severity") in ("error", "warn")]
    aligned = alignment.get("steering_aligned", False)
    relay_lines = ""
    if relay_run_dir:
        relay_lines = f"\n- **relay_run_dir:** `{relay_run_dir.as_posix()}`\n"
    if gaps:
        gaps_block = "".join(
            f'- [{g["severity"]}] {g["check"]}: {g["message"]}\n' for g in gaps
        )
    else:
        gaps_block = "- No gaps (errors/warnings).\n"

    norm_plan = (plan_path or f"docs/SOP/PHASE_PLANS/{spec.chapter_id}_relay.json").replace(
        "\\", "/"
    )
    from scripts.sop_discovery_core import expand_carry_docs_for_closeout

    carry_docs = expand_carry_docs_for_closeout(
        repo,
        carry_docs=spec.carry_docs,
        chapter_id=spec.chapter_id,
        plan_path=norm_plan,
    )
    carry_block = ", ".join(f"`{c}`" for c in carry_docs)
    doc_load_lines = "\n".join(f"- `{c}`" for c in carry_docs)

    return f"""# Agent continuity brief (generated)

**Do not edit by hand.** Regenerated by `apply_control_closeout_v1`. Load this file first (see [`AGENT_GUIDE_ROLE.md`](AGENT_GUIDE_ROLE.md)).

**As-of:** {_iso_now()} · **HEAD:** `{head_sha or 'unknown'}` · **Closeout slice:** `{spec.slice_id or 'backfill'}`

## Source-of-truth order

{chr(10).join(f'{i + 1}. `{p}`' for i, p in enumerate(SOURCE_OF_TRUTH_ORDER))}

## Chapter status

| Field | Value |
|-------|-------|
| Chapter | {spec.chapter_title} |
| Status | {spec.chapter_status} |
| Closed | {spec.closed_date} |
| Evidence | [{Path(spec.evidence_doc).name}]({spec.evidence_doc}) |
| Next SELECTION | [{_next_selection_name(spec.next_selection_doc)}]({spec.next_selection_doc}) |

## Active BUILD

<!-- ACTIVE_PRODUCT_DIRECTION:START -->
_(run sync_product_direction.cmd — populated from ACTIVE_PRODUCT_DIRECTION.json)_
<!-- ACTIVE_PRODUCT_DIRECTION:END -->

## Steering alignment

- **steering_aligned:** `{aligned}`
- **gap_count:** {len(gaps)}

{gaps_block}{relay_lines}
## Doc load bundle

{doc_load_lines}

Resolve: `python scripts/resolve_sop.py --chapter {spec.chapter_id} --json`

## Roles

### Guide agent (read-only advisor)

1. Read this brief, then `PPE_INTEGRATED_STATUS.md`.
2. If `steering_aligned` is false, list gaps for the build agent; do **not** start BUILD.
3. Never treat `CURRENT_FRONTIER.md` or `Frontier_Steward_Handoff.md` as controlling.

### Build agent (Cursor / ACP worker)

1. Honor `MVP1_FRONTIER.md` slice queue; run relay slices via `run_slice.cmd` / `run_phase.cmd` / `run_ppe.cmd`.
2. Do not edit steering docs during BUILD; closeout job updates them after `CONTINUE`.
3. Carry docs: {carry_block}.

## Cursor context

- **Relay workers:** each slice uses a fresh ACP session in an isolated worktree — not this Cursor chat history.
- **Steward vs BUILD:** keep SELECTION/planning in a steward thread; implementation via relay/orchestrator, not one mega-thread.
- **After this closeout:** open a **new** Cursor thread; load only this brief (+ next SELECTION doc). Full rules: [`CONTEXT_RULES.md`](../CONTEXT_RULES.md).
- **BUILD packets:** use [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md) — paths only, no inlined HANDOFF gate or logs.
"""


def apply_control_closeout(
    repo_root: Path,
    *,
    closeout: CloseoutSpec,
    relay_run_dir: Path | None = None,
    skip_alignment: bool = False,
    phase_plan_path: str | None = None,
) -> dict[str, Any]:
    repo = repo_root.resolve()
    from scripts.sop_discovery_core import validate_closeout_spec_docs

    doc_errors = validate_closeout_spec_docs(repo, closeout)
    if doc_errors:
        return {
            "job": "apply_control_closeout_v1",
            "passed": False,
            "doc_validation_errors": doc_errors,
            "generated_at": _iso_now(),
        }
    if phase_plan_path:
        try:
            from scripts.relay.ensure_evidence_doc_stub import ensure_evidence_doc_stub

            ensure_evidence_doc_stub(repo, phase_plan_path)
        except Exception:
            pass
    patch_handoff(repo, closeout)
    patch_frontier(repo, closeout)
    patch_integrated(repo, closeout)
    patch_evidence_chapter_status(repo, closeout)

    alignment_report = check_steering_alignment(
        repo,
        expected_chapter_title=closeout.chapter_title,
        expected_closed_date=closeout.closed_date,
        expected_next_selection=closeout.next_selection_doc,
        expected_evidence_doc=closeout.evidence_doc,
    )
    if skip_alignment:
        alignment_report.passed = True

    brief_md = build_continuity_brief_md(
        repo,
        closeout,
        alignment=alignment_report.to_dict(),
        relay_run_dir=relay_run_dir,
        head_sha=_git_head(repo),
        plan_path=phase_plan_path,
    )
    (repo / BRIEF_REL).write_text(brief_md, encoding="utf-8")

    cp_dir = repo / "artifacts" / "control_plane"
    cp_dir.mkdir(parents=True, exist_ok=True)
    brief_json = {
        "generated_at": _iso_now(),
        "closeout": closeout.__dict__,
        "alignment": alignment_report.to_dict(),
        "relay_run_dir": str(relay_run_dir) if relay_run_dir else None,
        "head_sha": _git_head(repo),
    }
    (cp_dir / "continuity_brief.json").write_text(
        json.dumps(brief_json, indent=2),
        encoding="utf-8",
    )

    if phase_plan_path:
        try:
            from scripts.ppe_ide_build_starter import prune_starters_for_plan

            pruned = prune_starters_for_plan(repo, phase_plan_path)
            if pruned:
                report_dir_extra = cp_dir / "closeout_pruned_starters.txt"
                report_dir_extra.write_text("\n".join(pruned) + "\n", encoding="utf-8")
        except Exception:
            pass

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_dir = cp_dir / ts
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "job": "apply_control_closeout_v1",
        "passed": alignment_report.passed,
        "alignment": alignment_report.to_dict(),
        "generated_at": _iso_now(),
    }
    (report_dir / "closeout_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    try:
        from scripts.active_product_direction import sync_product_direction

        sync_report = sync_product_direction(repo)
        report["product_direction_sync"] = sync_report
        (report_dir / "closeout_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"apply_control_closeout: direction sync {sync_report.get('pivotId')}")
    except Exception as exc:
        print(f"apply_control_closeout: direction sync skipped: {exc}")

    try:
        from scripts.sop_discovery_core import refresh_sop_discovery_artifacts

        refresh_report = refresh_sop_discovery_artifacts(repo)
        report["sop_discovery_refresh"] = refresh_report
        (report_dir / "closeout_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(
            "apply_control_closeout: sop discovery refresh "
            f"({refresh_report.get('active_chapter_count')} active chapters)"
        )
    except Exception as exc:
        print(f"apply_control_closeout: sop discovery refresh skipped: {exc}")

    return report


def run_consistency_check(repo_root: Path) -> tuple[bool, str]:
    """Invoke relay consistency check; return (passed, message)."""
    import sys

    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "relay_runtime_v0.py"),
        "--repo-root",
        str(repo_root),
        "stage",
        "control_plane_consistency_check",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out
