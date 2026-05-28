"""Phase 3 commercial wrapper v0 — shared demo CTA/offer copy and operator checklist."""

from __future__ import annotations

from src.viz.mvp1_product_shell import assert_no_signal_language

PRIVATE_APP_CTA_LABEL = "Get full access"
PRIVATE_APP_CTA_CAPTION = "Sign in on the full app to save snapshots and reviews."

DEMO_HERO_TAGLINE = (
    "Market-implied distributions and prediction markets — exploration, not advice."
)

PUBLIC_DEMO_BANNER = (
    "**Public demo:** no saved snapshot history here. "
    "**Get full access** opens the full app with saves and reviews."
)

RESEARCH_OFFER_HEADLINE = "**Research beta (v0):**"
RESEARCH_OFFER_BODY = (
    "BTC options market-structure readouts and anomaly inspection — "
    "decision support only, not investment advice or promised returns."
)

COMMERCIAL_BOUNDARY_CAPTION = (
    "Research exploration only; not trade advice, edge claims, or execution."
)


def research_offer_markdown() -> str:
    """Single markdown block for the research-offer strip above the CTA button."""
    return f"{RESEARCH_OFFER_HEADLINE} {RESEARCH_OFFER_BODY}"


def operator_checklist_markdown() -> str:
    """
    Lightweight operator checklist for public-demo sessions (copy-only; no automation).
    """
    return """\
### Before the session
- Set `PPE_ENABLE_SNAPSHOTS=0` on the **demo** service.
- Set `PPE_PRIVATE_APP_URL` (HTTPS) and `PPE_RESEARCH_OFFER_URL` (`https://` or `mailto:`).
- Optional: `PPE_RESEARCH_OFFER_LABEL` for the offer button text.

### During (~10 min)
1. Open the public demo — confirm **Get full access** and **Research beta (v0)** when env is set.
2. Walk MVP1 output + chart — market-implied read, not a buy/sell call.
3. Explain candidate / watch / no-trade and trust/degraded states without edge claims.
4. Offer one path: research beta, weekly brief, or bespoke call (steward picks one).
5. Ask willingness to pay; record exact words for reality-check logs.

### Do not say
- Promised profit, proven alpha, or trade-signal language.
- Fully automated trading or multi-asset product ready today.

### After
- Log outreach in steward reality-check / ops docs when a live conversation completes.
"""


def validate_all_wrapper_copy() -> None:
    """Guardrail: every shipped wrapper string must pass signal-language checks."""
    for text in (
        PRIVATE_APP_CTA_LABEL,
        PRIVATE_APP_CTA_CAPTION,
        DEMO_HERO_TAGLINE,
        PUBLIC_DEMO_BANNER,
        RESEARCH_OFFER_HEADLINE,
        RESEARCH_OFFER_BODY,
        research_offer_markdown(),
        COMMERCIAL_BOUNDARY_CAPTION,
        operator_checklist_markdown(),
    ):
        assert_no_signal_language(text)
