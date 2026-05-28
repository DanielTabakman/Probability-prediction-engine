"""Resolve PPE slice worker mode (acp vs deterministic vs local agent)."""

from __future__ import annotations

import os
from typing import Any

VALID_WORKER_MODES = frozenset({"acp", "deterministic", "local-agent"})


def _env_mode() -> str:
    raw = (os.environ.get("PPE_WORKER_MODE") or "").strip().lower()
    if raw in ("deterministic", "deterministic-worker", "local"):
        return "deterministic"
    if raw in ("acp", "cursor-acp"):
        return "acp"
    if raw in ("local-agent", "agent-cli", "agent"):
        return "local-agent"
    if os.environ.get("PPE_SKIP_ACP", "").strip().lower() in ("1", "true", "yes", "on"):
        return "deterministic"
    return ""


def infer_slice_kind(slice_id: str, slice_obj: dict[str, Any] | None) -> str:
    sid = slice_id.upper()
    if slice_obj and slice_obj.get("closeout"):
        return "closeout"
    if "CLOSEOUT" in sid or sid.endswith("-CLOSEOUT"):
        return "closeout"
    if "SMOKE" in sid or "WITNESS" in sid:
        return "smoke"
    if "CONTROL" in sid or "CHARTER" in sid:
        return "control"
    if "PRODUCT" in sid:
        return "product"
    return "evidence"


def resolve_worker_mode(
    *,
    slice_id: str,
    slice_obj: dict[str, Any] | None = None,
) -> str:
    """Return acp | deterministic | local-agent."""
    env = _env_mode()
    if env:
        return env

    if slice_obj:
        plan_mode = str(slice_obj.get("workerMode") or slice_obj.get("worker") or "").strip().lower()
        if plan_mode in ("deterministic", "local"):
            return "deterministic"
        if plan_mode in ("acp", "cursor-acp"):
            return "acp"
        if plan_mode in ("local-agent", "agent-cli", "agent"):
            return "local-agent"

    kind = infer_slice_kind(slice_id, slice_obj)
    if kind in ("closeout", "smoke", "control"):
        if os.environ.get("PPE_AUTO_DETERMINISTIC", "1").strip().lower() not in ("0", "false", "no"):
            return "deterministic"
    return "acp"


def resolve_declared_plane(slice_obj: dict[str, Any] | None, fallback: str) -> str:
    if not slice_obj:
        return fallback or "EVIDENCE-PLANE"
    plane = str(slice_obj.get("declaredPlane") or fallback or "EVIDENCE-PLANE").strip()
    if plane == "CONTROL-PLANE":
        return "EVIDENCE-PLANE"
    if plane in ("PRODUCT-PLANE", "EVIDENCE-PLANE"):
        return plane
    return "EVIDENCE-PLANE"
