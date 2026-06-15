"""Tests for operator instance resolution."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_operator_instance import (
    list_enabled_instances,
    load_instances_config,
    loop_lock_path,
    resolve_instance_for_repo,
)


class TestPpeOperatorInstance(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PPE_OPERATOR_INSTANCES.local.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "instances": [
                        {
                            "id": "msos",
                            "label": "MSOS",
                            "repoRoot": (self.repo / "clones" / "msos").as_posix(),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.repo / "clones" / "msos").mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_resolve_default_primary(self) -> None:
        inst = resolve_instance_for_repo(self.repo)
        self.assertEqual(inst["id"], "default")
        self.assertIn("repoRoot", inst)

    def test_resolve_configured_clone(self) -> None:
        clone = self.repo / "clones" / "msos"
        import os

        os.environ["PPE_COORDINATOR_REPO"] = str(self.repo)
        os.environ["PPE_OPERATOR_INSTANCE"] = "msos"
        try:
            inst = resolve_instance_for_repo(clone)
            self.assertEqual(inst["id"], "msos")
            self.assertEqual(inst["label"], "MSOS")
        finally:
            os.environ.pop("PPE_COORDINATOR_REPO", None)
            os.environ.pop("PPE_OPERATOR_INSTANCE", None)

    def test_list_enabled_includes_coordinator(self) -> None:
        rows = list_enabled_instances(self.repo)
        ids = {r["id"] for r in rows}
        self.assertIn("msos", ids)
        self.assertIn("default", ids)

    def test_loop_lock_path_per_instance(self) -> None:
        clone = self.repo / "clones" / "msos"
        import os

        os.environ["PPE_COORDINATOR_REPO"] = str(self.repo)
        try:
            path = loop_lock_path(clone)
            self.assertIn("LOOP_SINGLETON_msos", path.name)
        finally:
            os.environ.pop("PPE_COORDINATOR_REPO", None)

    def test_load_instances_config(self) -> None:
        cfg = load_instances_config(self.repo)
        self.assertEqual(len(cfg.get("instances") or []), 1)


if __name__ == "__main__":
    unittest.main()
