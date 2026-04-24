from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def snap_to_nearest_strike(
    strike: float | int | None,
    avail_strikes: Iterable[float | int] | None,
) -> float | int | None:
    """
    Pure helper: snap `strike` to the nearest value in `avail_strikes`.

    Returns `strike` unchanged when `strike` is None or `avail_strikes` is empty/None.
    """
    if strike is None:
        return None
    if not avail_strikes:
        return strike

    try:
        strikes_list = list(avail_strikes)
    except TypeError:
        return strike
    if not strikes_list:
        return strike

    try:
        target = float(strike)
    except Exception:
        return strike

    return min(strikes_list, key=lambda k: abs(float(k) - target))


def enforce_non_decreasing_4(
    k1: float | int | None,
    k2: float | int | None,
    k3: float | int | None,
    k4: float | int | None,
) -> tuple[float | int | None, float | int | None, float | int | None, float | int | None]:
    """
    Pure helper: enforce k1 <= k2 <= k3 <= k4, matching existing UI behavior.

    If any strike is None/unorderable, returns values unchanged.
    """
    try:
        if k1 is None or k2 is None or k3 is None or k4 is None:
            return k1, k2, k3, k4
        if not (k1 <= k2 <= k3 <= k4):
            k2 = max(k2, k1)
            k3 = max(k3, k2)
            k4 = max(k4, k3)
        return k1, k2, k3, k4
    except Exception:
        return k1, k2, k3, k4


def snap_and_order_u4_strikes(
    k1: Any,
    k2: Any,
    k3: Any,
    k4: Any,
    *,
    avail_strikes: Iterable[float | int] | None,
) -> tuple[float | int | None, float | int | None, float | int | None, float | int | None]:
    """
    Minimal extraction for the 4-leg (K1..K4) UI:
    - snap each provided strike to nearest available strike
    - enforce k1 <= k2 <= k3 <= k4 (preserving current behavior)
    - gracefully handle None/empty inputs
    """
    k1s = snap_to_nearest_strike(None if k1 is None else float(k1), avail_strikes)
    k2s = snap_to_nearest_strike(None if k2 is None else float(k2), avail_strikes)
    k3s = snap_to_nearest_strike(None if k3 is None else float(k3), avail_strikes)
    k4s = snap_to_nearest_strike(None if k4 is None else float(k4), avail_strikes)

    return enforce_non_decreasing_4(k1s, k2s, k3s, k4s)

