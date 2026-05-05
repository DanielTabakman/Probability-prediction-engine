"""MVP1 implied-lab UI scope: default hides post-MVP strike/payoff/ticket chrome."""

from __future__ import annotations

import os
from typing import Sequence

import streamlit as st

from src.viz.implied_lab_presets import PRESETS, compute_preset_shape


def post_mvp1_lab_ui_enabled() -> bool:
    """When true, show full implied-lab workbench (strikes, payoff solver, trade ticket)."""
    v = (os.environ.get("PPE_POST_MVP1_LAB_UI") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def ensure_mvp1_lab_default_shape(
    *,
    shape_key: str,
    mode_key: str,
    expiry_str: str,
    forward: float,
    avail_strikes: Sequence[float],
) -> None:
    """
    Seed session shape from the first preset when MVP1 mode hides strike controls,
    so derive_lab_outputs still has a deterministic internal strategy state.
    """
    if mode_key not in st.session_state:
        st.session_state[mode_key] = "Exact strikes"
    cur = st.session_state.get(shape_key)
    need = not isinstance(cur, dict) or not all(
        k in cur
        for k in (
            "k1",
            "k2",
            "k3",
            "k4",
            "use_k1",
            "use_k2",
            "use_k3",
            "use_k4",
            "reverse",
            "qty",
        )
    )
    if need:
        pid = next(iter(PRESETS))
        shape = compute_preset_shape(
            preset_id=pid,
            forward=float(forward),
            avail_strikes=[float(x) for x in avail_strikes],
        )
        st.session_state[shape_key] = {
            "k1": float(shape["k1"]),
            "k2": float(shape["k2"]),
            "k3": float(shape["k3"]),
            "k4": float(shape["k4"]),
            "reverse": bool(shape["reverse"]),
            "use_k1": bool(shape["use_k1"]),
            "use_k2": bool(shape["use_k2"]),
            "use_k3": bool(shape["use_k3"]),
            "use_k4": bool(shape["use_k4"]),
            "qty": int(shape.get("qty", 1)),
        }
        st.session_state[f"implied_lab_last_preset_{expiry_str}"] = pid
