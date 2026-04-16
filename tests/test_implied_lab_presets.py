from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.implied_lab_presets import PRESETS, compute_preset_shape, preset_what_changed


class TestImpliedLabPresets(unittest.TestCase):
    def test_preset_shapes_have_ordered_strikes_and_flags(self) -> None:
        avail = [30_000.0, 35_000.0, 40_000.0, 45_000.0, 50_000.0, 55_000.0, 60_000.0]
        forward = 50_000.0

        for preset_id in PRESETS.keys():
            shape = compute_preset_shape(preset_id=preset_id, forward=forward, avail_strikes=avail)
            for k in ("k1", "k2", "k3", "k4"):
                self.assertIn(k, shape)
            self.assertLessEqual(shape["k1"], shape["k2"])
            self.assertLessEqual(shape["k2"], shape["k3"])
            self.assertLessEqual(shape["k3"], shape["k4"])
            for flag in ("use_k1", "use_k2", "use_k3", "use_k4", "reverse"):
                self.assertIn(flag, shape)
                self.assertIsInstance(shape[flag], bool)

    def test_call_spread_disables_puts(self) -> None:
        shape = compute_preset_shape(
            preset_id="bull_call_spread",
            forward=50_000.0,
            avail_strikes=[40_000.0, 45_000.0, 50_000.0, 55_000.0, 60_000.0],
        )
        self.assertFalse(shape["use_k1"])
        self.assertFalse(shape["use_k2"])
        self.assertTrue(shape["use_k3"])
        self.assertTrue(shape["use_k4"])
        self.assertFalse(shape["reverse"])

    def test_put_spread_disables_calls(self) -> None:
        shape = compute_preset_shape(
            preset_id="bear_put_spread",
            forward=50_000.0,
            avail_strikes=[40_000.0, 45_000.0, 50_000.0, 55_000.0, 60_000.0],
        )
        self.assertTrue(shape["use_k1"])
        self.assertTrue(shape["use_k2"])
        self.assertFalse(shape["use_k3"])
        self.assertFalse(shape["use_k4"])
        self.assertFalse(shape["reverse"])

    def test_short_iron_fly_flips_polarity_and_uses_all_legs(self) -> None:
        shape = compute_preset_shape(
            preset_id="short_iron_fly",
            forward=50_000.0,
            avail_strikes=[40_000.0, 45_000.0, 50_000.0, 55_000.0, 60_000.0],
        )
        self.assertTrue(shape["use_k1"])
        self.assertTrue(shape["use_k2"])
        self.assertTrue(shape["use_k3"])
        self.assertTrue(shape["use_k4"])
        self.assertTrue(shape["reverse"])

    def test_preset_what_changed_mentions_enabled_disabled_and_strikes__sprint_001_slice_006_phase_2(self) -> None:
        shape = compute_preset_shape(
            preset_id="bull_call_spread",
            forward=50_000.0,
            avail_strikes=[40_000.0, 45_000.0, 50_000.0, 55_000.0, 60_000.0],
        )
        msg = preset_what_changed(preset_id="bull_call_spread", shape=shape)
        self.assertIn("Applied preset", msg)
        self.assertIn("Enabled legs", msg)
        self.assertIn("Disabled legs", msg)
        self.assertIn("Strikes set to", msg)
        self.assertIn("Bull call spread", msg)
        self.assertIn("K1", msg)
        self.assertIn("K4", msg)


if __name__ == "__main__":
    unittest.main()

