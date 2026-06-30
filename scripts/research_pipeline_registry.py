"""Load research pipeline collector/test registry (config/research_pipeline_registry.json)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPO / "config" / "research_pipeline_registry.json"


@lru_cache(maxsize=4)
def _load_registry_cached(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"registry must be object: {path}")
    return data


def load_registry(repo: Path | None = None) -> dict[str, Any]:
    path = (repo or REPO) / "config" / "research_pipeline_registry.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    return _load_registry_cached(str(path.resolve()))


def collectors(repo: Path | None = None) -> list[dict[str, Any]]:
    reg = load_registry(repo)
    items = reg.get("collectors") or []
    return [item for item in items if isinstance(item, dict)]


def tests(repo: Path | None = None) -> list[dict[str, Any]]:
    reg = load_registry(repo)
    items = reg.get("tests") or []
    return [item for item in items if isinstance(item, dict)]


def collector_by_id(collector_id: str, repo: Path | None = None) -> dict[str, Any] | None:
    for item in collectors(repo):
        if str(item.get("id") or "") == collector_id:
            return item
    return None
