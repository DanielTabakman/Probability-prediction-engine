from __future__ import annotations

from typing import Any

from src.data.fetch_btc_options import fetch_btc_options_summary as _fetch_btc_options_summary


def get_btc_options_summary() -> Any:
    return _fetch_btc_options_summary()

