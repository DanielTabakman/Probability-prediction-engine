"""Tests for ACTIVE_IDE_SLICE checkout lock."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.ppe_active_ide_slice import (
    ACTIVE_SLICE_REL,
    clear_active_slice,
    load_active_slice,
    write_active_slice,
)


class TestPpeActiveIdeSlice(unittest.TestCase):
    def test_write_load_clear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            out = write_active_slice(
                repo,
                slice_id="Ch-Product-Slice001",
                phase_plan_path="docs/SOP/PHASE_PLANS/plan.json",
                starter_path="artifacts/orchestrator/IDE_BUILD_STARTER_Ch-Product-Slice001.md",
            )
            self.assertTrue(out.is_file())
            data = load_active_slice(repo)
            assert data is not None
            self.assertEqual(data["sliceId"], "Ch-Product-Slice001")
            self.assertEqual(data["owner"], "IDE")
            self.assertIn("checkedOutAt", data)
            self.assertTrue(clear_active_slice(repo))
            self.assertFalse((repo / ACTIVE_SLICE_REL).is_file())

    def test_is_active_slice_stale(self) -> None:
        from datetime import datetime, timedelta, timezone

        from scripts.ppe_active_ide_slice import is_active_slice_stale

        old = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat().replace("+00:00", "Z")
        self.assertTrue(is_active_slice_stale({"checkedOutAt": old}))
        fresh = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.assertFalse(is_active_slice_stale({"checkedOutAt": fresh}))

    def test_write_starter_invokes_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with mock.patch(
                "scripts.ppe_ide_build_starter.build_starter_md", return_value="# starter\n"
            ):
                with mock.patch(
                    "scripts.ppe_active_ide_slice.write_active_slice"
                ) as mock_write:
                    from scripts.ppe_ide_build_starter import write_starter

                    write_starter(
                        repo,
                        slice_id="Ch-Product-Slice002",
                        phase_plan="docs/SOP/PHASE_PLANS/plan.json",
                    )
                    mock_write.assert_called_once()
                    kwargs = mock_write.call_args.kwargs
                    self.assertEqual(kwargs["slice_id"], "Ch-Product-Slice002")


if __name__ == "__main__":
    unittest.main()
