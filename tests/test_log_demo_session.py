"""Tests for demo session logging."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.log_demo_session import append_jsonl, build_row, format_markdown_row


def test_build_row_and_jsonl(tmp_path: Path) -> None:
    row = build_row(profile="friend", clarity="Y", return_again="N", asset="NVDA", notes="monitor BTC")
    assert row["pass"] == "Y"
    assert row["return_again"] == "N"
    assert "NVDA" in format_markdown_row(row)
    out = append_jsonl(tmp_path, row)
    assert out.is_file()
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    parsed = json.loads(lines[-1])
    assert parsed["profile"] == "friend"
