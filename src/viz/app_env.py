"""Environment flags and repo root for the Streamlit app entry."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Project root (repo root when running `streamlit run src/viz/app.py`).
APP_ROOT = Path(__file__).resolve().parents[2]

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))


def env_flag(name: str, default: bool) -> bool:
    raw = (os.environ.get(name) or "").strip().lower()
    if raw == "":
        return default
    return raw in ("1", "true", "yes", "y", "on")
