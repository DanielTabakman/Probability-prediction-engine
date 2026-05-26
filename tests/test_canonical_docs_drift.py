"""Relay canonical doc paths stay aligned with JOB_REGISTRY precedence (MVP1)."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.relay.canonical_docs import CANONICAL_DOC_PATHS

REPO_ROOT = Path(__file__).resolve().parents[1]
JOB_REGISTRY = REPO_ROOT / "docs" / "SOP" / "JOB_REGISTRY_V1.md"


def _numbered_paths_from_registry(text: str) -> list[str]:
    paths: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^\d+\.\s+`([^`]+)`", line)
        if m and m.group(1).startswith("docs/"):
            paths.append(m.group(1))
    return paths


def test_canonical_doc_paths_exist_on_disk() -> None:
    missing = [p for p in CANONICAL_DOC_PATHS if not (REPO_ROOT / p).is_file()]
    assert not missing, f"Missing canonical docs: {missing}"


def test_mvp1_frontier_is_first_canonical_path() -> None:
    assert CANONICAL_DOC_PATHS[0] == "docs/SOP/MVP1_FRONTIER.md"


def test_registry_precedence_matches_relay_canonical_docs() -> None:
    """JOB_REGISTRY SOP precedence (items 2–8) matches relay preflight prefix."""
    text = JOB_REGISTRY.read_text(encoding="utf-8")
    registry_paths = _numbered_paths_from_registry(text)
    registry_sop = [p for p in registry_paths if p.startswith("docs/SOP/")]
    assert tuple(registry_sop) == CANONICAL_DOC_PATHS[: len(registry_sop)]
    assert CANONICAL_DOC_PATHS[-1] == "docs/SOP/RELAY_RUNTIME_V0.md"


def test_legacy_frontier_not_required_for_relay() -> None:
    assert "docs/SOP/CURRENT_FRONTIER.md" not in CANONICAL_DOC_PATHS
