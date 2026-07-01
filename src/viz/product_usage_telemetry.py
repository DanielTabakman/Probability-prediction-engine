"""Append-only product usage telemetry for Streamlit implied lab (Q-009b)."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRODUCT_USAGE_FILENAME = "ppe_product_usage.jsonl"


def _usage_dir() -> Path:
    raw = (os.environ.get("PPE_PRODUCT_USAGE_DIR") or os.environ.get("PPE_PRODUCT_USAGE_JSONL") or "").strip()
    if raw:
        p = Path(raw).expanduser()
        return p if p.is_dir() else p.parent
    return Path("data")


def _usage_path() -> Path:
    raw = (os.environ.get("PPE_PRODUCT_USAGE_JSONL") or "").strip()
    if raw and not Path(raw).is_dir():
        return Path(raw).expanduser()
    return _usage_dir() / PRODUCT_USAGE_FILENAME


def log_product_usage_event(
    event_name: str,
    *,
    source: str = "streamlit",
    path: str | None = None,
    asset_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Fire-and-forget append to shared product usage JSONL."""
    try:
        record: dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "event_name": event_name,
            "source": source,
        }
        if path:
            record["path"] = path
        if asset_id:
            record["asset_id"] = asset_id
        if extra:
            record.update(extra)
        out = _usage_path()
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, separators=(",", ":")) + "\n")
    except OSError:
        pass
