from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, wait
from typing import Callable

import pandas as pd


def resolve_btc_spot_usd(
    *,
    get_deribit_index_usd: Callable[[], float | None],
    get_yahoo_prices_df: Callable[[], pd.DataFrame | None],
    deribit_timeout_s: float = 3.0,
) -> float | None:
    """
    Resolve a BTC spot reference for UI anchoring.

    Preference order:
    - Deribit index (bounded wait so the UI can mount even if Deribit hangs)
    - Yahoo close (BTC-USD) from the provided DataFrame

    Notes:
    - This function is Streamlit-free. Callers inject cached fetch callables.
    """
    current_btc = None
    try:
        with ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(get_deribit_index_usd)
            done, _ = wait([fut], timeout=float(deribit_timeout_s))
            if done:
                current_btc = fut.result()
    except Exception:
        current_btc = None

    if current_btc is not None:
        try:
            return float(current_btc)
        except Exception:
            pass

    try:
        df = get_yahoo_prices_df()
        if df is None or getattr(df, "empty", True):
            return None
        spot_rows = df[df["symbol"] == "BTC-USD"]
        if not len(spot_rows):
            return None
        spot_rows = spot_rows.sort_values("timestamp")
        for col in ("close", "Close"):
            if col in spot_rows.columns:
                return float(spot_rows[col].iloc[-1])
    except Exception:
        return None

    return None

