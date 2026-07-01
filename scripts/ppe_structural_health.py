"""Structural repo health metrics and warn thresholds (advisory)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

Severity = Literal["info", "watch", "escalate"]

APP_PY_MAX_LINES = 300
SCRIPTS_PY_MAX_COUNT = 250
UNTRACKED_NON_ARTIFACT_MAX = 5
HOUSEKEEPING_OVERDUE_CHAPTERS = 3

APP_PY_REL = "src/viz/app.py"
SCRIPTS_GLOB = "scripts/*.py"
STATE_REL = "artifacts/control_plane/BETWEEN_CHAPTER_HOUSEKEEPING_STATE.json"


def _count_lines(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for _ in path.read_text(encoding="utf-8", errors="replace").splitlines())


def load_housekeeping_state(repo: Path) -> dict[str, Any]:
    path = repo / STATE_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def collect_structural_metrics(
    repo: Path,
    *,
    untracked_non_artifact: int | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    app_py = repo / APP_PY_REL
    scripts = list(repo.glob(SCRIPTS_GLOB))
    state = load_housekeeping_state(repo)
    metrics: dict[str, Any] = {
        "app_py_lines": _count_lines(app_py),
        "app_py_max_lines": APP_PY_MAX_LINES,
        "scripts_py_count": len(scripts),
        "scripts_py_max_count": SCRIPTS_PY_MAX_COUNT,
        "untracked_non_artifact_max": UNTRACKED_NON_ARTIFACT_MAX,
        "housekeeping_overdue_chapters": HOUSEKEEPING_OVERDUE_CHAPTERS,
        "product_chapters_since_housekeeping": int(state.get("product_chapters_since_run") or 0),
        "last_housekeeping_scheduled_at": state.get("last_scheduled_at"),
        "last_product_closeout_chapter": state.get("last_product_closeout_chapter"),
    }
    if untracked_non_artifact is not None:
        metrics["untracked_non_artifact"] = untracked_non_artifact
    return metrics


def evaluate_structural_warnings(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []

    app_lines = int(metrics.get("app_py_lines") or 0)
    if app_lines > APP_PY_MAX_LINES:
        warnings.append(
            {
                "id": "app-py-monolith",
                "severity": "watch",
                "message": f"src/viz/app.py is {app_lines} lines (warn > {APP_PY_MAX_LINES})",
                "metric": "app_py_lines",
                "value": app_lines,
                "threshold": APP_PY_MAX_LINES,
            }
        )

    script_count = int(metrics.get("scripts_py_count") or 0)
    if script_count > SCRIPTS_PY_MAX_COUNT:
        warnings.append(
            {
                "id": "scripts-sprawl",
                "severity": "info",
                "message": f"scripts/*.py count is {script_count} (warn > {SCRIPTS_PY_MAX_COUNT})",
                "metric": "scripts_py_count",
                "value": script_count,
                "threshold": SCRIPTS_PY_MAX_COUNT,
            }
        )

    untracked = metrics.get("untracked_non_artifact")
    if untracked is not None and int(untracked) > UNTRACKED_NON_ARTIFACT_MAX:
        warnings.append(
            {
                "id": "untracked-drift",
                "severity": "watch",
                "message": f"{untracked} untracked non-artifact path(s) (warn > {UNTRACKED_NON_ARTIFACT_MAX})",
                "metric": "untracked_non_artifact",
                "value": int(untracked),
                "threshold": UNTRACKED_NON_ARTIFACT_MAX,
            }
        )

    since_hk = int(metrics.get("product_chapters_since_housekeeping") or 0)
    if since_hk >= HOUSEKEEPING_OVERDUE_CHAPTERS:
        warnings.append(
            {
                "id": "housekeeping-overdue",
                "severity": "watch",
                "message": (
                    f"{since_hk} product chapter(s) since between-chapter housekeeping "
                    f"(warn >= {HOUSEKEEPING_OVERDUE_CHAPTERS})"
                ),
                "metric": "product_chapters_since_housekeeping",
                "value": since_hk,
                "threshold": HOUSEKEEPING_OVERDUE_CHAPTERS,
            }
        )

    return warnings


def structural_health_block(
    repo: Path,
    *,
    untracked_non_artifact: int | None = None,
) -> dict[str, Any]:
    metrics = collect_structural_metrics(repo, untracked_non_artifact=untracked_non_artifact)
    warnings = evaluate_structural_warnings(metrics)
    return {
        "metrics": metrics,
        "warnings": warnings,
        "ok": not any(w.get("severity") == "escalate" for w in warnings),
    }
