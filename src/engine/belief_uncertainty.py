"""
Belief uncertainty input helpers.

Internal belief model uses σ_ln: standard deviation of ln(price) at expiry.
This module provides a human-scaled mapping to/from an intuitive "±% move (1σ)".

Moved out of src.viz to keep services/engine independent from visualization modules.
The src.viz module remains as a shim re-export for UI stability.
"""

from __future__ import annotations

import math


def sigma_ln_to_move_pct_1sigma(sigma_ln: float) -> float:
    """
    Convert σ_ln to an intuitive ±% move for a 1σ change.

    With ln S ~ N(μ, σ²), a ±1σ move corresponds to S being multiplied by exp(±σ).
    We report the symmetric magnitude using the upside move: (exp(σ) - 1) × 100.
    """
    s = float(sigma_ln)
    if not math.isfinite(s) or s <= 0:
        return 0.0
    return (math.exp(s) - 1.0) * 100.0


def move_pct_1sigma_to_sigma_ln(move_pct_1sigma: float) -> float:
    """
    Convert an intuitive ±% move (1σ) to σ_ln.

    move_pct_1sigma = (exp(σ) - 1) × 100  =>  σ = ln(1 + move_pct/100).
    """
    p = float(move_pct_1sigma)
    if not math.isfinite(p) or p <= 0:
        return 0.0
    return math.log1p(p / 100.0)

