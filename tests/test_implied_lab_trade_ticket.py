"""FS-007: trade ticket code text (pure, no Streamlit)."""

from __future__ import annotations

import unittest

from src.viz.app import _implied_lab_trade_ticket_code_text


class TestImpliedLabTradeTicketCodeText(unittest.TestCase):
    def test_ticket_includes_expiry_debit_and_legs(self) -> None:
        strat = {
            "long_k1": False,
            "long_k2": True,
            "long_k3": True,
            "long_k4": False,
            "k1": 40_000,
            "k2": 45_000,
            "k3": 50_000,
            "k4": 55_000,
        }
        put_by_k = {40_000: 0.01, 45_000: 0.02}
        call_by_k = {50_000: 0.03, 55_000: 0.04}
        summary = {
            "cost_usd": 100.0,
            "max_gain": 500.0,
            "max_loss": 200.0,
            "breakevens": [44_000.0, 56_000.0],
        }
        text, prems, sides = _implied_lab_trade_ticket_code_text(
            selected_expiry_str="2026-06-26",
            qty=2,
            forward=50_000.0,
            selected_strategy=strat,
            put_by_k=put_by_k,
            call_by_k=call_by_k,
            summary=summary,
        )
        self.assertIn("Expiry: 2026-06-26", text)
        self.assertIn("Size: 2x", text)
        self.assertIn("debit", text)
        self.assertIn("Max gain (approx): 500", text)
        self.assertIn("Breakevens:", text)
        self.assertEqual(len(prems), 4)
        self.assertEqual(sides, ("Short", "Long", "Long", "Short"))
        low = text.lower()
        for tok in ("best ", "optimal", "recommended", "you should"):
            self.assertNotIn(tok, low)


if __name__ == "__main__":
    unittest.main()
