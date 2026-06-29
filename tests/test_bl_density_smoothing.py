"""Tests for Breeden-Litzenberger density smoothing (MVP1 bl_density_smoothing v1)."""

from __future__ import annotations

import math

from src.engine.implied_distribution import (
    _bl_density_from_calls,
    _integrate_density_trapezoid,
    build_distribution_chart_data,
    market_implied_density_breeden_litzenberger,
    smooth_bl_density,
)
from src.viz.distribution_export import build_distribution_export_rows
from src.viz.implied_lab_derive import derive_lab_outputs
from src.viz.implied_lab_provenance import build_trust_strip_lines


def _black_scholes_call(forward: float, strike: float, vol: float, T: float) -> float:
    if T <= 0 or vol <= 0 or forward <= 0 or strike <= 0:
        return max(0.0, forward - strike)
    sigma_sqrt_t = vol * math.sqrt(T)
    d1 = (math.log(forward / strike) + 0.5 * sigma_sqrt_t**2) / sigma_sqrt_t
    d2 = d1 - sigma_sqrt_t
    nd1 = 0.5 * (1.0 + math.erf(d1 / math.sqrt(2.0)))
    nd2 = 0.5 * (1.0 + math.erf(d2 / math.sqrt(2.0)))
    return forward * nd1 - strike * nd2


def _price_grid(k_lo: float, k_hi: float, n: int = 80) -> list[float]:
    step = (k_hi - k_lo) / max(n - 1, 1)
    return [k_lo + i * step for i in range(n)]


def test_smooth_bl_density_integrates_to_one() -> None:
    prices = [80_000.0 + i * 1_000.0 for i in range(41)]
    pdf = [0.02 + 0.01 * math.sin(i * 0.4) for i in range(len(prices))]
    pdf[20] += 0.15
    smoothed = smooth_bl_density(prices, pdf)
    assert min(smoothed) >= 0.0
    area = _integrate_density_trapezoid(prices, smoothed)
    assert abs(area - 1.0) < 0.02


def test_smooth_bl_density_dampens_interior_spike() -> None:
    prices = [float(i) for i in range(30)]
    pdf = [0.04] * len(prices)
    pdf[15] = 0.45
    smoothed = smooth_bl_density(prices, pdf)
    assert smoothed[15] < pdf[15]
    assert max(smoothed) > 0.0


def test_bl_smoothed_noisy_calls_integrates_and_nonnegative() -> None:
    forward, vol, T = 100_000.0, 0.55, 0.25
    strikes = [70_000.0 + i * 5_000.0 for i in range(15)]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    noisy = [c * (1.0 + 0.04 * math.sin(i * 1.7)) for i, c in enumerate(calls)]
    grid = _price_grid(65_000.0, 145_000.0)
    pdf = market_implied_density_breeden_litzenberger(strikes, noisy, grid)
    assert min(pdf) >= 0.0
    assert max(pdf) > 0.0
    area = _integrate_density_trapezoid(grid, pdf)
    assert abs(area - 1.0) < 0.08


def test_bl_smoothing_improves_mass_recovery_with_noise() -> None:
    forward, vol, T = 100_000.0, 0.5, 0.3
    strikes = [80_000.0 + i * 4_000.0 for i in range(12)]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    noisy = [c * (1.0 + 0.07 * math.sin(i * 2.7)) for i, c in enumerate(calls)]
    grid = _price_grid(75_000.0, 130_000.0)
    raw_pdf = _normalize_via_bl(strikes, noisy, grid, apply_smoothing=False)
    smooth_pdf = market_implied_density_breeden_litzenberger(strikes, noisy, grid)
    raw_area = _integrate_density_trapezoid(grid, raw_pdf)
    smooth_area = _integrate_density_trapezoid(grid, smooth_pdf)
    assert abs(smooth_area - 1.0) <= abs(raw_area - 1.0) + 0.02
    assert max(smooth_pdf) > 0.0


def _normalize_via_bl(
    strikes: list[float],
    calls: list[float],
    grid: list[float],
    *,
    apply_smoothing: bool,
) -> list[float]:
    return market_implied_density_breeden_litzenberger(
        strikes,
        calls,
        grid,
        apply_smoothing=apply_smoothing,
    )


def test_bl_raw_path_available_for_toggle() -> None:
    forward, vol, T = 100_000.0, 0.5, 0.25
    strikes = [85_000.0 + i * 3_000.0 for i in range(9)]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    grid = _price_grid(80_000.0, 115_000.0)
    raw = market_implied_density_breeden_litzenberger(
        strikes, calls, grid, apply_smoothing=False
    )
    smoothed = market_implied_density_breeden_litzenberger(strikes, calls, grid)
    assert raw != smoothed or max(raw) == 0.0
    assert abs(_integrate_density_trapezoid(grid, raw) - 1.0) < 0.05


def test_bl_density_from_calls_matches_unsmoothed_pipeline() -> None:
    forward, vol, T = 100_000.0, 0.45, 0.2
    strikes = [90_000.0, 100_000.0, 110_000.0, 120_000.0, 130_000.0]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    grid = _price_grid(85_000.0, 135_000.0, n=40)
    from src.engine.implied_distribution import _normalize_density

    expected = _normalize_density(grid, _bl_density_from_calls(strikes, calls, grid))
    actual = market_implied_density_breeden_litzenberger(
        strikes, calls, grid, apply_smoothing=False
    )
    assert len(expected) == len(actual)
    assert all(abs(a - b) < 1e-12 for a, b in zip(actual, expected, strict=True))


def _lab_state(*, bl_smoothing: bool | None = None) -> dict:
    state = {
        "mode": "exact_strikes",
        "qty": 1,
        "strikes_exact": {"k1": 90_000.0, "k2": 95_000.0, "k3": 105_000.0, "k4": 110_000.0},
        "legs_enabled": {"use_k1": True, "use_k2": True, "use_k3": True, "use_k4": True},
        "polarity": {"long_k1": False, "long_k2": True, "long_k3": True, "long_k4": False},
        "user_belief": {"enabled": False},
    }
    if bl_smoothing is not None:
        state["bl_density_smoothing_enabled"] = bl_smoothing
    return state


def _lab_market_data(forward: float = 100_000.0) -> dict:
    vol, T = 0.5, 0.25
    dist = build_distribution_chart_data(
        forward=forward,
        vol_annual=vol,
        T_years=T,
        price_min=forward * 0.75,
        price_max=forward * 1.35,
        num_points=41,
    )
    strikes = [85_000.0 + i * 5_000.0 for i in range(9)]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    call_marks = [
        {"strike": k, "mark_btc": c / forward}
        for k, c in zip(strikes, calls, strict=True)
    ]
    return {
        "forward": forward,
        "vol": vol,
        "T_years": T,
        "dist": dist,
        "put_by_k": {90_000.0: 0.01, 95_000.0: 0.02},
        "call_by_k": {105_000.0: 0.02, 110_000.0: 0.01},
        "call_marks": call_marks,
        "data_sources": ["test"],
        "as_of_utc": "2026-06-29T00:00:00Z",
    }


def test_derive_lab_outputs_chart_uses_smoothed_bl_by_default() -> None:
    outputs = derive_lab_outputs(_lab_state(), _lab_market_data())
    helpers = outputs["chart_helpers"]
    assert helpers.get("bl_density_smoothing_applied") is True
    pdf = helpers.get("market_pdf_raw") or []
    assert pdf and max(pdf) > 0.0
    prices = _lab_market_data()["dist"]["prices"]
    assert abs(_integrate_density_trapezoid(prices, pdf) - 1.0) < 0.08


def test_derive_lab_outputs_raw_toggle_differs_from_smoothed() -> None:
    market = _lab_market_data()
    smooth = derive_lab_outputs(_lab_state(bl_smoothing=True), market)
    raw = derive_lab_outputs(_lab_state(bl_smoothing=False), market)
    smooth_pdf = smooth["chart_helpers"]["market_pdf_raw"]
    raw_pdf = raw["chart_helpers"]["market_pdf_raw"]
    assert smooth_pdf != raw_pdf
    assert raw["chart_helpers"]["bl_density_smoothing_applied"] is False


def test_trust_strip_labels_bl_smoothing_mode() -> None:
    outputs = derive_lab_outputs(_lab_state(), _lab_market_data())
    lines = build_trust_strip_lines(outputs["verification"])
    joined = "\n".join(lines)
    assert "Savitzky–Golay smoothed" in joined
    mi = outputs["verification"]["density"]["market_implied"]
    assert mi.get("bl_density_smoothing") == "applied"


def test_export_bl_row_reflects_smoothed_density() -> None:
    exp_ts = 1893456000000
    forward, vol, T = 100_000.0, 0.5, 0.25
    strikes = [85_000.0 + i * 5_000.0 for i in range(9)]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": forward, "atm_iv": vol}

    def _marks(_exp: int) -> dict:
        return {
            "calls": [
                {"strike": k, "mark_btc": c / forward}
                for k, c in zip(strikes, calls, strict=True)
            ],
        }

    rows = build_distribution_export_rows(
        as_of_utc="2026-06-29T00:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
        asset_id="BTC",
    )
    bl_row = next(r for r in rows if r["distribution"] == "market_implied_bl")
    assert bl_row["bl_status"] == "computed:smoothed"
    assert float(bl_row["mean_usd"]) > 0.0
