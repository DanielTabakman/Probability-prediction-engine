#!/usr/bin/env python3
"""One-shot scheduled warm for ppe_display_api (cache ops meta infra).

Usage (cron / compose sidecar):
  python scripts/run_display_cache_refresh.py
  python scripts/run_display_cache_refresh.py --base-url http://127.0.0.1:8765
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.warm_display_payload_cache import main as warm_main  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    return warm_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
