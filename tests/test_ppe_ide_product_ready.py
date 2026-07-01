"""Tests for IDE product-ready marker."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_ide_product_ready import (
    MARKER_REL,
    check_marker,
    clear_marker,
    load_marker,
    mark_product_ready,
    marker_covers_product_slices,
)


class TestPpeIdeProductReady(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop.mkdir(parents=True)
        self.plan_rel = "docs/SOP/PHASE_PLANS/phase.json"
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "phase.json").write_text(
            json.dumps(
                {
                    "sprintSpecPath": "docs/SOP/SPRINT_X.md",
                    "slices": [
                        {
                            "sliceId": "Ch-Product-Slice002",
                            "buildBranch": "build/auto/Ch-Product-Slice002-local",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @patch("scripts.ppe_ide_product_ready._branch_has_commits", return_value=False)
    def test_mark_fails_without_commits(self, *_m: object) -> None:
        rc, msg = mark_product_ready(
            self.repo,
            slice_id="Ch-Product-Slice002",
            plan_path=self.plan_rel,
        )
        self.assertEqual(rc, 2)
        self.assertIn("no commits", msg)

    @patch("scripts.ppe_ide_product_ready._branch_has_commits", return_value=True)
    @patch("scripts.ppe_ide_product_ready._git")
    def test_mark_and_clear(self, mock_git: object, *_m: object) -> None:
        mock_git.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="abc123\n", stderr=""
        )
        rc, path = mark_product_ready(
            self.repo,
            slice_id="Ch-Product-Slice002",
            plan_path=self.plan_rel,
        )
        self.assertEqual(rc, 0)
        self.assertTrue(Path(path).is_file())
        data = load_marker(self.repo)
        self.assertIsNotNone(data)
        assert data is not None
        self.assertEqual(data["sliceId"], "Ch-Product-Slice002")
        self.assertTrue(
            marker_covers_product_slices(
                self.repo,
                plan_path=self.plan_rel,
                product_slice_ids=["Ch-Product-Slice002"],
            )
        )
        self.assertTrue(clear_marker(self.repo))
        self.assertIsNone(load_marker(self.repo))

    @patch("scripts.ppe_ide_product_ready._branch_has_commits", return_value=True)
    @patch("scripts.ppe_ide_product_ready._git")
    def test_multi_plan_markers_preserved(self, mock_git: object, *_m: object) -> None:
        mock_git.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="abc123\n", stderr=""
        )
        plan_a = "docs/SOP/PHASE_PLANS/plan_a_relay.json"
        plan_b = "docs/SOP/PHASE_PLANS/plan_b_relay.json"
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "plan_a_relay.json").write_text(
            json.dumps(
                {
                    "slices": [
                        {"sliceId": "A-Product-Slice001", "buildBranch": "main"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "plan_b_relay.json").write_text(
            json.dumps(
                {
                    "slices": [
                        {"sliceId": "B-Product-Slice001", "buildBranch": "main"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        mark_product_ready(self.repo, slice_id="A-Product-Slice001", plan_path=plan_a)
        mark_product_ready(self.repo, slice_id="B-Product-Slice001", plan_path=plan_b)
        from scripts.ppe_ide_product_ready import completed_product_slice_ids

        self.assertIn("A-Product-Slice001", completed_product_slice_ids(self.repo, plan_path=plan_a))
        self.assertIn("B-Product-Slice001", completed_product_slice_ids(self.repo, plan_path=plan_b))

    @patch("scripts.ppe_ide_product_ready._branch_has_commits", return_value=True)
    @patch("scripts.ppe_ide_product_ready._git")
    def test_mark_releases_matching_worker_lease(self, mock_git: object, *_m: object) -> None:
        from scripts.ppe_worker_lease import acquire_lease, load_lease

        mock_git.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="abc123\n", stderr=""
        )
        acquire_lease(
            self.repo,
            worker_id="codex-app",
            branch="build/auto/Ch-Product-Slice002-local",
            path_globs=["src/**"],
            work_item={"slice_id": "Ch-Product-Slice002"},
        )
        rc, _path = mark_product_ready(
            self.repo,
            slice_id="Ch-Product-Slice002",
            plan_path=self.plan_rel,
        )
        self.assertEqual(rc, 0)
        self.assertIsNone(load_lease(self.repo))

    @patch("scripts.ppe_ide_product_ready._branch_has_commits", return_value=True)
    @patch("scripts.ppe_ide_product_ready._git")
    def test_check_ok(self, mock_git: object, *_m: object) -> None:
        mock_git.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="deadbeef\n", stderr=""
        )
        mark_product_ready(self.repo, slice_id="Ch-Product-Slice002", plan_path=self.plan_rel)
        manifest_dir = self.repo / "docs" / "SOP"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        (manifest_dir / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps({"phasePlanPath": self.plan_rel, "status": "READY"}),
            encoding="utf-8",
        )
        self.assertEqual(check_marker(self.repo), 0)


if __name__ == "__main__":
    unittest.main()
