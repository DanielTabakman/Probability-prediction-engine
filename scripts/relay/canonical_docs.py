"""Canonical SOP paths for relay preflight and control-plane consistency checks.

MVP1 steering uses ``MVP1_FRONTIER.md``; legacy ``CURRENT_FRONTIER.md`` is
historical only and is not required for relay preflight.
"""

from __future__ import annotations

# RELAY_RUNTIME_V0 section 0 / CODEX_AUTONOMY_V1 precedence (MVP1, 2026-05-19).
CANONICAL_DOC_PATHS: tuple[str, ...] = (
    "docs/SOP/MVP1_FRONTIER.md",
    "docs/SOP/PPE_INTEGRATED_STATUS.md",
    "docs/SOP/HANDOFF.md",
    "docs/SOP/OPERATING_RULES.md",
    "docs/SOP/FRONTIER_STEWARD_PROTOCOL.md",
    "docs/SOP/CODEX_AUTONOMY_V1.md",
    "docs/SOP/JOB_REGISTRY_V1.md",
    "docs/SOP/RELAY_RUNTIME_V0.md",
)

LEGACY_FRONTIER_DOC_PATH = "docs/SOP/CURRENT_FRONTIER.md"
