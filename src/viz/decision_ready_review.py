"""
Sprint 005: display-only copy for decision-ready trade review (structure + payoff read + disagreement link).

No new semantics: strings are derived from existing verification / glance payloads only.
"""

from __future__ import annotations

from typing import Any

# Guardrail for tests — advisory language must not appear in generated copy.
FORBIDDEN_ADVISORY_TOKENS = (
    "best ",
    "optimal",
    "recommended",
    "you should",
    "correct trade",
    "high edge",
)


def _payoff_shape_plain(name: str, debit_credit: str | None) -> str:
    """Human-readable payoff shape from strategy label + debit/credit (illustrative only)."""
    n = name.lower()
    dc_clause = ""
    if debit_credit == "debit":
        dc_clause = " Opened as a **net debit** (premium paid net)."
    elif debit_credit == "credit":
        dc_clause = " Opened as a **net credit** (premium received net)."

    if "iron condor" in n:
        body = (
            "**Range-bound** payoff between inner strikes with **capped** risk at the wings "
            "(see the green expiry P&L line and Summary extremes)."
        )
    elif "iron butterfly" in n:
        body = (
            "**Peaked** payoff near the body strikes with **capped** wing risk "
            "(green line shows how P&L changes with spot at expiry)."
        )
    elif "short strangle" in n or "short straddle" in n:
        body = (
            "**Short-volatility-style** payoff: gains if spot stays near the short strikes; "
            "tails matter for max loss — use the green line and Summary."
        )
    elif "strangle" in n or "straddle" in n:
        if "capped" in n:
            body = (
                "**Straddle/strangle-family** payoff with **modified** wings — "
                "inspect the green line for where risk flattens or caps."
            )
        else:
            body = (
                "**Straddle/strangle-family** payoff: premium paid for **breakout / vol** expression "
                "(green line at expiry)."
            )
    elif "risk reversal" in n or "spread + long" in n:
        body = (
            "**Directional overlay** shape: combines spreads with a long option leg for tilt or hedge "
            "(read the green line for how payoff leans with spot)."
        )
    elif "custom" in n:
        body = (
            "**Custom four-leg** payoff — use the **green line** and Summary **max gain / max loss** "
            "to see how this instantiation behaves."
        )
    else:
        body = (
            "Payoff at expiry follows the **green line**; Summary gives **max gain**, **max loss**, "
            "and breakevens for the current quantity."
        )

    return "**Payoff shape (illustrative read):** " + body + dc_clause


def build_decision_ready_review_payload(
    verification: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Build markdown-safe lines for the right-column review block.

    Returns None when there is no applicable strategy overlay (same gate as strategy_summary.applicable).
    """
    if not verification or not isinstance(verification, dict):
        return None
    ss = verification.get("strategy_summary")
    if not isinstance(ss, dict) or not ss.get("applicable"):
        return None
    vals = ss.get("values") if isinstance(ss.get("values"), dict) else {}
    name = str(vals.get("name") or "").strip() or "Active structure"
    dc_raw = vals.get("debit_credit")
    dc_str: str | None = None
    if dc_raw in ("debit", "credit"):
        dc_str = str(dc_raw)

    structure_line = (
        f"You are inspecting **{name}** — an **illustrative** multi-leg BTC structure on the chart "
        f"(green **expiry P&L** line). It is **not** a recommendation and **not** an optimized pick."
    )
    payoff_line = _payoff_shape_plain(name, dc_str)

    glance = verification.get("belief_vs_market_glance")
    has_glance = isinstance(glance, dict) and bool(glance)

    if has_glance:
        linkage_line = (
            "**How this ties together:** **Belief vs market — at a glance** is directly under this block, "
            "then **Trade ticket (copy/paste)** (one expander) for the copy-ready leg list — same numbers as "
            "**Summary**. That glance card carries the **interpretive disagreement** and **illustrative fit "
            "classes** for the same exploration; your strikes instantiate **one** concrete payoff, not a "
            "ranked choice."
        )
    else:
        linkage_line = (
            "**Belief overlay off or not linked here:** there is no **interpretive disagreement** digest "
            "in this run. The **green line** and **Summary** still describe the structure; open "
            "**Trade ticket (copy/paste)** just under the glance card (or directly under this review if the "
            "glance card is empty) for the copy-paste leg block — same numbers as **Summary**."
        )

    vs_sum = verification.get("verification_summary")
    bullets: list[str] = []
    if isinstance(vs_sum, dict):
        ob = vs_sum.get("overlay_basis")
        if isinstance(ob, str) and ob.strip():
            bullets.append(f"- **Strike construction:** {ob.strip()}")
    bullets.append(
        "- **Same numbers as Summary / ticket:** max gain, max loss, breakevens, and legs stay "
        "single-source from the engine — open **Trade ticket (copy/paste)** below the glance card "
        "(one expander) for the leg list."
    )

    fit_caption = "**Fit is not recommendation.** Illustrative structure only — same stance as the glance card."
    if has_glance and isinstance(glance, dict):
        fn = glance.get("fit_note")
        if isinstance(fn, str) and fn.strip():
            fit_caption = f"**{fn.strip()}** Illustrative structure only."

    return {
        "structure_line": structure_line,
        "payoff_line": payoff_line,
        "linkage_line": linkage_line,
        "bullets": bullets[:2],  # at most: strike construction + consistency note
        "fit_caption": fit_caption,
    }


def assert_no_advisory_language(text: str) -> None:
    """Raise AssertionError if forbidden advisory tokens appear (case-insensitive)."""
    low = text.lower()
    for tok in FORBIDDEN_ADVISORY_TOKENS:
        if tok.lower() in low:
            raise AssertionError(f"advisory/forbidden token {tok!r} in generated copy")
