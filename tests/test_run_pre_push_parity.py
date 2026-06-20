"""Tests for scripts/run_pre_push_parity.py."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_pre_push_parity import main, run_docker_entrypoint_smoke

REPO = Path(__file__).resolve().parents[1]


class TestRunPrePushParity(unittest.TestCase):
    def test_main_runs_gate_by_default(self) -> None:
        with patch("scripts.run_pre_push_parity.run_pushable_gate", return_value=0) as gate:
            rc = main([])
        self.assertEqual(rc, 0)
        gate.assert_called_once()

    def test_main_skips_gate_with_skip_gate_flag(self) -> None:
        with patch("scripts.run_pre_push_parity.run_pushable_gate") as gate:
            with patch("scripts.run_pre_push_parity.run_docker_entrypoint_smoke", return_value=0) as docker:
                rc = main(["--skip-gate", "--docker"])
        self.assertEqual(rc, 0)
        gate.assert_not_called()
        docker.assert_called_once()

    def test_docker_smoke_fails_when_docker_missing(self) -> None:
        with patch("scripts.run_pre_push_parity._docker_available", return_value=False):
            rc = run_docker_entrypoint_smoke(REPO)
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
