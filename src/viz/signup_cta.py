"""Helpers for demo → private app and research-offer CTAs (no Streamlit imports)."""

from __future__ import annotations

_DEFAULT_RESEARCH_OFFER_LABEL = "Request research beta access"


def private_app_cta_url(*, snapshots_enabled: bool, private_app_url: str | None) -> str | None:
    """
    Return the URL to advertise when the demo should nudge users toward the full app.

    Show CTA only when snapshots are disabled (demo), a non-empty URL is configured,
    and the URL uses HTTPS.
    """
    if snapshots_enabled:
        return None
    url = (private_app_url or "").strip()
    if not url:
        return None
    if not url.lower().startswith("https://"):
        return None
    return url


def _allowed_offer_url(url: str) -> bool:
    lower = url.lower()
    return lower.startswith("https://") or lower.startswith("mailto:")


def research_offer_cta(
    *,
    snapshots_enabled: bool,
    offer_url: str | None,
    offer_label: str | None = None,
) -> tuple[str, str] | None:
    """
    Return (url, button_label) for the public-demo research-offer CTA.

    Shown only when snapshots are disabled (demo mode) and URL is https:// or mailto:.
    """
    if snapshots_enabled:
        return None
    url = (offer_url or "").strip()
    if not url or not _allowed_offer_url(url):
        return None
    label = (offer_label or "").strip() or _DEFAULT_RESEARCH_OFFER_LABEL
    return url, label
