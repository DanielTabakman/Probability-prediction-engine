"""Tests for MSOS mirror timestamp verification."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from scripts.verify_msos_mirror_timestamp import extract_generated_timestamp, verify_mirror_freshness


def test_extract_generated_timestamp() -> None:
    md = "**Generated (UTC):** 2026-07-02T12:00:00Z\n\n# Mirror"
    line, ts = extract_generated_timestamp(md)
    assert "2026-07-02" in line
    assert ts is not None
    assert ts.year == 2026


def test_extract_generated_timestamp_not_found() -> None:
    line, ts = extract_generated_timestamp("# No timestamp here")
    assert ts is None
    assert line == "NOT_FOUND"


def test_verify_mirror_freshness_stale() -> None:
    old = datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    md = f"**Generated (UTC):** {old}\n"
    with patch("scripts.verify_msos_mirror_timestamp.fetch_mirror_markdown", return_value=("doc-id", md)):
        report = verify_mirror_freshness(max_age_hours=24)
    assert report["ok"] is False
    assert report["fresh"] is False


def test_verify_mirror_freshness_ok() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    md = f"**Generated (UTC):** {now}\n"
    with patch("scripts.verify_msos_mirror_timestamp.fetch_mirror_markdown", return_value=("doc-id", md)):
        report = verify_mirror_freshness(max_age_hours=24)
    assert report["ok"] is True
    assert report["fresh"] is True
