"""Steering-doc alignment checks (deterministic, no LLM).

Hard gates for apply_control_closeout_v1; also runnable standalone and via pytest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

Severity = Literal["error", "warn", "info"]

SOURCE_OF_TRUTH_ORDER = [
    "docs/VISION/PPE_MASTER_MVP1.md",
    "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json",
    "docs/SOP/MVP1_FRONTIER.md",
    "docs/SOP/PPE_INTEGRATED_STATUS.md",
    "docs/SOP/HANDOFF.md",
    "docs/SOP/OPERATING_RULES.md",
]

HANDOFF_PATH = "docs/SOP/HANDOFF.md"
FRONTIER_PATH = "docs/SOP/MVP1_FRONTIER.md"
INTEGRATED_PATH = "docs/SOP/PPE_INTEGRATED_STATUS.md"
PROMPTS_DIR = "docs/CONTROL_PLANE/PROMPTS"


@dataclass
class AlignmentFinding:
    check: str
    severity: Severity
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"check": self.check, "severity": self.severity, "message": self.message}


@dataclass
class AlignmentReport:
    passed: bool
    findings: list[AlignmentFinding] = field(default_factory=list)
    parsed: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "findings": [f.to_dict() for f in self.findings],
            "parsed": self.parsed,
            "steering_aligned": self.passed
            and not any(f.severity == "error" for f in self.findings),
        }


def _read(repo: Path, rel: str) -> str:
    return (repo / rel).read_text(encoding="utf-8-sig")


def _extract_handoff_gate(text: str) -> dict[str, str]:
    m = re.search(r"```text\s*\n(.*?)```", text, re.DOTALL)
    block = m.group(1) if m else ""
    out: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- Active MVP1 focus:"):
            out["active_focus"] = line
        if line.startswith("- Last closed chapter:") or "Last closed" in line and "chapter" in line.lower():
            out["last_closed"] = line
        if "Next pending execution step:" in line or "Next pending" in line:
            out["next_step"] = line
        if "Closed chapters:" in line:
            out["closed_chapters"] = line
    return out


def _extract_frontier_focus(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    section = re.search(
        r"### Current execution focus.*?\n(.*?)(?=\n### |\Z)",
        text,
        re.DOTALL,
    )
    body = section.group(1) if section else ""
    for line in body.splitlines():
        s = line.strip()
        if "**Active BUILD chapter:**" in s:
            out["active_build"] = s
        if "**Last closed chapter:**" in s:
            out["last_closed"] = s
        if "SELECTION" in s and "POST_" in s:
            out["next_selection_line"] = s
    return out


def _normalize_post_path(path: str) -> str:
    path = path.replace("\\", "/")
    if path.startswith("docs/SOP/"):
        return path
    return f"docs/SOP/{path.lstrip('/')}"


def _frontier_execution_focus_section(text: str) -> str:
    m = re.search(
        r"### Current execution focus.*?\n(.*?)(?=\n### )",
        text,
        re.DOTALL,
    )
    return m.group(1) if m else text


def _extract_next_selection_from_frontier(text: str) -> str | None:
    section = _frontier_execution_focus_section(text)
    m = re.search(
        r"Active BUILD chapter:.*?SELECTION.*?\]\((?:docs/SOP/)?(POST_[^)]+)\)",
        section,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        return _normalize_post_path(m.group(1))
    m2 = re.search(
        r"Active BUILD chapter:.*?\]\((?:docs/SOP/)?([^)]+)\)",
        section,
        re.IGNORECASE | re.DOTALL,
    )
    if m2:
        p = m2.group(1)
        if "POST_" in p or p.endswith(".md"):
            return _normalize_post_path(p)
    return None


def _extract_next_selection_from_handoff_gate(text: str) -> str | None:
    block = _extract_handoff_gate(text)
    step = block.get("next_step", "")
    m = re.search(r"`(docs/SOP/POST_[^`]+)`", step)
    if m:
        return m.group(1)
    m2 = re.search(r"(docs/SOP/POST_[^\s`]+)", step)
    return m2.group(1) if m2 else None


def _extract_next_selection_from_integrated(text: str) -> str | None:
    m = re.search(
        r"\*\*Next chapter SELECTION:\*\*.*?\]\((?:docs/SOP/)?(POST_[^)]+)\)",
        text,
        re.DOTALL,
    )
    if m:
        return _normalize_post_path(m.group(1))
    m2 = re.search(
        r"## Next BUILD \(agent lane\).*?\]\((?:docs/SOP/)?(POST_[^)]+)\)",
        text,
        re.DOTALL,
    )
    return _normalize_post_path(m2.group(1)) if m2 else None


def _chapter_row_in_integrated(text: str, chapter_title: str) -> bool:
    # Match table row containing chapter title fragment
    frag = chapter_title.replace("MVP1 ", "").split("—")[0].strip()[:30]
    for line in text.splitlines():
        if "|" in line and frag.lower() in line.lower() and "COMPLETE" in line:
            return True
    return chapter_title.lower() in text.lower() and "COMPLETE" in text


def _legacy_prompt_refs(repo: Path) -> list[str]:
    hits: list[str] = []
    prompts = repo / PROMPTS_DIR
    if not prompts.is_dir():
        return hits
    for p in prompts.glob("*.md"):
        t = p.read_text(encoding="utf-8-sig")
        if "CURRENT_FRONTIER.md" in t and "historical" not in t.lower()[:200]:
            hits.append(str(p.relative_to(repo)).replace("\\", "/"))
    return hits


def check_steering_alignment(
    repo_root: Path,
    *,
    expected_chapter_title: str | None = None,
    expected_closed_date: str | None = None,
    expected_next_selection: str | None = None,
    expected_evidence_doc: str | None = None,
) -> AlignmentReport:
    repo = repo_root.resolve()
    findings: list[AlignmentFinding] = []

    handoff = _read(repo, HANDOFF_PATH)
    frontier = _read(repo, FRONTIER_PATH)
    integrated = _read(repo, INTEGRATED_PATH)

    hg = _extract_handoff_gate(handoff)
    ff = _extract_frontier_focus(frontier)

    next_f = _extract_next_selection_from_frontier(frontier)
    next_h = _extract_next_selection_from_handoff_gate(handoff)
    next_i = _extract_next_selection_from_integrated(integrated)

    parsed = {
        "handoff_gate": hg,
        "frontier_focus": ff,
        "next_selection": {"frontier": next_f, "handoff": next_h, "integrated": next_i},
    }

    if next_f and next_h and next_f != next_h:
        findings.append(
            AlignmentFinding(
                "next_selection",
                "error",
                f"FRONTIER next SELECTION {next_f!r} != HANDOFF {next_h!r}",
            )
        )
    if next_f and next_i and next_f != next_i:
        findings.append(
            AlignmentFinding(
                "next_selection",
                "error",
                f"FRONTIER next SELECTION {next_f!r} != INTEGRATED {next_i!r}",
            )
        )

    if ff.get("last_closed") and hg.get("last_closed"):
        # Normalize: both should mention same chapter title if expected set
        if expected_chapter_title:
            if expected_chapter_title not in ff["last_closed"]:
                findings.append(
                    AlignmentFinding(
                        "last_closed_chapter",
                        "error",
                        f"FRONTIER missing chapter {expected_chapter_title!r}",
                    )
                )
            if expected_chapter_title not in handoff and expected_chapter_title not in hg.get(
                "last_closed", ""
            ):
                findings.append(
                    AlignmentFinding(
                        "last_closed_chapter",
                        "error",
                        f"HANDOFF missing chapter {expected_chapter_title!r}",
                    )
                )
        if expected_closed_date:
            if expected_closed_date not in ff.get("last_closed", ""):
                findings.append(
                    AlignmentFinding(
                        "last_closed_date",
                        "error",
                        f"FRONTIER missing closed date {expected_closed_date}",
                    )
                )

    if expected_chapter_title and not _chapter_row_in_integrated(integrated, expected_chapter_title):
        findings.append(
            AlignmentFinding(
                "integrated_chapter_row",
                "error",
                f"PPE_INTEGRATED_STATUS missing COMPLETE row for {expected_chapter_title!r}",
            )
        )

    if expected_evidence_doc:
        ev_path = repo / expected_evidence_doc
        if not ev_path.is_file():
            findings.append(
                AlignmentFinding(
                    "evidence_doc",
                    "error",
                    f"Evidence doc missing: {expected_evidence_doc}",
                )
            )
        else:
            ev_text = ev_path.read_text(encoding="utf-8-sig")
            if "COMPLETE" not in ev_text:
                findings.append(
                    AlignmentFinding(
                        "evidence_complete",
                        "error",
                        f"{expected_evidence_doc} does not contain COMPLETE",
                    )
                )
            if expected_closed_date and expected_closed_date not in ev_text:
                findings.append(
                    AlignmentFinding(
                        "evidence_date",
                        "warn",
                        f"{expected_evidence_doc} missing date {expected_closed_date}",
                    )
                )

    if expected_next_selection:
        norm = expected_next_selection.replace("\\", "/")
        for label, path in [("frontier", next_f), ("handoff", next_h), ("integrated", next_i)]:
            if path and norm not in path and path.split("/")[-1] not in norm:
                findings.append(
                    AlignmentFinding(
                        "next_selection_expected",
                        "error",
                        f"{label} next selection {path!r} != expected {norm}",
                    )
                )

    for ref in _legacy_prompt_refs(repo):
        findings.append(
            AlignmentFinding(
                "legacy_prompt_drift",
                "info",
                f"CONTROL_PLANE prompt still references CURRENT_FRONTIER: {ref}",
            )
        )

    errors = [f for f in findings if f.severity == "error"]
    return AlignmentReport(passed=len(errors) == 0, findings=findings, parsed=parsed)


def main() -> int:
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(description="Steering alignment check")
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--chapter-title", default=None)
    p.add_argument("--closed-date", default=None)
    p.add_argument("--next-selection", default=None)
    p.add_argument("--evidence-doc", default=None)
    args = p.parse_args()
    report = check_steering_alignment(
        args.repo_root,
        expected_chapter_title=args.chapter_title,
        expected_closed_date=args.closed_date,
        expected_next_selection=args.next_selection,
        expected_evidence_doc=args.evidence_doc,
    )
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
