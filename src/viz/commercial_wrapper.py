"""Phase 3 commercial wrapper v0 — demo CTAs, signal guardrails, operator checklist."""

from __future__ import annotations

from dataclasses import dataclass

from src.viz.signup_cta import private_app_cta_url

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
COMMERCIAL_BOUNDARY_CAPTION = (
    "Research exploration only; not trade advice, edge claims, or execution."
)
PRIVATE_APP_CTA_LABEL = "Get full access"
PRIVATE_APP_CTA_CAPTION = "Sign in on the full app to save snapshots and reviews."
DEMO_BANNER = (
    "**Public demo:** no saved snapshot history here. "
    "**Get full access** opens the full app with saves and reviews."
)


def assert_commercial_copy_safe(text: str) -> None:
    """Raise if commercial surface copy includes forbidden signal language."""
    low = text.lower()
    for tok in COMMERCIAL_FORBIDDEN_SIGNAL_TOKENS:
        if tok in low:
            raise AssertionError(f"forbidden signal language: {tok!r}")


@dataclass(frozen=True)
class CommercialSurfaceCopy:
    tagline: str
    private_app_label: str
    private_app_caption: str
    demo_banner: str


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
    )
    for value in (
        copy.tagline,
        copy.private_app_label,
        copy.private_app_caption,
        copy.demo_banner,
        COMMERCIAL_BOUNDARY_CAPTION,
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
) -> str | None:
    """Resolve private-app CTA URL using env gates."""
    return private_app_cta_url(
        snapshots_enabled=snapshots_enabled,
        private_app_url=private_app_url,
    )
