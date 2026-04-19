from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.implied_lab_last_action import last_action_meaning, shape_window_local_region_story


class TestImpliedLabLastAction(unittest.TestCase):
    def test_mode_switch_message(self) -> None:
        msg = last_action_meaning(action_id="mode_switch", mode_label="Exact strikes")
        self.assertIn("Mode changed", msg)
        self.assertIn("Exact strikes", msg)

    def test_quantity_message(self) -> None:
        msg = last_action_meaning(action_id="quantity", qty=3)
        self.assertIn("Quantity set", msg)
        self.assertIn("3", msg)

    def test_polarity_reverse_messages(self) -> None:
        msg_on = last_action_meaning(action_id="polarity_reverse", reverse=True)
        msg_off = last_action_meaning(action_id="polarity_reverse", reverse=False)
        self.assertIn("Polarity", msg_on)
        self.assertIn("reversed", msg_on.lower())
        self.assertIn("normal", msg_off.lower())

    def test_leg_toggle_message(self) -> None:
        msg = last_action_meaning(action_id="leg_toggle", leg="K2", leg_enabled=False)
        self.assertIn("Leg K2", msg)
        self.assertIn("disabled", msg.lower())

    def test_strike_edit_message(self) -> None:
        msg = last_action_meaning(
            action_id="strike_edit",
            strikes={"k1": 40_000.0, "k2": 45_000.0, "k3": 50_000.0, "k4": 55_000.0},
        )
        self.assertIn("Strikes updated", msg)
        self.assertIn("K1", msg)
        self.assertIn("K4", msg)

    def test_belief_toggle_messages(self) -> None:
        self.assertIn("shown", last_action_meaning(action_id="belief_toggle", belief_enabled=True))
        self.assertIn("hidden", last_action_meaning(action_id="belief_toggle", belief_enabled=False))

    def test_belief_center_message_mentions_peak(self) -> None:
        msg = last_action_meaning(action_id="belief_center", belief_center_usd=123_456.0)
        self.assertIn("Belief peak", msg)
        self.assertIn("$123,456", msg)

    def test_belief_width_message_mentions_sigma(self) -> None:
        msg = last_action_meaning(action_id="belief_width", belief_width_sigma_ln=0.23456)
        self.assertIn("σ_ln", msg)
        self.assertIn("0.2346", msg)  # rounded to 4dp

    def test_target_payoff_edit_message_is_descriptive(self) -> None:
        msg = last_action_meaning(action_id="target_payoff_edit", target_id="Body left", target_value=50_000.0)
        self.assertIn("Target-payoff input updated", msg)
        self.assertIn("Body left", msg)
        self.assertIn("$50,000", msg)

    def test_net_pnl_mode_toggle_messages(self) -> None:
        self.assertIn("enabled", last_action_meaning(action_id="net_pnl_mode_toggle", net_pnl_mode=True))
        self.assertIn("disabled", last_action_meaning(action_id="net_pnl_mode_toggle", net_pnl_mode=False))

    def test_shape_window(self) -> None:
        msg = last_action_meaning(action_id="shape_window", shape_window_label="Near forward")
        self.assertIn("shape window", msg.lower())
        self.assertIn("Near forward", msg)
        self.assertIn("underlying price", msg.lower())

    def test_local_region_story_full_range_no_strip(self) -> None:
        md, strip = shape_window_local_region_story(
            zoom_choice="Full range",
            xr0=40_000.0,
            xr1=120_000.0,
            forward=95_000.0,
            belief_overlay_enabled=False,
            verification=None,
        )
        self.assertIn("no narrowed band", md.lower())
        self.assertIn("full", md.lower())
        self.assertEqual(strip, "")

    def test_local_region_story_near_forward_mentions_band(self) -> None:
        md, strip = shape_window_local_region_story(
            zoom_choice="Near forward",
            xr0=80_000.0,
            xr1=110_000.0,
            forward=95_000.0,
            belief_overlay_enabled=False,
            verification=None,
        )
        self.assertIn("Near forward", md)
        self.assertIn("80", md.replace(",", ""))
        self.assertIn("same priced inputs", md.lower())
        self.assertTrue(len(strip) > 10)

    def test_local_region_story_gap_inside_window(self) -> None:
        ver = {
            "belief_vs_market_glance": {
                "largest_gap_price_usd": 90_000.0,
                "largest_gap_display": "$90,000",
            }
        }
        md, _ = shape_window_local_region_story(
            zoom_choice="Near forward",
            xr0=80_000.0,
            xr1=110_000.0,
            forward=95_000.0,
            belief_overlay_enabled=True,
            verification=ver,
        )
        self.assertIn("inside this shape window", md.lower())
        self.assertIn("ΔPDF", md)


if __name__ == "__main__":
    unittest.main()

