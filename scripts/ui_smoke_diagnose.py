"""
Diagnose UI smoke failures and relay STOP_FOR_REVIEW caused by smoke/env mismatch.

Used by run_implied_lab_ui_smoke.py, write_last_run_report.py, and ppe_run.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class SmokeDiagnosis:
    category: str
    summary: str
    likely_cause: str
    suggested_fix: str
    auto_retry_command: str | None = None
    confidence: str = "medium"  # low | medium | high

    def as_dict(self) -> dict[str, str | None]:
        return {
            "category": self.category,
            "summary": self.summary,
            "likely_cause": self.likely_cause,
            "suggested_fix": self.suggested_fix,
            "auto_retry_command": self.auto_retry_command,
            "confidence": self.confidence,
        }


def _match(text: str, *patterns: str) -> bool:
    blob = (text or "").lower()
    return any(p.lower() in blob for p in patterns)


def diagnose_smoke_text(*, notes: str = "", detail: str = "", scenario: str = "") -> SmokeDiagnosis | None:
    """Classify a smoke failure from manifest notes/detail strings."""
    blob = f"{notes}\n{detail}\nscenario={scenario}"

    if _match(blob, "mode & solver", "could not find expander header: mode"):
        return SmokeDiagnosis(
            category="mvp1_scenario_mismatch",
            summary="Primary smoke ran scenario A but default MVP1 UI hides Mode & solver.",
            likely_cause=(
                "run_implied_lab_ui_smoke.py used A_width_target_payoff without "
                "PPE_POST_MVP1_LAB_UI=1, or an older harness called _set_mode directly."
            ),
            suggested_fix=(
                "Use primary_smoke_scenario() (MVP1_compact_verification on default UI) or set "
                "PPE_POST_MVP1_LAB_UI=1 for scenario A. Re-run: python scripts/run_implied_lab_ui_smoke.py"
            ),
            auto_retry_command="python scripts/run_implied_lab_ui_smoke.py",
            confidence="high",
        )

    if _match(blob, "belief peak", "where you think price lands", "help for where you think"):
        return SmokeDiagnosis(
            category="belief_peak_label_drift",
            summary="Harness could not set the belief peak number input.",
            likely_cause="Streamlit label drift or help-button aria-label collision.",
            suggested_fix=(
                "Ensure scripts/implied_lab_ui_smoke_harness.py uses BELIEF_PEAK_LABEL_REGEX and "
                "targets input[type='number'], not the help button."
            ),
            auto_retry_command="python scripts/run_implied_lab_ui_smoke.py",
            confidence="high",
        )

    if _match(blob, "σ_ln (advanced)", "sigma_ln", "could not select σ_ln"):
        return SmokeDiagnosis(
            category="belief_uncertainty_mode",
            summary="Harness could not switch belief uncertainty to σ_ln (advanced).",
            likely_cause="Advanced uncertainty expander collapsed or radio not visible in compact UI.",
            suggested_fix=(
                "Harness should call _ensure_belief_uncertainty_sigma_mode inside the belief expander."
            ),
            auto_retry_command="python scripts/run_implied_lab_ui_smoke.py",
            confidence="medium",
        )

    if _match(blob, "need btc spot", "my belief vs market", "streamlit not ready", "timeout"):
        return SmokeDiagnosis(
            category="live_data_or_env",
            summary="Smoke failed waiting for live data or page readiness.",
            likely_cause="Deribit/Yahoo/network unavailable or slow host.",
            suggested_fix="Retry with clean port; classify as environment-sensitive if baseline reproduces.",
            auto_retry_command="python scripts/run_implied_lab_ui_smoke.py",
            confidence="medium",
        )

    return None


def diagnose_manifest(manifest: dict[str, Any]) -> SmokeDiagnosis | None:
    close = manifest.get("workflow_hardening_slice003_closeout") or {}
    detail = str(close.get("detail") or "")
    for row in manifest.get("scenarios") or []:
        if not isinstance(row, dict):
            continue
        notes = str(row.get("notes") or "")
        scenario = str(row.get("scenario") or "")
        hit = diagnose_smoke_text(notes=notes, detail=detail, scenario=scenario)
        if hit:
            return hit
    return diagnose_smoke_text(notes="", detail=detail)


def diagnose_manifest_path(path: Path) -> SmokeDiagnosis | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return diagnose_manifest(data)


def diagnose_relay_result(relay: dict[str, Any]) -> SmokeDiagnosis | None:
    tests = relay.get("tests") if isinstance(relay.get("tests"), dict) else {}
    if tests.get("ui_smoke_primary_status") not in ("FAIL", "INCONCLUSIVE"):
        return None
    notes = str(relay.get("notes") or "")
    if tests.get("validation_classification") == "environment-sensitive" and _match(
        notes, "mode expander", "scenario a", "mvp1 ui", "baseline reproduces"
    ):
        return diagnose_smoke_text(notes=notes, detail=notes)
    artifacts = relay.get("artifacts") if isinstance(relay.get("artifacts"), dict) else {}
    manifest_rel = str(artifacts.get("ui_smoke_manifest") or "").strip()
    if manifest_rel:
        hit = diagnose_smoke_text(notes=notes, detail=manifest_rel)
        if hit:
            return hit
    return diagnose_smoke_text(notes=notes)


def find_newest_smoke_manifest(repo_root: Path) -> Path | None:
    root = repo_root / "artifacts" / "ui_smoke"
    if not root.is_dir():
        return None
    candidates: list[Path] = []
    for run_dir in root.iterdir():
        if not run_dir.is_dir():
            continue
        p = run_dir / "ui_smoke_manifest.json"
        if p.is_file():
            candidates.append(p)
    wt = repo_root / "_worktrees" / "acp_orchestrator"
    if wt.is_dir():
        candidates.extend(wt.glob("*/artifacts/ui_smoke/*/ui_smoke_manifest.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def format_diagnosis(d: SmokeDiagnosis | None) -> str:
    if d is None:
        return ""
    lines = [
        f"Smoke diagnosis ({d.category}, confidence={d.confidence}): {d.summary}",
        f"Likely cause: {d.likely_cause}",
        f"Suggested fix: {d.suggested_fix}",
    ]
    if d.auto_retry_command:
        lines.append(f"Retry: {d.auto_retry_command}")
    return "\n".join(lines)


def find_newest_relay_result(repo_root: Path) -> dict[str, Any] | None:
    wt = repo_root / "_worktrees" / "acp_orchestrator"
    if not wt.is_dir():
        return None
    paths = list(wt.glob("*/artifacts/relay/runs/*/relay_result.json"))
    paths.extend(wt.glob("*\\artifacts\\relay\\runs\\*\\relay_result.json"))
    existing = [p for p in paths if p.is_file()]
    if not existing:
        return None
    newest = max(existing, key=lambda p: p.stat().st_mtime)
    try:
        data = json.loads(newest.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def diagnose_stop_for_review(
    *,
    repo_root: Path,
    exit_code: int,
    relay: dict[str, Any] | None = None,
) -> SmokeDiagnosis | None:
    if exit_code not in (20, 1):
        return None
    if relay is None:
        relay = find_newest_relay_result(repo_root)
    if relay:
        hit = diagnose_relay_result(relay)
        if hit:
            return hit
    manifest_path = find_newest_smoke_manifest(repo_root)
    if manifest_path:
        return diagnose_manifest_path(manifest_path)
    return None
