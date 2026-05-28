"""MVP1 product shell copy — name hierarchy and path labels (display-only)."""

from __future__ import annotations

PLATFORM_NAME = "Probability Engine"
WORKSPACE_NAME = "BTC Implied Lab"

FORBIDDEN_SIGNAL_TOKENS = (
    "best trade",
    "recommended",
    "guaranteed",
    "high edge",
    "you should buy",
)


def product_hierarchy_line() -> str:
    """Primary + secondary product names for first-session clarity."""
    return f"**{PLATFORM_NAME}** → **{WORKSPACE_NAME}**"


def workspace_context_caption() -> str:
    return (
        "You are in the BTC options **implied lab** — market-implied readouts and belief overlay. "
        "Research exploration only; not trade advice."
    )


def feedback_path_hint() -> str:
    return (
        "**Feedback:** use **Give feedback** in the panel below to flag confusion, usefulness, "
        "or repeat-use intent (saved locally on this device)."
    )


def assert_no_signal_language(text: str) -> None:
    low = text.lower()
    for tok in FORBIDDEN_SIGNAL_TOKENS:
        if tok in low:
            raise AssertionError(f"forbidden signal language: {tok!r}")
