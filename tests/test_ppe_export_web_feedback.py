"""Tests for ppe_export_web_feedback.py and msos_public_copy_gate.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORT_SCRIPT = REPO_ROOT / "scripts" / "ppe_export_web_feedback.py"
COPY_GATE = REPO_ROOT / "scripts" / "msos_public_copy_gate.py"


def test_export_markdown_from_fixture_jsonl(tmp_path: Path) -> None:
    jsonl = tmp_path / "ppe_web_feedback.jsonl"
    row = {
        "id": "a",
        "created_at_utc": "2026-06-30T12:00:00Z",
        "source": "public_feedback",
        "tester_profile": "solo operator",
        "comprehension": "Y",
        "return_intent": "Y",
        "confusion_category": "value/desirability signal",
        "usefulness": 4,
        "repeat_use_intent": 5,
    }
    jsonl.write_text(json.dumps(row) + "\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT), "--path", str(jsonl), "--markdown"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "public_feedback" in proc.stdout
    assert "Average usefulness" in proc.stdout


def test_public_copy_gate_passes_repo() -> None:
    from scripts.msos_public_copy_gate import run_gate

    report = run_gate(repo_root=REPO_ROOT)
    assert report["passed"] is True, report["errors"]


def test_public_copy_gate_catches_banned_html() -> None:
    from scripts.msos_public_copy_gate import scan_html

    errors, _warnings = scan_html("<html>PPE workflow store</html>", page_id="test")
    assert errors


def test_playwright_witness_imports_copy_scan() -> None:
    text = (REPO_ROOT / "scripts" / "msos_production_playwright_witness.py").read_text(
        encoding="utf-8"
    )
    assert "scan_html" in text


def test_format_digest_line_window() -> None:
    from datetime import datetime, timedelta, timezone

    from scripts.ppe_export_web_feedback import records_in_days

    now = datetime.now(timezone.utc).isoformat()
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    rows = [
        {"created_at_utc": now, "usefulness": 4, "repeat_use_intent": 5},
        {"created_at_utc": old, "usefulness": 1, "repeat_use_intent": 1},
    ]
    assert len(records_in_days(rows, 7)) == 1


def test_format_digest_line_with_env(tmp_path: Path, monkeypatch) -> None:
    from datetime import datetime, timezone

    from scripts.ppe_export_web_feedback import format_digest_line

    jsonl = tmp_path / "ppe_web_feedback.jsonl"
    row = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "usefulness": 4,
        "repeat_use_intent": 5,
    }
    jsonl.write_text(json.dumps(row) + "\n", encoding="utf-8")
    monkeypatch.setenv("PPE_WEB_FEEDBACK_DIR", str(tmp_path))
    line = format_digest_line(REPO_ROOT, days=7)
    assert line is not None
    assert "submission" in line
    assert "4.0/5" in line
