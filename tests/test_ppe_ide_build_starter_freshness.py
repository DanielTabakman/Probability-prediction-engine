"""Tests for IDE BUILD starter doc-resolve freshness (tier 9)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_ide_build_starter import (
    build_starter_md,
    doc_resolve_fingerprint,
    format_resolve_fingerprint_line,
    parse_starter_resolve_fingerprint,
    plan_regen_ready_starters,
    regenerate_starters_for_ready_queue,
    starter_doc_resolve_stale,
    write_starter,
)


def _write_min_plan(repo: Path, *, plan_rel: str, slice_id: str) -> None:
    plans = repo / "docs" / "SOP" / "PHASE_PLANS"
    sop = repo / "docs" / "SOP"
    plans.mkdir(parents=True, exist_ok=True)
    name = Path(plan_rel).name
    (plans / name).write_text(
        json.dumps(
            {
                "sprintSpecPath": "docs/SOP/SPRINT_TEST_V1.md",
                "selectionRecord": "docs/SOP/POST_TEST_V1_SELECTION.md",
                "slices": [
                    {
                        "sliceId": slice_id,
                        "declaredPlane": "PRODUCT-PLANE",
                        "layerPreset": "PPE_UI",
                        "buildBranch": f"build/auto/{slice_id}",
                        "touchSet": ["src/viz/app.py"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (sop / "SPRINT_TEST_V1.md").write_text("# sprint\n", encoding="utf-8")
    (sop / "POST_TEST_V1_SELECTION.md").write_text("# sel\n", encoding="utf-8")
    presets_src = Path(__file__).resolve().parents[1] / "docs" / "SOP" / "REPO_LAYER_PATH_PREFIXES.json"
    if presets_src.is_file():
        (sop / "REPO_LAYER_PATH_PREFIXES.json").write_text(
            presets_src.read_text(encoding="utf-8"),
            encoding="utf-8",
        )


class TestStarterDocResolveFreshness(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.plan_rel = "docs/SOP/PHASE_PLANS/test_chapter_v1_relay.json"
        self.slice_id = "Ch-Product-Slice002"
        _write_min_plan(self.repo, plan_rel=self.plan_rel, slice_id=self.slice_id)
        (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
            json.dumps({"items": [{"planPath": self.plan_rel, "status": "READY"}]}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_starter_embeds_resolve_fingerprint(self) -> None:
        md = build_starter_md(self.repo, slice_id=self.slice_id, phase_plan=self.plan_rel)
        fp = parse_starter_resolve_fingerprint(md)
        self.assertIsNotNone(fp)
        self.assertEqual(fp, doc_resolve_fingerprint(self.repo, self.plan_rel))

    def test_stale_when_fingerprint_mismatch(self) -> None:
        md = build_starter_md(self.repo, slice_id=self.slice_id, phase_plan=self.plan_rel)
        stale_fp = format_resolve_fingerprint_line("deadbeef0000")
        tampered = md.replace(
            format_resolve_fingerprint_line(parse_starter_resolve_fingerprint(md) or ""),
            stale_fp,
        )
        stale, reason = starter_doc_resolve_stale(
            self.repo,
            slice_id=self.slice_id,
            phase_plan=self.plan_rel,
            starter_text=tampered,
        )
        self.assertTrue(stale)
        self.assertIn("fingerprint", reason)

    def test_plan_regen_includes_stale_ready_starter(self) -> None:
        write_starter(self.repo, slice_id=self.slice_id, phase_plan=self.plan_rel)
        path = self.repo / "artifacts" / "orchestrator" / f"IDE_BUILD_STARTER_{self.slice_id}.md"
        text = path.read_text(encoding="utf-8")
        old_fp = parse_starter_resolve_fingerprint(text)
        self.assertIsNotNone(old_fp)
        path.write_text(text.replace(old_fp or "", "deadbeef0000"), encoding="utf-8")
        plan = plan_regen_ready_starters(self.repo)
        self.assertGreaterEqual(plan["stale_count"], 1)
        self.assertEqual(plan["pending_count"], plan["missing_count"] + plan["stale_count"])

    def test_regenerate_refreshes_stale_starter(self) -> None:
        write_starter(self.repo, slice_id=self.slice_id, phase_plan=self.plan_rel)
        path = self.repo / "artifacts" / "orchestrator" / f"IDE_BUILD_STARTER_{self.slice_id}.md"
        text = path.read_text(encoding="utf-8")
        old_fp = parse_starter_resolve_fingerprint(text)
        self.assertIsNotNone(old_fp)
        path.write_text(text.replace(old_fp or "", "deadbeef0000"), encoding="utf-8")
        out = regenerate_starters_for_ready_queue(self.repo)
        self.assertIn(self.plan_rel, out)
        new_fp = parse_starter_resolve_fingerprint(path.read_text(encoding="utf-8"))
        self.assertEqual(new_fp, doc_resolve_fingerprint(self.repo, self.plan_rel))


if __name__ == "__main__":
    unittest.main()
