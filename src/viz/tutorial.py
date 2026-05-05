"""
In-app tutorial content for Streamlit.

Keep this as a small helper module so `src/viz/app.py` stays readable.
"""

from __future__ import annotations

import streamlit as st


def render_tutorial_section() -> None:
    st.markdown(
        """
### What this app is
This is a **local-first** Streamlit workbench for comparing **market data** and **prediction markets**, and for running the **Bitcoin implied lab (MVP1)** workflow:
freeze → reopen → review → class summary.

### Quick start
- Run: `streamlit run src/viz/app.py`
- Use the sidebar **Refresh priced inputs (Deribit)** when you want fresh quotes.

### Walkthrough

#### 1) Markets + Polymarket (reference sections)
- Use the sidebar toggles for **Market prices (Yahoo)** and **Prediction markets (Polymarket)**.
- These are **reference-only** blocks to orient you; they are not trade recommendations.

#### 2) Bitcoin implied lab (main workflow)
- Open **Bitcoin implied lab — market-implied view as the anchor**.
- Pick an **expiry** and use the panels to inspect the market-implied distribution and the belief overlay.

#### 3) Phase 4 — Freeze & reopen
- Open **Freeze & history (this device, SQLite)**.
- Click **Freeze this evaluation**.
- Pick a frozen record and click **Reopen read-only view**.

#### 4) Phase 5 — Review
- In **Read-only: frozen snapshot**, set **Review status** and add **Outcome notes**.
- Click **Save review**.
- Reviewed snapshots disappear from **Pending snapshot reviews** once non-pending.

#### 5) Phase 6 — Class summary
- Open **Class summary — reviewed snapshots (Phase 6)**.
- Filter by status / expiry / reviewed date.
- Use **Open** buttons to jump to specific reviewed snapshots.
- Download rollup JSON / reviewed rows CSV.

### Tips
- If the app feels slow, use **Compute/Refresh** actions (when available) instead of expecting every checkbox to recompute instantly.
- If you want the full post-MVP lab workbench, set `PPE_POST_MVP1_LAB_UI=1`.
"""
    )

