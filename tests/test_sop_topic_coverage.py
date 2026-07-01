"""Charter / thread-role phrases should resolve via TOPIC_ROUTES."""

from __future__ import annotations

import unittest

from scripts.sop_discovery_core import resolve_by_topic

# Phrases from ppe-thread-roles.mdc and asset-auto-discovery → expected route id
CHARTER_PHRASE_COVERAGE: list[tuple[str, str]] = [
    ("what's next", "operator_relay"),
    ("operator thread", "operator_relay"),
    ("charter thread", "steward_selection"),
    ("ux backlog", "ux_execution"),
    ("add asset", "asset_enable"),
    ("asset batch wave 1", "asset_batch"),
    ("sop discovery", "sop_discovery"),
    ("token economy", "token_burst"),
    ("msos web feedback", "msos_web"),
    ("resolve_sop", "sop_discovery"),
]


class TestSopTopicCoverage(unittest.TestCase):
    def test_charter_phrases_map_to_topic_routes(self) -> None:
        missing: list[str] = []
        for phrase, expected_id in CHARTER_PHRASE_COVERAGE:
            report = resolve_by_topic(phrase)
            route_id = report.get("topic_route_id")
            if not report.get("ok") or route_id != expected_id:
                missing.append(f"{phrase!r} -> {route_id!r} (expected {expected_id!r})")
        self.assertFalse(missing, "topic coverage gaps:\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
