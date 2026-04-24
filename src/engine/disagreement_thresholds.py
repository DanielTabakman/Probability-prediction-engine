"""
Single source for belief-vs-market disagreement thresholds (peak, width, L1 shape gap).

Moved out of src.viz to keep services/engine independent from visualization modules.
The src.viz module remains as a shim re-export for UI stability.
"""

from __future__ import annotations

# Peak alignment: |center - market_peak| < max(PEAK_ALIGN_ABS_MIN_USD, PEAK_ALIGN_REL_TO_MARKET_PEAK * market_peak)
PEAK_ALIGN_ABS_MIN_USD = 1.0
PEAK_ALIGN_REL_TO_MARKET_PEAK = 0.002

# Width band vs ATM-implied σ at horizon: compare sigma_user to sigma_mkt * ratio
WIDTH_NARROWER_RATIO = 0.92
WIDTH_WIDER_RATIO = 1.08

# L1 density gap ∫|f_user - f_ref| dx → Low / Moderate / High (belief summary only; not category)
L1_SHAPE_GAP_LOW_BELOW = 0.28
L1_SHAPE_GAP_MODERATE_BELOW = 0.52


def peak_alignment_tolerance_usd(market_peak: float) -> float:
    return max(PEAK_ALIGN_ABS_MIN_USD, PEAK_ALIGN_REL_TO_MARKET_PEAK * float(market_peak))

