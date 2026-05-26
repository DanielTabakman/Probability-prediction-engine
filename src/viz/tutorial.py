"""
In-app tutorial content for Streamlit.

Keep this as a small helper module so `src/viz/app.py` stays readable.
"""

from __future__ import annotations

import streamlit as st


def render_tutorial_section(
    *,
    show_dev_sections: bool = False,
    show_demo_cta: bool = False,
) -> None:
    st.markdown(
        """
**What you’re looking at:** Bitcoin **options-implied** curves plus **prediction-market** context —
a way to compare what is **priced in** with **your own** view.
"""
    )
    st.caption("Exploration only — not trading advice.")

    st.markdown("**Try this (in order)**")
    st.markdown(
        """
1. In the **sidebar** (under **Data**), click **Refresh priced inputs (Deribit)** once when you want **live option quotes** and chart overlays.
2. Stay on this page: keep **Bitcoin view** checked in the sidebar, then find **Bitcoin implied lab — market-implied view as the anchor** below and pick an **Expiry**.
3. Use the **left** column for belief / shape; the **right** side is the **market-implied** chart.
4. Open **Belief vs market — at a glance** (a short readout of where you disagree with the market-implied curve).
5. For extra context (not trade ideas): open **Market context (price chart + prediction questions)** lower on the page, and the **Market prices (reference)** / **Prediction markets (reference)** expanders — all **reference only**.
"""
    )

    st.caption(
        "Purple / orange / green lines on the main implied chart: see **How to read this chart** under "
        "**Market-implied distribution (anchor)** below."
    )

    with st.expander("Saving snapshots and reviews (full app)", expanded=False):
        if show_demo_cta:
            st.markdown(
                """
This **public demo** tab does not keep saved snapshot history on the server. The **full app** lets you
**freeze** a lab state, **reopen** it later, add **reviews**, and use **Class summary** over time.
Click **Get full access** at the top when you see it (same destination as the short banner above).
"""
            )
        else:
            st.markdown(
                """
On this deployment you can **freeze** a lab state, **reopen** it later, add **reviews**, and use
**Class summary** when those features are enabled. Look for **Freeze & history** under the implied lab.
"""
            )

    if show_dev_sections:
        with st.expander("Running locally", expanded=False):
            st.markdown("From the repo root: `streamlit run src/viz/app.py`")

    if st.button("Got it — collapse this intro", key="ppe_tutorial_got_it"):
        st.session_state["ppe_tutorial_intro_done"] = True
        st.rerun()


def render_how_it_works_expander(*, expanded: bool = False) -> None:
    """MVP1 §15B slice 5: plain-language map of the implied lab (copy only; no math)."""
    with st.expander("How this lab works (~90 sec)", expanded=expanded):
        st.markdown(
            """
**Market-implied distribution**  
The main chart is built from **live option prices** (Deribit) for a chosen **expiry**. It answers:
“Given today’s quotes, what **probability shape** over BTC levels is roughly priced in?” It is a **market readout**, not a forecast of what *will* happen.

**Belief overlay**  
In **MVP1 compact** mode you can still set a **simple belief curve** (plain-language controls on the left). That overlay is **your** stated view — optional, and always shown **against** the market-implied curve, not instead of it.

**Disagreement**  
When belief is on, **Belief vs market — at a glance** summarizes **where** your curve and the market-implied curve differ in plain language. It is **diagnostic** (where views diverge), not a buy/sell signal.

**Strategy families (fit, not recommendation)**  
Deeper panels may show **strategy shapes** that **fit** the disagreement story. Language stays **non-prescriptive**: families are **illustrative structure**, not ranked “best trades” or guaranteed edge.

**Boundary — not advice**  
This app is a **research cockpit** for exploration and learning. Nothing here is personalized investment, tax, or legal advice; there are **no** promises of returns. Prefer **Freeze & history** (when enabled) to capture what you reviewed, not as a trade log.
"""
        )
        st.caption("Exploration only — not trading advice.")
