from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

PresetId = Literal["bull_call_spread", "bear_put_spread", "short_iron_fly"]


@dataclass(frozen=True)
class ImpliedLabPreset:
    preset_id: PresetId
    label: str


PRESETS: dict[PresetId, ImpliedLabPreset] = {
    "bull_call_spread": ImpliedLabPreset(
        preset_id="bull_call_spread",
        label="Bull call spread",
    ),
    "bear_put_spread": ImpliedLabPreset(
        preset_id="bear_put_spread",
        label="Bear put spread",
    ),
    "short_iron_fly": ImpliedLabPreset(
        preset_id="short_iron_fly",
        label="Short iron fly",
    ),
}


def _snap_to_strike(avail_strikes: list[float], target: float) -> float:
    if not avail_strikes:
        return float(target)
    return float(min(avail_strikes, key=lambda k: abs(float(k) - float(target))))


def _ordered_k(k1: float, k2: float, k3: float, k4: float) -> tuple[float, float, float, float]:
    # Keep monotone ordering without silently swapping the intended body pair.
    k2 = max(k2, k1)
    k3 = max(k3, k2)
    k4 = max(k4, k3)
    return float(k1), float(k2), float(k3), float(k4)


def compute_preset_shape(
    *,
    preset_id: PresetId,
    forward: float,
    avail_strikes: list[float],
) -> dict[str, Any]:
    """
    Pure mapping: a preset picks strikes + leg toggles + polarity using the universal 4-leg model.

    The caller owns how this is written into Streamlit session state.
    """
    if preset_id not in PRESETS:
        raise KeyError(f"Unknown preset_id: {preset_id}")

    atm = _snap_to_strike(avail_strikes, float(forward))
    # Aim for a visible width change without assuming a particular strike increment.
    width_hint = max(2_000.0, abs(float(forward)) * 0.10)
    left = _snap_to_strike(avail_strikes, atm - width_hint)
    right = _snap_to_strike(avail_strikes, atm + width_hint)

    # Default strikes (used even when some legs are disabled, to keep naming stable).
    k1, k2, k3, k4 = _ordered_k(left, atm, atm, right)

    if preset_id == "bull_call_spread":
        return {
            "k1": k1,
            "k2": k2,
            "k3": k3,
            "k4": k4,
            "use_k1": False,
            "use_k2": False,
            "use_k3": True,
            "use_k4": True,
            "reverse": False,
            "qty": 1,
        }
    if preset_id == "bear_put_spread":
        return {
            "k1": k1,
            "k2": k2,
            "k3": k3,
            "k4": k4,
            "use_k1": True,
            "use_k2": True,
            "use_k3": False,
            "use_k4": False,
            "reverse": False,
            "qty": 1,
        }
    if preset_id == "short_iron_fly":
        return {
            "k1": k1,
            "k2": k2,
            "k3": k3,
            "k4": k4,
            "use_k1": True,
            "use_k2": True,
            "use_k3": True,
            "use_k4": True,
            # Base polarity is (short, long, long, short). Reverse => (long, short, short, long).
            # This yields a short-premium-like peaked shape around the body strikes.
            "reverse": True,
            "qty": 1,
        }

    # Exhaustiveness guard (should be unreachable due to PresetId Literal).
    raise KeyError(f"Unhandled preset_id: {preset_id}")


def preset_label(preset_id: PresetId) -> str:
    return PRESETS[preset_id].label


def preset_what_changed(*, preset_id: PresetId, shape: dict[str, Any]) -> str:
    """
    Pure mapping: explain the effect of applying a preset in plain English.

    Sprint 001 — Slice 006 (Phase 2): "Last action" meaning readout.
    """
    label = preset_label(preset_id)
    enabled: list[str] = []
    disabled: list[str] = []
    for leg in ("k1", "k2", "k3", "k4"):
        flag = bool(shape.get(f"use_{leg}", True))
        (enabled if flag else disabled).append(leg.upper())

    def _fmt_usd(x: Any) -> str:
        try:
            v = float(x)
        except Exception:
            return "—"
        if abs(v) >= 1000:
            return f"${v:,.0f}"
        return f"${v:.2f}"

    ks = {k: _fmt_usd(shape.get(k)) for k in ("k1", "k2", "k3", "k4")}
    reverse = bool(shape.get("reverse", False))
    polarity = "reversed (long/short flipped)" if reverse else "normal"
    qty = shape.get("qty", 1)

    parts: list[str] = [
        f"Applied preset: **{label}**.",
        f"Enabled legs: {', '.join(enabled) if enabled else '—'}.",
        f"Disabled legs: {', '.join(disabled) if disabled else '—'}.",
        f"Strikes set to K1 {ks['k1']} · K2 {ks['k2']} · K3 {ks['k3']} · K4 {ks['k4']}.",
        f"Polarity: {polarity}.",
        f"Quantity: {qty}.",
    ]
    return " ".join(parts)
