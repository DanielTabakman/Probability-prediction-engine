"""Tests for cross-venue research WSGI boundary."""

from __future__ import annotations

from src.viz.cross_venue_research_boundary import (
    CROSS_VENUE_RESEARCH_HTTP_PATH,
    build_cross_venue_research_response,
    handle_cross_venue_research_wsgi_path,
)


def test_handle_cross_venue_research_wsgi_path() -> None:
    result = handle_cross_venue_research_wsgi_path(CROSS_VENUE_RESEARCH_HTTP_PATH, {})
    assert result is not None
    status, body = result
    assert status == "200 OK"
    assert b"cross_venue_research_boundary" in body


def test_build_response_has_kind() -> None:
    payload = build_cross_venue_research_response()
    assert payload.get("kind") == "cross_venue_research_boundary"
