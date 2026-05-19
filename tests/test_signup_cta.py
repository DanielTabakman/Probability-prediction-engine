"""Unit tests for demo → private app CTA URL logic (no Streamlit / app import)."""

from src.viz.signup_cta import private_app_cta_url, research_offer_cta


def test_cta_url_when_snapshots_off_and_url_set():
    assert (
        private_app_cta_url(
            snapshots_enabled=False,
            private_app_url="https://app.example.com",
        )
        == "https://app.example.com"
    )


def test_cta_url_strips_whitespace():
    assert (
        private_app_cta_url(
            snapshots_enabled=False,
            private_app_url="  https://app.example.com  ",
        )
        == "https://app.example.com"
    )


def test_cta_suppressed_when_snapshots_on():
    assert (
        private_app_cta_url(
            snapshots_enabled=True,
            private_app_url="https://app.example.com",
        )
        is None
    )


def test_cta_suppressed_when_url_not_https():
    assert private_app_cta_url(snapshots_enabled=False, private_app_url="http://app.example.com") is None


def test_cta_suppressed_when_url_empty_or_none():
    assert private_app_cta_url(snapshots_enabled=False, private_app_url=None) is None
    assert private_app_cta_url(snapshots_enabled=False, private_app_url="") is None
    assert private_app_cta_url(snapshots_enabled=False, private_app_url="   ") is None


def test_research_offer_https_and_default_label():
    got = research_offer_cta(
        snapshots_enabled=False,
        offer_url="https://cal.example.com/book",
        offer_label=None,
    )
    assert got == ("https://cal.example.com/book", "Request research beta access")


def test_research_offer_mailto_and_custom_label():
    got = research_offer_cta(
        snapshots_enabled=False,
        offer_url="mailto:research@example.com?subject=PPE%20beta",
        offer_label="  Email for beta access  ",
    )
    assert got == ("mailto:research@example.com?subject=PPE%20beta", "Email for beta access")


def test_research_offer_suppressed_when_snapshots_on():
    assert (
        research_offer_cta(
            snapshots_enabled=True,
            offer_url="https://cal.example.com/book",
        )
        is None
    )


def test_research_offer_suppressed_for_invalid_scheme():
    assert research_offer_cta(snapshots_enabled=False, offer_url="http://bad.example.com") is None
    assert research_offer_cta(snapshots_enabled=False, offer_url="") is None
