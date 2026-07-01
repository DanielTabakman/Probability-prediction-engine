"""Tests for SOP discovery tier-7 maintenance."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.sop_discovery_core import (
    backfill_evidence_front_matter,
    build_chapter_doc_index,
    evidence_doc_archived,
    parse_evidence_front_matter,
    plan_evidence_front_matter_backfill,
    stamp_evidence_archived_frontmatter,
)
from scripts.ppe_ide_build_starter import plan_regen_ready_starters, regenerate_starters_for_ready_queue


class TestEvidenceArchiveSignals(unittest.TestCase):
    def test_parse_front_matter(self) -> None:
        text = "---\narchived: true\nchapter_id: foo_v1\nclosed: 2026-06-01\n---\n\n# Body\n"
        fm = parse_evidence_front_matter(text)
        self.assertTrue(fm.get("archived"))
        self.assertEqual(fm.get("chapter_id"), "foo_v1")

    def test_evidence_doc_archived_from_complete_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            sop.mkdir(parents=True)
            rel = "docs/SOP/TEST_EVIDENCE_STATUS.md"
            (repo / rel).write_text(
                "# Test\n\n**Status:** **COMPLETE** 2026-06-01\n",
                encoding="utf-8",
            )
            self.assertTrue(evidence_doc_archived(repo, rel))

    def test_backfill_plan_and_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            plans = sop / "PHASE_PLANS"
            sop.mkdir(parents=True)
            plans.mkdir(parents=True)
            plan_rel = "docs/SOP/PHASE_PLANS/done_chapter_v1_relay.json"
            evidence_rel = "docs/SOP/DONE_CHAPTER_V1_EVIDENCE_STATUS.md"
            (plans / "done_chapter_v1_relay.json").write_text(
                json.dumps(
                    {
                        "slices": [
                            {
                                "sliceId": "Closeout",
                                "closeout": {"evidenceDoc": evidence_rel},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (repo / evidence_rel).write_text(
                "# Done\n\n**Chapter:** `done_chapter_v1`\n**Status:** **COMPLETE** 2026-06-02\n",
                encoding="utf-8",
            )
            (sop / "PHASE_QUEUE.json").write_text(
                json.dumps({"items": [{"planPath": plan_rel, "status": "DONE"}]}),
                encoding="utf-8",
            )
            plan = plan_evidence_front_matter_backfill(repo)
            self.assertEqual(plan["pending_count"], 1)
            out = backfill_evidence_front_matter(repo, apply=True)
            self.assertEqual(out["stamped_count"], 1)
            text = (repo / evidence_rel).read_text(encoding="utf-8")
            self.assertIn("archived: true", text)

    def test_complete_without_queue_done_not_backfilled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            plans = sop / "PHASE_PLANS"
            sop.mkdir(parents=True)
            plans.mkdir(parents=True)
            evidence_rel = "docs/SOP/ACTIVE_V1_EVIDENCE_STATUS.md"
            (plans / "active_v1_relay.json").write_text(
                json.dumps(
                    {
                        "slices": [
                            {"sliceId": "Closeout", "closeout": {"evidenceDoc": evidence_rel}},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (repo / evidence_rel).write_text(
                "# Active\n\n**Status:** **COMPLETE** 2026-06-01\n",
                encoding="utf-8",
            )
            (sop / "PHASE_QUEUE.json").write_text(
                json.dumps(
                    {
                        "items": [
                            {
                                "planPath": "docs/SOP/PHASE_PLANS/active_v1_relay.json",
                                "status": "READY",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            plan = plan_evidence_front_matter_backfill(repo)
            self.assertEqual(plan["pending_count"], 0)

    def test_archived_index_uses_front_matter_when_queue_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            plans = sop / "PHASE_PLANS"
            sop.mkdir(parents=True)
            plans.mkdir(parents=True)
            plan_rel = "docs/SOP/PHASE_PLANS/active_chapter_v1_relay.json"
            evidence_rel = "docs/SOP/ACTIVE_CHAPTER_V1_EVIDENCE_STATUS.md"
            (plans / "active_chapter_v1_relay.json").write_text(
                json.dumps(
                    {
                        "slices": [
                            {
                                "sliceId": "Closeout",
                                "closeout": {"evidenceDoc": evidence_rel},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (repo / evidence_rel).write_text("# Active\n\n**Status:** **ACTIVE**\n", encoding="utf-8")
            (sop / "PHASE_QUEUE.json").write_text(json.dumps({"items": []}), encoding="utf-8")
            stamp_evidence_archived_frontmatter(
                repo,
                evidence_rel,
                chapter_id="active_chapter_v1",
                closed_date="2026-06-03",
            )
            index = build_chapter_doc_index(repo)
            row = index["by_chapter_id"]["active_chapter_v1"]
            self.assertTrue(row["archived"])


class TestReadyStarterRegenPlan(unittest.TestCase):
    def test_plan_regen_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            sop.mkdir(parents=True)
            (sop / "PHASE_QUEUE.json").write_text(
                json.dumps(
                    {
                        "items": [
                            {"planPath": "docs/SOP/PHASE_PLANS/a.json", "status": "READY"},
                            {"planPath": "docs/SOP/PHASE_PLANS/b.json", "status": "DONE"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            plan = plan_regen_ready_starters(repo)
            self.assertEqual(plan["pending_count"], 0)
            out = regenerate_starters_for_ready_queue(repo)
            self.assertIsInstance(out, dict)


if __name__ == "__main__":
    unittest.main()
