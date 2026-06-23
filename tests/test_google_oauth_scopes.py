"""Google OAuth scope policy for sync scripts."""

from __future__ import annotations

from scripts.google_oauth_scopes import MCP_GOOGLE_SCOPES, SYNC_GOOGLE_SCOPES


def test_sync_scopes_cover_documents_and_drive_read() -> None:
    assert "https://www.googleapis.com/auth/documents" in SYNC_GOOGLE_SCOPES
    assert any("drive" in scope for scope in SYNC_GOOGLE_SCOPES)


def test_sync_scopes_exclude_gmail_and_calendar() -> None:
    joined = " ".join(SYNC_GOOGLE_SCOPES)
    assert "gmail" not in joined
    assert "calendar" not in joined
