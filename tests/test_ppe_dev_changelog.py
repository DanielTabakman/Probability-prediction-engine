"""Tests for ppe_dev_changelog."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppe_dev_changelog import (
    QUIET_STUB,
    append_chapter_closed_event,
    cmd_backfill,
    cmd_refresh,
    load_changelog,
    load_state,
    save_state,
    state_path,
)


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> None:
    merged = os.environ.copy()
    merged.setdefault("GIT_AUTHOR_NAME", "test")
    merged.setdefault("GIT_AUTHOR_EMAIL", "test@example.com")
    merged.setdefault("GIT_COMMITTER_NAME", "test")
    merged.setdefault("GIT_COMMITTER_EMAIL", "test@example.com")
    if env:
        merged.update(env)
    subprocess.run(["git", *args], cwd=repo, check=True, env=merged)


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "test")


def _commit(repo: Path, message: str, *, date: str = "2026-06-01T12:00:00+00:00") -> str:
    env = {
        "GIT_AUTHOR_DATE": date,
        "GIT_COMMITTER_DATE": date,
    }
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message, env=env)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


class TestPpeDevChangelog(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _init_repo(self.repo)
        (self.repo / "README.md").write_text("seed\n", encoding="utf-8")
        _commit(self.repo, "seed commit")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_refresh_appends_commit_under_utc_date(self) -> None:
        (self.repo / "apps" / "msos-web" / "page.tsx").parent.mkdir(parents=True)
        (self.repo / "apps" / "msos-web" / "page.tsx").write_text("export {}\n", encoding="utf-8")
        _commit(
            self.repo,
            "MSOS-P2-Product-Slice002: homepage (product-plane)",
            date="2026-06-03T10:00:00+00:00",
        )

        self.assertEqual(cmd_refresh(self.repo), 0)
        parsed = load_changelog(self.repo)
        self.assertIn("2026-06-03", parsed.sections)
        bullets = "\n".join(parsed.sections["2026-06-03"])
        self.assertIn("MSOS-P2-Product-Slice002", bullets)
        self.assertIn("apps/msos-web", bullets)

    def test_refresh_dedupes_same_sha(self) -> None:
        (self.repo / "note.txt").write_text("a\n", encoding="utf-8")
        _commit(self.repo, "second commit", date="2026-06-02T10:00:00+00:00")
        self.assertEqual(cmd_refresh(self.repo), 0)
        state1 = load_state(self.repo)
        count1 = len(state1.recorded_shas)
        self.assertEqual(cmd_refresh(self.repo), 0)
        state2 = load_state(self.repo)
        self.assertEqual(len(state2.recorded_shas), count1)

    def test_refresh_day_quiet_stub(self) -> None:
        self.assertEqual(cmd_refresh(self.repo, day="2026-01-15"), 0)
        text = (self.repo / "docs" / "RELEASES" / "DEV_CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## 2026-01-15", text)
        self.assertIn(QUIET_STUB, text)

    def test_append_chapter_closed_event(self) -> None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        plan = {
            "slices": [
                {
                    "sliceId": "MSOS-P2-Closeout-Slice005",
                    "closeout": {
                        "chapterTitle": "MSOS P2 homepage",
                    },
                }
            ]
        }
        plan_path = self.repo / "docs" / "SOP" / "PHASE_PLANS" / "p2.json"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(json.dumps(plan), encoding="utf-8")

        self.assertEqual(
            append_chapter_closed_event(
                self.repo,
                slice_id="MSOS-P2-Closeout-Slice005",
                phase_plan=plan_path,
            ),
            0,
        )
        parsed = load_changelog(self.repo)
        self.assertIn(today, parsed.sections)
        joined = "\n".join(parsed.sections[today])
        self.assertIn("MSOS P2 homepage", joined)
        self.assertIn("MSOS-P2-Closeout-Slice005", joined)

        self.assertEqual(
            append_chapter_closed_event(
                self.repo,
                slice_id="MSOS-P2-Closeout-Slice005",
                phase_plan=plan_path,
            ),
            0,
        )
        self.assertEqual(len(parsed.sections[today]), len(load_changelog(self.repo).sections[today]))

    def test_backfill_skips_recorded_shas(self) -> None:
        (self.repo / "a.txt").write_text("1\n", encoding="utf-8")
        sha = _commit(self.repo, "backfill one", date="2026-05-20T10:00:00+00:00")
        state = load_state(self.repo)
        state.recorded_shas.append(sha)
        save_state(self.repo, state)

        self.assertEqual(cmd_backfill(self.repo, days=30), 0)
        self.assertTrue(state_path(self.repo).is_file())
        self.assertIn(sha, load_state(self.repo).recorded_shas)


if __name__ == "__main__":
    unittest.main()
