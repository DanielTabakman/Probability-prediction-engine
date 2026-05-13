"""Helpers for demo → private app call-to-action (no Streamlit imports)."""


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
