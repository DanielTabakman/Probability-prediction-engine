"""Minimal Google OAuth scopes for CI sync scripts (not MCP)."""

from __future__ import annotations

# Used by scripts/google_docs_sync.py and scripts/verify_msos_mirror_timestamp.py.
# - documents: read/write MSOS mirror marker block
# - drive.readonly: export PPE Master markdown from Google Docs
SYNC_GOOGLE_SCOPES: tuple[str, ...] = (
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.readonly",
)

# Broader scopes used by local @a-bonus/google-docs-mcp (Cursor). Do not use in CI.
MCP_GOOGLE_SCOPES: tuple[str, ...] = (
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/script.external_request",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.events",
)
