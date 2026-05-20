"""Tests for scripts.relay.steering_alignment."""

from __future__ import annotations

from pathlib import Path

from scripts.relay.steering_alignment import check_steering_alignment


def test_steering_aligned_friends_first() -> None:
    """Golden path: current repo steering docs agree on friends-first chapter."""
    repo_root = Path(__file__).resolve().parents[1]
    report = check_steering_alignment(
        repo_root,
        expected_chapter_title="MVP1 friends-first screen",
        expected_closed_date="2026-05-20",
        expected_next_selection="docs/SOP/POST_MVP1_FRIENDS_FIRST_SELECTION.md",
        expected_evidence_doc="docs/SOP/MVP1_FRIENDS_FIRST_EVIDENCE_STATUS.md",
    )
    assert report.passed, report.findings


def test_next_selection_mismatch_detected(tmp_path: Path) -> None:
    handoff = tmp_path / "docs" / "SOP"
    handoff.mkdir(parents=True)
    frontier = """### Current execution focus (MVP1 framing)
- **Active BUILD chapter:** **none** — await steward **SELECTION** ([`POST_A.md`](POST_A.md))
- **Last closed chapter:** **Foo** — **COMPLETE** 2026-01-01
"""
    h = """```text
- Next pending execution step: **steward SELECTION** — `docs/SOP/POST_B.md`
```"""
    (handoff / "MVP1_FRONTIER.md").write_text(frontier, encoding="utf-8")
    (handoff / "HANDOFF.md").write_text(f"# HANDOFF\n\n## HANDOFF GATE\n\n{h}\n", encoding="utf-8")
    (handoff / "PPE_INTEGRATED_STATUS.md").write_text(
        "**Next chapter SELECTION:** [`POST_A.md`](POST_A.md)\n", encoding="utf-8"
    )
    report = check_steering_alignment(tmp_path)
    assert not report.passed
    assert any(f.check == "next_selection" for f in report.findings)
