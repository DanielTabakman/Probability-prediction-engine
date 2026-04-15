"""Feature slice 010: market-data degraded / partial state copy (provenance-aligned)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.decision_ready_review import assert_no_advisory_language
from src.viz.implied_lab_provenance import (
    build_market_data_legibility_payload,
    build_trust_strip_lines,
)


class TestMarketDataLegibilityPayload(unittest.TestCase):
    def test_no_provenance_neutral(self) -> None:
        leg = build_market_data_legibility_payload({}, call_n=0, put_n=0)
        self.assertIn("Trust / provenance", leg["summary_line"])
        self.assertFalse(leg["expander_expanded"])
        self.assertFalse((leg.get("detail_markdown") or "").strip())
        self.assertIsNone(leg.get("trust_strip_suffix"))

    def test_nominal_path_collapsed_expander(self) -> None:
        md = {
            "quote_cache_ttl_s": 120,
            "live_data_provenance": {
                "spot_reference": "deribit_btc_index",
                "deribit_atm_ticker_ok": True,
                "atm_iv_from_deribit": True,
            },
        }
        leg = build_market_data_legibility_payload(md, call_n=5, put_n=4)
        self.assertIn("nominal path", leg["summary_line"].lower())
        self.assertFalse(leg["expander_expanded"])
        self.assertIn("5** calls", leg["detail_markdown"])
        self.assertIsNone(leg.get("trust_strip_suffix"))
        assert_no_advisory_language(leg["summary_line"] + leg["detail_markdown"])

    def test_yahoo_spot_degraded(self) -> None:
        md = {
            "quote_cache_ttl_s": 120,
            "live_data_provenance": {
                "spot_reference": "yahoo_btc_usd_last_close",
                "deribit_atm_ticker_ok": True,
                "atm_iv_from_deribit": True,
            },
        }
        leg = build_market_data_legibility_payload(md, call_n=5, put_n=4)
        self.assertTrue(leg["expander_expanded"])
        self.assertIn("Yahoo", leg["detail_markdown"])
        self.assertIn("degraded", leg["summary_line"].lower())
        suf = leg.get("trust_strip_suffix")
        self.assertIsInstance(suf, str)
        assert suf is not None
        self.assertIn("degraded", suf.lower())

    def test_partial_orange_suffix(self) -> None:
        md = {
            "live_data_provenance": {
                "spot_reference": "deribit_btc_index",
                "deribit_atm_ticker_ok": True,
                "atm_iv_from_deribit": True,
            },
        }
        leg = build_market_data_legibility_payload(md, call_n=2, put_n=1)
        self.assertTrue(leg["expander_expanded"])
        self.assertIn("Not computed", leg["detail_markdown"])
        suf = leg.get("trust_strip_suffix")
        self.assertIsInstance(suf, str)
        assert suf is not None
        self.assertIn("partial", suf.lower())

    def test_trust_strip_appends_suffix_before_pointer(self) -> None:
        vs = {
            "as_of_utc": "2026-04-11T12:00:00+00:00",
            "data_sources": ["Deribit"],
            "overlay_basis": "Green overlay: test.",
            "strategy_families_scope": "Scope line.",
        }
        verification = {
            "verification_summary": vs,
            "market_data_legibility": {
                "summary_line": "x",
                "trust_strip_suffix": "**Market inputs:** test degraded suffix.",
            },
        }
        lines = build_trust_strip_lines(verification)
        self.assertEqual(lines[-1], "Full traces and numeric inputs: expand **Verification** below.")
        self.assertEqual(lines[-2], "**Market inputs:** test degraded suffix.")


if __name__ == "__main__":
    unittest.main()
