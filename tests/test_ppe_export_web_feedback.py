"""Tests for ppe_export_web_feedback.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "ppe_export_web_feedback.py"


def test_export_markdown_from_fixture_jsonl(tmp_path: Path) -> None:
    jsonl = tmp_path / "ppe_web_feedback.jsonl"
    rows = [
        {
            "id": "a",
            "created_at_utc": "2026-06-30T12:00:00Z",
            "source": "public_feedback",
            "tester_profile": "solo operator",
            "comprehension": "Y",
            "return_intent": "Y",
            "confusion_category": "value/desirability signal",
            "usefulness": 4,
            "repeat_use_intent": 5,
            "objections_text": "chart clear",
        }
    ]
    jsonl.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--path", str(jsonl), "--markdown"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    out = proc.stdout
    assert "public_feedback" in out
    assert "solo operator" in out
    assert "Average usefulness" in out


def test_export_empty_file(tmp_path: Path) -> None:
    jsonl = tmp_path / "missing.jsonl"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--path", str(jsonl), "--markdown"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "No submissions yet" in proc.stdout
