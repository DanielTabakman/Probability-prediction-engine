"""Unit tests for demo → private app CTA URL logic (no Streamlit / app import)."""

from src.viz.signup_cta import private_app_cta_url


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
