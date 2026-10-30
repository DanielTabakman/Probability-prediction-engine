"""Tests for deterministic ChatGPT/GitHub/Codex context accounting."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ppe_context_surface_audit import build_context_surface_audit


PROJECT_TEXT = "Project instructions stay compact."
ROLE_TEXT = {
    "Founder setup and collaboration": "Founder setup contract.",
    "Charter or product topic": "Charter contract.",
    "Codex implementation": "Codex contract.",
    "Review and reconciliation": "Review contract.",
}


class TestPpeContextSurfaceAudit(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "CHATGPT_PROJECT_STARTER.md").write_text(
            f"# Starter\n\n```text\n{PROJECT_TEXT}\n```\n",
            encoding="utf-8",
        )
        control_lines = ["# Control plane", ""]
        for index, (heading, text) in enumerate(ROLE_TEXT.items(), start=1):
            control_lines.extend(
                [
                    f"### {index}. {heading}",
                    "",
                    "```text",
                    text,
                    "```",
                    "",
                ]
            )
        (sop / "CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md").write_text(
            "\n".join(control_lines),
            encoding="utf-8",
        )
        for name in (
            "AGENT_ROUTING_V1.md",
            "CHAPTER_DOC_INDEX.json",
            "PHASE_CHAPTER_BACKLOG.json",
            "ACTIVE_PRODUCT_DIRECTION.json",
        ):
            (sop / name).write_text("{}\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_measures_project_roles_and_fixed_bundles(self) -> None:
        head = "b" * 40
        (self.repo / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md").write_text(
            "# Brief\n\n"
            f"**HEAD:** `{'a' * 40}`\n\n"
            "**Active relay:** ``\n"
            "- **Sprint:** [``]()\n"
            "- **Plan:** [``]()\n"
            "- path: `C:/Users/example/run`\n",
            encoding="utf-8",
        )

        report = build_context_surface_audit(self.repo, head=head)

        self.assertEqual(report["project_instructions"]["chars"], len(PROJECT_TEXT))
        self.assertEqual(
            report["startup_bundles"]["founder_setup"]["chars"],
            len(PROJECT_TEXT) + 1 + len(ROLE_TEXT["Founder setup and collaboration"]),
        )
        self.assertEqual(report["continuity"]["freshness"], "stale")
        self.assertFalse(report["continuity"]["complete"])
        self.assertFalse(report["continuity"]["safe_to_load_first"])
        self.assertEqual(report["verdict"], "WATCH")

    def test_fresh_complete_portable_continuity_is_safe(self) -> None:
        head = "c" * 40
        (self.repo / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md").write_text(
            "# Brief\n\n"
            f"**HEAD:** `{head}`\n\n"
            "**Active relay:** `slice-1`\n"
            "- **Sprint:** [`SPRINT.md`](SPRINT.md)\n"
            "- **Plan:** [`PLAN.json`](PLAN.json)\n",
            encoding="utf-8",
        )

        report = build_context_surface_audit(self.repo, head=head)

        self.assertEqual(report["continuity"]["freshness"], "fresh")
        self.assertTrue(report["continuity"]["complete"])
        self.assertTrue(report["continuity"]["safe_to_load_first"])
        self.assertEqual(report["verdict"], "OK")


if __name__ == "__main__":
    unittest.main()
