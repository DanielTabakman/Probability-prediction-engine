"""Sprint 005: decision-ready review display payload (display-only, no Streamlit)."""

from __future__ import annotations

import unittest

from src.viz.decision_ready_review import (
    FORBIDDEN_ADVISORY_TOKENS,
    assert_no_advisory_language,
    build_decision_ready_review_payload,
)


def _join_payload_text(p: dict) -> str:
    parts = [
        p["structure_line"],
        p["payoff_line"],
        p["linkage_line"],
        p.get("fit_caption") or "",
    ]
    parts.extend(p.get("bullets") or [])
    return "\n".join(parts)


class TestDecisionReadyReviewPayload(unittest.TestCase):
    def _minimal_applicable_verification(
        self,
        *,
        name: str = "Iron condor",
        debit_credit: str = "credit",
        glance: dict | None = None,
    ) -> dict:
        v: dict = {
            "strategy_summary": {
                "applicable": True,
                "values": {
                    "name": name,
                    "debit_credit": debit_credit,
                },
            },
            "verification_summary": {
                "overlay_basis": "Green overlay: strikes from exact K1–K4 using listed option marks.",
            },
        }
        if glance is not None:
            v["belief_vs_market_glance"] = glance
        return v

    def test_none_when_not_applicable(self) -> None:
        self.assertIsNone(build_decision_ready_review_payload(None))
        self.assertIsNone(build_decision_ready_review_payload({}))
        self.assertIsNone(
            build_decision_ready_review_payload(
                {"strategy_summary": {"applicable": False, "values": {}}}
            )
        )

    def test_normal_active_strategy_with_glance(self) -> None:
        glance = {"fit_note": "Fit is not recommendation."}
        p = build_decision_ready_review_payload(
            self._minimal_applicable_verification(glance=glance)
        )
        assert p is not None
        self.assertIn("Iron condor", p["structure_line"])
        self.assertIn("Range-bound", p["payoff_line"])
        self.assertIn("Belief vs market", p["linkage_line"])
        self.assertIn("Trade ticket (copy/paste)", p["linkage_line"])
        self.assertIn("directly under this block", p["linkage_line"])
        self.assertEqual(len(p["bullets"]), 2)
        self.assertIn("Strike construction", p["bullets"][0])
        self.assertIn("Fit is not recommendation", p["fit_caption"])
        assert_no_advisory_language(_join_payload_text(p))

    def test_missing_belief_context_branch(self) -> None:
        p = build_decision_ready_review_payload(self._minimal_applicable_verification())
        assert p is not None
        self.assertIn("Belief overlay off", p["linkage_line"])
        self.assertIn("Trade ticket (copy/paste)", p["linkage_line"])
        assert_no_advisory_language(_join_payload_text(p))

    def test_payoff_debit_credit_clauses(self) -> None:
        v = self._minimal_applicable_verification(name="Strangle", debit_credit="debit")
        p = build_decision_ready_review_payload(v)
        assert p is not None
        self.assertIn("net debit", p["payoff_line"])

    def test_custom_name_fallback_payoff(self) -> None:
        v = self._minimal_applicable_verification(name="Custom 4-leg", debit_credit="debit")
        p = build_decision_ready_review_payload(v)
        assert p is not None
        self.assertIn("Custom four-leg", p["payoff_line"])

    def test_default_name_when_empty(self) -> None:
        v = self._minimal_applicable_verification(name="")
        v["strategy_summary"]["values"]["name"] = ""
        p = build_decision_ready_review_payload(v)
        assert p is not None
        self.assertIn("Active structure", p["structure_line"])

    def test_forbidden_token_list_is_reasonable(self) -> None:
        for tok in FORBIDDEN_ADVISORY_TOKENS:
            self.assertGreater(len(tok), 2)


if __name__ == "__main__":
    unittest.main()
