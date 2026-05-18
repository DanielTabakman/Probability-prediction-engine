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
