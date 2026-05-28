"""Phase 3 commercial wrapper v0 — demo CTAs, signal guardrails, operator checklist."""

from __future__ import annotations

from dataclasses import dataclass

from src.viz.mvp1_product_shell import assert_no_signal_language
from src.viz.signup_cta import private_app_cta_url, research_offer_cta

COMMERCIAL_FORBIDDEN_SIGNAL_TOKENS = (
    "best trade",
    "recommended",
    "guaranteed",
    "high edge",
    "you should buy",
    "guaranteed returns",
    "proven alpha",
    "buy signal",
    "sell signal",
)

APP_TAGLINE = (
    "Market-implied distributions and prediction markets — exploration, not advice."
)
PRIVATE_APP_CTA_LABEL = "Get full access"
PRIVATE_APP_CTA_CAPTION = "Sign in on the full app to save snapshots and reviews."
DEMO_BANNER = (
    "**Public demo:** no saved snapshot history here. "
    "**Get full access** opens the full app with saves and reviews."
)
RESEARCH_OFFER_BLURB = (
    "**Research beta (v0):** BTC options market-structure readouts and anomaly inspection — "
    "decision support only, not investment advice or promised returns."
)


def assert_commercial_copy_safe(text: str) -> None:
    """Raise if commercial surface copy includes forbidden signal language."""
    low = text.lower()
    for tok in COMMERCIAL_FORBIDDEN_SIGNAL_TOKENS:
        if tok in low:
            raise AssertionError(f"forbidden signal language: {tok!r}")
    assert_no_signal_language(text)


@dataclass(frozen=True)
class CommercialSurfaceCopy:
    tagline: str
    private_app_label: str
    private_app_caption: str
    demo_banner: str
    research_offer_blurb: str


@dataclass(frozen=True)
class OperatorChecklistItem:
    step_id: str
    label: str
    detail: str


def commercial_surface_copy() -> CommercialSurfaceCopy:
    copy = CommercialSurfaceCopy(
        tagline=APP_TAGLINE,
        private_app_label=PRIVATE_APP_CTA_LABEL,
        private_app_caption=PRIVATE_APP_CTA_CAPTION,
        demo_banner=DEMO_BANNER,
        research_offer_blurb=RESEARCH_OFFER_BLURB,
    )
    for value in (
        copy.tagline,
        copy.private_app_label,
        copy.private_app_caption,
        copy.demo_banner,
        copy.research_offer_blurb,
    ):
        assert_commercial_copy_safe(value)
    return copy


def operator_checklist() -> tuple[OperatorChecklistItem, ...]:
    items = (
        OperatorChecklistItem(
            step_id="env_snapshots",
            label="Disable snapshots on the public demo",
            detail="Set `PPE_ENABLE_SNAPSHOTS=0` so the demo shows CTAs and no saved history.",
        ),
        OperatorChecklistItem(
            step_id="env_private_url",
            label="Configure full-app URL",
            detail="Set `PPE_PRIVATE_APP_URL` to an https:// URL for the **Get full access** CTA.",
        ),
        OperatorChecklistItem(
            step_id="env_offer_url",
            label="Configure research-offer URL",
            detail=(
                "Set `PPE_RESEARCH_OFFER_URL` to https:// or mailto:; optional "
                "`PPE_RESEARCH_OFFER_LABEL` overrides the button label."
            ),
        ),
        OperatorChecklistItem(
            step_id="commercial_boundary",
            label="Keep copy within commercial boundary",
            detail=(
                "Do not promise risk-free profit, alpha claims, or trade signals. "
                "Sell legibility and decision-support discipline only."
            ),
        ),
        OperatorChecklistItem(
            step_id="verify_ctas",
            label="Verify CTAs before outreach",
            detail=(
                "Open the demo, confirm hero CTAs render, and walk the ~10 min "
                "conversation script from the operator playbook."
            ),
        ),
    )
    for item in items:
        assert_commercial_copy_safe(item.label)
        assert_commercial_copy_safe(item.detail)
    return items


def resolve_demo_ctas(
    *,
    snapshots_enabled: bool,
    private_app_url: str | None,
    offer_url: str | None,
    offer_label: str | None = None,
) -> tuple[str | None, tuple[str, str] | None]:
    """Resolve demo CTAs using env gates; validates offer label when present."""
    private_url = private_app_cta_url(
        snapshots_enabled=snapshots_enabled,
        private_app_url=private_app_url,
    )
    offer = research_offer_cta(
        snapshots_enabled=snapshots_enabled,
        offer_url=offer_url,
        offer_label=offer_label,
    )
    if offer is not None:
        _url, label = offer
        assert_commercial_copy_safe(label)
    return private_url, offer
