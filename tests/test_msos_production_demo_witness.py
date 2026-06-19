"""Tests for MSOS production demo witness helpers."""

from __future__ import annotations

from scripts.msos_production_demo_witness import _has_research_cta


def test_has_research_cta_positive() -> None:
    html = '<a href="mailto:a@b.com">Request research beta access</a>'
    assert _has_research_cta(html) is True


def test_has_research_cta_negative() -> None:
    assert _has_research_cta("<p>Explore the platform</p>") is False
