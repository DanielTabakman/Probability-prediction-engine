"""Cross-venue research summary display boundary for MSOS Strategy Lab."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CROSS_VENUE_RESEARCH_KIND = "cross_venue_research_boundary"
CROSS_VENUE_RESEARCH_HTTP_PATH = "/ppe-display-api/cross-venue-research.json"
CROSS_VENUE_RESEARCH_HTTP_PATH_ALT = "/cross-venue-research.json"


def _repo_root() -> Path:
    raw = os.environ.get("PPE_REPO_ROOT") or os.environ.get("PPE_ROOT") or "."
    return Path(raw).resolve()


def build_cross_venue_research_response() -> dict[str, Any]:
    repo = _repo_root()
    summary_path = repo / "artifacts/control_plane/RESEARCH_SUMMARY.json"
    if summary_path.is_file():
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return {
                    "kind": CROSS_VENUE_RESEARCH_KIND,
                    "schema_version": 1,
                    "source": "research_summary_json",
                    **payload,
                }
        except (json.JSONDecodeError, OSError):
            pass
    from src.viz.research_summary import build_research_summary

    payload = build_research_summary(repo)
    return {
        "kind": CROSS_VENUE_RESEARCH_KIND,
        "schema_version": 1,
        "source": "live_build",
        **payload,
    }


def handle_cross_venue_research_wsgi_path(path: str, environ: dict[str, Any]) -> tuple[str, bytes] | None:
    normalized = path.rstrip("/") or "/"
    if normalized not in (CROSS_VENUE_RESEARCH_HTTP_PATH, CROSS_VENUE_RESEARCH_HTTP_PATH_ALT):
        return None
    try:
        payload = build_cross_venue_research_response()
    except Exception as exc:  # noqa: BLE001
        payload = {"kind": "cross_venue_research_error", "error": str(exc)}
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    status = "200 OK" if payload.get("kind") == CROSS_VENUE_RESEARCH_KIND else "503 Service Unavailable"
    return status, body
