"""Helpers for demo → private app CTAs (no Streamlit imports)."""

from __future__ import annotations


def private_app_cta_url(*, snapshots_enabled: bool, private_app_url: str | None) -> str | None:
    if snapshots_enabled:
        return None
    url = (private_app_url or "").strip()
    if not url or not url.lower().startswith("https://"):
        return None
    return url
