"""Tests for scripts.relay.steering_alignment."""

from __future__ import annotations

from pathlib import Path

from scripts.relay.steering_alignment import check_steering_alignment


def test_steering_aligned_fixture(tmp_path: Path) -> None:
    """Golden path: aligned HANDOFF / FRONTIER / INTEGRATED + evidence (isolated repo)."""
    sop = tmp_path / "docs" / "SOP"
    sop.mkdir(parents=True)
    next_sel = "docs/SOP/POST_GOLDEN_SELECTION.md"
    frontier = f"""### Current execution focus (MVP1 framing)
- **Integrated status (one-pager):** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
- **Active BUILD chapter:** **none** — await steward **SELECTION** ([`POST_GOLDEN_SELECTION.md`]({next_sel}))
- **Last closed chapter:** **Golden Chapter** — **COMPLETE** 2026-05-20
- **Steward parallel:** pending
"""
    gate = f"""```text
- Next pending execution step: **steward SELECTION** — `{next_sel}`
- Last closed chapter: **Golden Chapter** — **COMPLETE** 2026-05-20
```"""
    (sop / "MVP1_FRONTIER.md").write_text(frontier, encoding="utf-8")
    (sop / "HANDOFF.md").write_text(f"# H\n\n## HANDOFF GATE\n\n{gate}\n", encoding="utf-8")
    (sop / "PPE_INTEGRATED_STATUS.md").write_text(
        f"| Golden Chapter | **COMPLETE** 2026-05-20 | evidence |\n\n"
        f"**Next chapter SELECTION:** [`POST_GOLDEN_SELECTION.md`]({next_sel})\n\n"
        f"## Next BUILD (agent lane)\n\n[`POST_GOLDEN_SELECTION.md`]({next_sel})\n",
        encoding="utf-8",
    )
    (sop / "GOLDEN_EVIDENCE.md").write_text(
        "## Chapter status\n\n**Golden Chapter:** **COMPLETE** 2026-05-20.\n", encoding="utf-8"
    )
    report = check_steering_alignment(
        tmp_path,
        expected_chapter_title="Golden Chapter",
        expected_closed_date="2026-05-20",
        expected_next_selection=next_sel,
        expected_evidence_doc="docs/SOP/GOLDEN_EVIDENCE.md",
    )
    assert report.passed, report.findings


def test_steering_fails_when_evidence_has_pending_slices(tmp_path: Path) -> None:
    sop = tmp_path / "docs" / "SOP"
    sop.mkdir(parents=True)
    for name in ("HANDOFF.md", "MVP1_FRONTIER.md", "PPE_INTEGRATED_STATUS.md"):
        (sop / name).write_text("# stub\n", encoding="utf-8")
    evidence = sop / "BAD_EVIDENCE.md"
    evidence.write_text(
        "# evidence\n\n**Status:** **COMPLETE** 2026-06-27\n\n| Slice | Status |\n|-------|--------|\n| X | PENDING |\n",
        encoding="utf-8",
    )
    report = check_steering_alignment(
        tmp_path,
        expected_chapter_title="Bad Chapter",
        expected_closed_date="2026-06-27",
        expected_evidence_doc="docs/SOP/BAD_EVIDENCE.md",
    )
    assert not report.passed
    assert any(f.check == "evidence_pending_slices" for f in report.findings)


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
