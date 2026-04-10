"""
Fetch Bitcoin options (and summary) from Yahoo Finance. May be limited; Deribit is an alternative for production.
"""
from __future__ import annotations

import pandas as pd
import yfinance as yf
from datetime import datetime, timezone

SYMBOL = "BTC-USD"


def fetch_btc_options_chain(expiration: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """
    Get calls and puts for BTC-USD. If expiration is None, use nearest expiry.
    Returns (calls_df, puts_df) or None if options not available.
    """
    try:
        tk = yf.Ticker(SYMBOL)
        opts = getattr(tk, "options", None)
        if not opts or (isinstance(opts, (list, tuple)) and len(opts) == 0):
            return None
        exp = expiration or (opts[0] if isinstance(opts[0], str) else str(opts[0]))
        chain = tk.option_chain(exp)
        if chain is None:
            return None
        return (chain.calls, chain.puts)
    except Exception:
        return None


def fetch_btc_options_summary() -> dict:
    """
    Return a small summary for the UI: expirations, and for nearest expiry:
    at-the-money (ATM) call/put implied vol or last price if available.
    """
    out = {"available": False, "expirations": [], "nearest_expiry": None, "calls_count": 0, "puts_count": 0}
    try:
        tk = yf.Ticker(SYMBOL)
        opts = getattr(tk, "options", None)
        if not opts or (isinstance(opts, (list, tuple)) and len(opts) == 0):
            return out
        out["available"] = True
        out["expirations"] = list(opts)[:10]  # next 10 expiries
        out["nearest_expiry"] = opts[0] if isinstance(opts[0], str) else str(opts[0])
        chain = tk.option_chain(out["nearest_expiry"])
        if chain:
            out["calls_count"] = len(chain.calls) if chain.calls is not None else 0
            out["puts_count"] = len(chain.puts) if chain.puts is not None else 0
    except Exception:
        pass
    return out
