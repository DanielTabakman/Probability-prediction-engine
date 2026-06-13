"""Central autobuilder dispatch — loop, watch, phone, and CLI share one entry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

VERDICT_IDE_BUILD = "IDE_BUILD"


def _auto_dispatch_enabled(repo: Path) -> bool:
    try:
        from scripts.ppe_ide_handoff import ide_handoff_enabled
        from scripts.ppe_operator_config import auto_remote_build_enabled

        return auto_remote_build_enabled(repo) or ide_handoff_enabled(repo)
    except ImportError:
        return True


def should_dispatch_loop(repo: Path, status: dict[str, Any]) -> bool:
    if str(status.get("verdict") or "") != VERDICT_IDE_BUILD:
        return False
    if not _auto_dispatch_enabled(repo):
        return False
    try:
        from scripts.ppe_remote_build_agent import read_build_lock

        return read_build_lock(repo) is None
    except ImportError:
        return True


def should_dispatch_watch(
    repo: Path,
    status: dict[str, Any],
    prior: dict[str, Any],
    *,
    retry: bool = False,
) -> bool:
    if not _auto_dispatch_enabled(repo):
        return False
    if str(status.get("verdict") or "") != VERDICT_IDE_BUILD:
        return False
    try:
        from scripts.ppe_remote_build_agent import read_build_lock, resolve_build_target
        from scripts.ppe_watch_operator_mobile import _auto_build_retry_due
    except ImportError:
        return False

    target = resolve_build_target(repo)
    if not target.get("ok") or target.get("mode") != "ide_build":
        return False
    slice_id = str(target.get("slice_id") or "")
    if not slice_id or read_build_lock(repo):
        return False

    prior_verdict_slice = str(prior.get("last_verdict_slice") or "")
    last_auto = prior.get("last_auto_build") or {}
    if not retry:
        if (
            str(prior.get("last_verdict") or "") == VERDICT_IDE_BUILD
            and prior_verdict_slice == slice_id
            and last_auto.get("started")
            and str(last_auto.get("slice_id") or prior.get("last_auto_build_slice") or "") == slice_id
        ):
            return False
    elif not _auto_build_retry_due(prior, VERDICT_IDE_BUILD):
        return False
    elif prior_verdict_slice and prior_verdict_slice != slice_id:
        return False
    return True


def dispatch_build(
    repo: Path,
    *,
    source: str,
    note: str = "",
    force_handoff: bool = False,
) -> dict[str, Any]:
    """Try headless CLI when allowed; otherwise IDE handoff."""
    from scripts.ppe_ide_handoff import respond_to_ide_build

    return respond_to_ide_build(
        repo.resolve(),
        source=source,
        note=note,
        force_handoff=force_handoff,
    )


def maybe_dispatch_loop(repo: Path, status: dict[str, Any]) -> dict[str, Any] | None:
    if not should_dispatch_loop(repo, status):
        return None
    return dispatch_build(
        repo,
        source="loop-guard",
        note="auto-triggered by operator loop on IDE_BUILD guard stop",
    )


def maybe_dispatch_watch(
    repo: Path,
    status: dict[str, Any],
    prior: dict[str, Any],
    *,
    retry: bool = False,
) -> dict[str, Any] | None:
    if not should_dispatch_watch(repo, status, prior, retry=retry):
        return None
    note = "auto-triggered by mobile watch on IDE_BUILD"
    if retry:
        note = "auto-retry by mobile watch (IDE_BUILD still stuck)"
    return dispatch_build(
        repo,
        source="auto-watch",
        note=note,
        force_handoff=retry and bool(prior.get("last_auto_build")),
    )
