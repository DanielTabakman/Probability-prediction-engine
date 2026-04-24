from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.probability_engine.services.implied_lab_inputs import build_implied_lab_market_data


@dataclass(frozen=True)
class ImpliedLabFetchBundle:
    expiries: list[dict[str, Any]]
    expiry_fetch_diag: Any
    market_data_for_selected_expiry: dict[str, Any] | None


def fetch_implied_lab_bundle(
    *,
    spot_usd: float,
    max_expiries: int,
    selected_expiry_str: str | None,
    cached_option_expiries: Callable[[int], tuple[list[dict[str, Any]], Any]],
    cached_forward_iv: Callable[[float, float], dict[str, Any] | None],
    cached_marks_full: Callable[[float], dict[str, Any] | None],
    quote_cache_ttl_s: int,
) -> ImpliedLabFetchBundle:
    """
    Orchestrate implied-lab inputs: expiries + (optionally) market_data for one expiry.

    This service is Streamlit-free: callers inject any caching wrappers.
    """
    expiries, expiry_fetch_diag = cached_option_expiries(int(max_expiries))

    market_data = None
    if expiries and selected_expiry_str:
        selected = next(
            (e for e in expiries if e.get("expiry_date_str") == selected_expiry_str),
            None,
        )
        if selected and selected.get("expiry_ts") is not None:
            market_data = build_implied_lab_market_data(
                expiry_ts_ms=float(selected["expiry_ts"]),
                spot_usd=float(spot_usd),
                cached_forward_iv=cached_forward_iv,
                cached_marks_full=cached_marks_full,
                quote_cache_ttl_s=int(quote_cache_ttl_s),
            )

    return ImpliedLabFetchBundle(
        expiries=list(expiries or []),
        expiry_fetch_diag=expiry_fetch_diag,
        market_data_for_selected_expiry=market_data,
    )

