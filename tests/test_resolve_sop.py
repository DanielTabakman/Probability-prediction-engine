"""Tests for SOP / chapter doc discovery."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.sop_discovery_core import (
    build_chapter_doc_index,
    build_program_doc_index,
    chapter_doc_index_fresh,
    expand_carry_docs_for_closeout,
    format_operator_resolve_lines,
    list_topics,
    refresh_sop_discovery_artifacts,
    resolve_by_chapter,
    resolve_by_role,
    resolve_by_search,
    resolve_by_topic,
    search_sop_docs,
    write_archive_index,
    write_chapter_doc_index,
)


class TestResolveSop(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        plans = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True, exist_ok=True)
        plans.mkdir(parents=True, exist_ok=True)
        plan_rel = "docs/SOP/PHASE_PLANS/ppe_exposure_menu_v1_relay.json"
        (plans / "ppe_exposure_menu_v1_relay.json").write_text(
            json.dumps(
                {
                    "sprintSpecPath": "docs/SOP/SPRINT_PPE_EXPOSURE_MENU_V1.md",
                    "selectionRecord": "docs/SOP/POST_PPE_EXPOSURE_MENU_V1_SELECTION.md",
                    "slices": [
                        {
                            "sliceId": "Closeout",
                            "closeout": {
                                "evidenceDoc": "docs/SOP/PPE_EXPOSURE_MENU_V1_EVIDENCE_STATUS.md",
                                "sprintSpec": "docs/SOP/SPRINT_PPE_EXPOSURE_MENU_V1.md",
                                "selectionOutcomeDoc": "docs/SOP/POST_PPE_EXPOSURE_MENU_V1_SELECTION.md",
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "SPRINT_PPE_EXPOSURE_MENU_V1.md").write_text("# sprint\n", encoding="utf-8")
        (sop / "POST_PPE_EXPOSURE_MENU_V1_SELECTION.md").write_text("# sel\n", encoding="utf-8")
        (sop / "PPE_EXPOSURE_MENU_V1_EVIDENCE_STATUS.md").write_text("# ev\n", encoding="utf-8")
        (sop / "EXPOSURE_MENU_PROGRAM_V1.md").write_text("# program\n", encoding="utf-8")
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps({"items": [{"planPath": plan_rel, "status": "DONE"}]}),
            encoding="utf-8",
        )
        self.plan_rel = plan_rel

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_archived_counts(self) -> None:
        index = build_chapter_doc_index(self.repo)
        self.assertEqual(index["active_chapter_count"], 0)
        self.assertEqual(index["archived_chapter_count"], 1)
        self.assertTrue(index["by_chapter_id"]["ppe_exposure_menu_v1"]["archived"])

    def test_list_topics(self) -> None:
        topics = list_topics()
        self.assertIn("asset_batch", {t["id"] for t in topics})
        self.assertIn("steward_selection", {t["id"] for t in topics})

    def test_expand_carry_docs_for_closeout(self) -> None:
        expanded = expand_carry_docs_for_closeout(
            self.repo,
            carry_docs=["docs/SOP/PPE_EXPOSURE_MENU_V1_EVIDENCE_STATUS.md"],
            chapter_id="ppe_exposure_menu_v1",
            plan_path=self.plan_rel,
        )
        self.assertIn("docs/SOP/POST_PPE_EXPOSURE_MENU_V1_SELECTION.md", expanded)

    def test_resolve_by_chapter(self) -> None:
        report = resolve_by_chapter(self.repo, chapter_id="ppe_exposure_menu_v1")
        self.assertTrue(report["ok"])

    def test_resolve_by_topic_asset_batch(self) -> None:
        report = resolve_by_topic("asset batch wave 1")
        self.assertEqual(report["topic_route_id"], "asset_batch")

    def test_resolve_by_role_operator(self) -> None:
        report = resolve_by_role("operator")
        self.assertTrue(report["ok"])
        self.assertIn("OPERATOR_STATUS.md", report["load_always"][0])

    def test_resolve_by_role_unknown(self) -> None:
        report = resolve_by_role("invalid")
        self.assertFalse(report["ok"])

    def test_write_index(self) -> None:
        out = write_chapter_doc_index(self.repo)
        self.assertTrue(out.is_file())
        archive = self.repo / "docs" / "SOP" / "ARCHIVE_INDEX.md"
        self.assertTrue(archive.is_file())
        self.assertIn("ppe_exposure_menu_v1", archive.read_text(encoding="utf-8"))

    def test_chapter_doc_index_fresh_after_write(self) -> None:
        write_chapter_doc_index(self.repo)
        fresh, reason = chapter_doc_index_fresh(self.repo)
        self.assertTrue(fresh, reason)

    def test_chapter_doc_index_stale_when_missing(self) -> None:
        fresh, reason = chapter_doc_index_fresh(self.repo)
        self.assertFalse(fresh)
        self.assertIn("missing", reason)

    def test_write_archive_index(self) -> None:
        data = build_chapter_doc_index(self.repo)
        out = write_archive_index(self.repo, data=data)
        text = out.read_text(encoding="utf-8")
        self.assertIn("Do not load for BUILD", text)
        self.assertIn("ppe_exposure_menu_v1", text)

    def test_refresh_returns_archive_path(self) -> None:
        report = refresh_sop_discovery_artifacts(self.repo)
        self.assertTrue(report.get("archive_index_path"))
        self.assertTrue((self.repo / report["archive_index_path"]).is_file())

    def test_search_exposure_menu(self) -> None:
        (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
            json.dumps({"items": [{"planPath": self.plan_rel, "status": "PLANNED"}]}),
            encoding="utf-8",
        )
        hits = search_sop_docs(self.repo, "exposure menu")
        self.assertTrue(any(h.get("chapter_id") == "ppe_exposure_menu_v1" for h in hits))

    def test_resolve_by_search_single_chapter(self) -> None:
        (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
            json.dumps({"items": [{"planPath": self.plan_rel, "status": "PLANNED"}]}),
            encoding="utf-8",
        )
        report = resolve_by_search(self.repo, "ppe_exposure_menu_v1")
        self.assertTrue(report.get("ok"))
        self.assertEqual(report.get("chapter_id"), "ppe_exposure_menu_v1")

    def test_format_operator_resolve_lines(self) -> None:
        lines = format_operator_resolve_lines(
            self.repo,
            plan_path=self.plan_rel,
        )
        self.assertTrue(any("resolve_sop.py --chapter" in line for line in lines))

    def test_program_doc_index(self) -> None:
        data = build_program_doc_index(self.repo)
        self.assertGreaterEqual(data["program_count"], 1)
        mods = {row["module_id"] for row in data["programs"]}
        self.assertIn("exposure_menu", mods)


if __name__ == "__main__":
    unittest.main()
