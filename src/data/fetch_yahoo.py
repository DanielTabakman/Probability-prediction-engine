"""
Fetch gold, silver, and Bitcoin prices from Yahoo Finance.
"""
from __future__ import annotations

import pandas as pd
import yfinance as yf

DEFAULT_SYMBOLS = {
    "gold": ["GC=F", "GLD"],
    "silver": ["SI=F", "SLV"],
    "bitcoin": ["BTC-USD"],
}


def fetch_yahoo_prices(
    symbols: dict[str, list[str]] | None = None,
    period: str = "5d",
) -> pd.DataFrame:
    """
    Fetch OHLCV for configured symbols. Returns a long-format DataFrame
    with columns: symbol, asset, open, high, low, close, volume, timestamp.
    """
    symbols = symbols or DEFAULT_SYMBOLS
    all_tickers = []
    asset_map = {}
    for asset, syms in symbols.items():
        for s in syms:
            all_tickers.append(s)
            asset_map[s] = asset

    if not all_tickers:
        return pd.DataFrame()

    data = yf.download(
        all_tickers,
        period=period,
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True,
    )

    out = []
    # Single ticker: yfinance >=1.x often returns a MultiIndex (Ticker, Field) even for one symbol
    # when group_by="ticker"; extract the ticker level so Open/Close renames apply.
    if len(all_tickers) == 1:
        t = all_tickers[0]
        if isinstance(data.columns, pd.MultiIndex) and t in data.columns.get_level_values(0):
            df = data[t].copy()
        else:
            df = data.copy()
        df = df.reset_index()
        df.columns = [c if c != "Date" else "date" for c in df.columns]
        df["symbol"] = t
        df["asset"] = asset_map[t]
        renames = {"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
        df = df.rename(columns={k: v for k, v in renames.items() if k in df.columns})
        out.append(df)
    else:
        for ticker in all_tickers:
            try:
                block = data[ticker].copy()
                if block is None or block.empty:
                    continue
                block = block.reset_index()
                block.columns = [c if c != "Date" else "date" for c in block.columns]
                block["symbol"] = ticker
                block["asset"] = asset_map[ticker]
                renames = {"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
                block = block.rename(columns={k: v for k, v in renames.items() if k in block.columns})
                out.append(block)
            except Exception:
                continue

    if not out:
        return pd.DataFrame()

    result = pd.concat(out, ignore_index=True)
    result["timestamp"] = pd.to_datetime(result.get("date", result.index))
    return result
