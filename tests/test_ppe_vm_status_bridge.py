"""Tests for VM status bridge (desktop stale → VM authoritative)."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.ppe_vm_status_bridge import (
    apply_vm_authoritative,
    parse_status_brief,
    should_trust_vm_over_local,
)


class TestVmStatusBridge(unittest.TestCase):
    def test_parse_status_brief(self) -> None:
        line = (
            "PHASE=AWAITING_BUILD VERDICT=IDE_BUILD slice=MSOS-FCR-Product-Slice002 "
            "stack_loop=True stack_watch=True next=handoff"
        )
        parsed = parse_status_brief(line)
        self.assertEqual(parsed["phase"], "AWAITING_BUILD")
        self.assertEqual(parsed["verdict"], "IDE_BUILD")
        self.assertEqual(parsed["slice_id"], "MSOS-FCR-Product-Slice002")

    def test_should_trust_vm_ide_build_over_run_local(self) -> None:
        self.assertTrue(
            should_trust_vm_over_local(
                local_verdict="RUN_LOCAL",
                vm_verdict="IDE_BUILD",
                preflight_warnings=["checkout is 'fix/foo', not main"],
            )
        )

    def test_should_not_trust_when_same_verdict(self) -> None:
        self.assertFalse(
            should_trust_vm_over_local(
                local_verdict="IDE_BUILD",
                vm_verdict="IDE_BUILD",
            )
        )

    @patch("scripts.ppe_vm_status_bridge.fetch_vm_autobuilder_status")
    @patch("scripts.ppe_vm_status_bridge.vm_bridge_enabled", return_value=True)
    def test_apply_vm_authoritative_overlays_verdict(
        self,
        _enabled: object,
        fetch: object,
    ) -> None:
        fetch.return_value = {
            "ok": True,
            "source": "json",
            "status": {
                "verdict": "IDE_BUILD",
                "phase": "AWAITING_BUILD",
                "blocker": "product slice pending",
                "build": {
                    "slice_id": "MSOS-FCR-Product-Slice002",
                    "plan_path": "docs/SOP/PHASE_PLANS/msos_forward_consistency_radar_v1_relay.json",
                },
                "operator": {"chapter_name": "Forward Consistency Radar"},
            },
        }
        local = {
            "verdict": "RUN_LOCAL",
            "preflight_warnings": ["checkout is 'fix/foo', not main"],
            "commands": ["DESKTOP_CONTINUE.cmd --no-pause"],
            "guard": {"reason": "IDE_MARKER_OK"},
        }
        merged = apply_vm_authoritative(local, loop_host_allowed=False)
        self.assertTrue(merged.get("vm_authoritative"))
        self.assertEqual(merged.get("verdict"), "IDE_BUILD")
        self.assertEqual(merged.get("local_verdict"), "RUN_LOCAL")


if __name__ == "__main__":
    unittest.main()
