"""
Chromeless Streamlit entry for Strategy Lab embed (distribution region only).

Run: ``streamlit run src/viz/app_embed.py``

Query params:
  - ``embed_only=1`` — same chromeless view (default for this entry)
  - ``format=json`` — inline JSON payload for display API consumers
"""

from __future__ import annotations

import streamlit as st

from src.viz.app_env import APP_ROOT  # noqa: F401 — bootstrap repo root on sys.path
from src.viz.embed_only_lab import run_embed_only_lab_page

st.set_page_config(
    page_title="PPE Distribution (embed)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

run_embed_only_lab_page()
