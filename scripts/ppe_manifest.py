"""Active phase manifest load/validate/update for run_ppe.cmd."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MANIFEST_REL = "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
VALID_STATUSES = frozenset({"READY", "RUNNING", "COMPLETE"})


def manifest_path(repo_root: Path) -> Path:
    return repo_root.resolve() / MANIFEST_REL


def load_manifest(repo_root: Path) -> dict[str, Any]:
    p = manifest_path(repo_root)
    if not p.is_file():
        raise FileNotFoundError(f"Missing manifest: {MANIFEST_REL}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save_manifest(repo_root: Path, data: dict[str, Any]) -> None:
    p = manifest_path(repo_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_phase_plan(repo_root: Path, rel_or_abs: str) -> dict[str, Any]:
    plan_path = Path(rel_or_abs)
    if not plan_path.is_absolute():
        plan_path = repo_root / plan_path
    return json.loads(plan_path.read_text(encoding="utf-8-sig"))


def validate_phase_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    slices = plan.get("slices")
    if not isinstance(slices, list) or not slices:
        errors.append("phase plan: missing non-empty 'slices' array")
        return errors
    has_closeout = False
    for i, sl in enumerate(slices):
        if not isinstance(sl, dict):
            errors.append(f"slice[{i}]: not an object")
            continue
        if not sl.get("sliceId"):
            errors.append(f"slice[{i}]: missing sliceId")
        if "closeout" in sl:
            has_closeout = True
    if not has_closeout:
        errors.append("phase plan: no slice with 'closeout' block (chapter closeout required)")
    return errors


def validate_manifest(repo_root: Path, manifest: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if manifest is None:
        try:
            manifest = load_manifest(repo_root)
        except FileNotFoundError as e:
            return [str(e)]
        except json.JSONDecodeError as e:
            return [f"manifest JSON invalid: {e}"]

    status = str(manifest.get("status") or "").strip()
    if status not in VALID_STATUSES:
        errors.append(f"manifest status must be one of {sorted(VALID_STATUSES)}; got {status!r}")

    plan_rel = str(manifest.get("phasePlanPath") or "").strip()
    if not plan_rel and status == "READY":
        errors.append("manifest phasePlanPath is empty; steward must set at SELECTION")
    elif plan_rel:
        plan_path = repo_root / plan_rel.replace("\\", "/")
        if not plan_path.is_file():
            errors.append(f"phase plan not found: {plan_rel}")
        else:
            try:
                plan = load_phase_plan(repo_root, plan_rel)
            except json.JSONDecodeError as e:
                errors.append(f"phase plan JSON invalid: {e}")
            else:
                errors.extend(validate_phase_plan(plan))

    for key in ("sprintSpecPath", "selectionRecord"):
        rel = str(manifest.get(key) or "").strip()
        if rel:
            p = repo_root / rel.replace("\\", "/")
            if not p.is_file():
                errors.append(f"manifest {key} not found: {rel}")

    return errors


def resolve_summary(repo_root: Path) -> dict[str, Any]:
    manifest = load_manifest(repo_root)
    plan_rel = str(manifest.get("phasePlanPath") or "").strip()
    summary: dict[str, Any] = {
        "manifest_path": MANIFEST_REL,
        "status": manifest.get("status"),
        "phase_plan_path": plan_rel or None,
        "selection_record": manifest.get("selectionRecord"),
        "sprint_spec_path": manifest.get("sprintSpecPath"),
        "notes": manifest.get("notes"),
        "slice_count": 0,
        "first_slice_id": None,
        "chapter_name": None,
        "errors": validate_manifest(repo_root, manifest),
    }
    if plan_rel and not summary["errors"]:
        plan = load_phase_plan(repo_root, plan_rel)
        slices = plan.get("slices") or []
        summary["slice_count"] = len(slices)
        if slices:
            summary["first_slice_id"] = slices[0].get("sliceId")
        summary["chapter_name"] = plan.get("name")
    return summary


def set_manifest_status(repo_root: Path, status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")
    manifest = load_manifest(repo_root)
    manifest["status"] = status
    save_manifest(repo_root, manifest)


def clear_manifest_plan_path(repo_root: Path, *, note: str = "") -> None:
    """Clear phasePlanPath while keeping status (typically COMPLETE)."""
    manifest = load_manifest(repo_root)
    manifest["phasePlanPath"] = ""
    if note:
        prev = str(manifest.get("notes") or "").strip()
        manifest["notes"] = f"{prev} {note}".strip() if prev else note
    save_manifest(repo_root, manifest)


def maybe_mark_manifest_complete(
    repo_root: Path,
    phase_plan_path: Path,
    slice_id: str,
) -> bool:
    """If slice_id is the phase closeout slice, set manifest status COMPLETE."""
    plan = load_phase_plan(repo_root, str(phase_plan_path))
    for sl in plan.get("slices") or []:
        if sl.get("sliceId") == slice_id and "closeout" in sl:
            manifest_path_p = manifest_path(repo_root)
            if not manifest_path_p.is_file():
                return False
            manifest = load_manifest(repo_root)
            plan_rel = str(manifest.get("phasePlanPath") or "").replace("\\", "/")
            if plan_rel:
                m_plan = (repo_root / plan_rel).resolve()
                if m_plan != phase_plan_path.resolve():
                    return False
            try:
                from scripts.ppe_phase_plan_window import non_closeout_slices_pending

                plan_rel_for_pending = str(phase_plan_path.resolve().relative_to(repo_root)).replace(
                    "\\", "/"
                )
                pending = non_closeout_slices_pending(repo_root, plan_rel_for_pending)
            except ValueError:
                pending = non_closeout_slices_pending(
                    repo_root, str(phase_plan_path).replace("\\", "/")
                )
            if pending:
                print(
                    f"maybe_mark_manifest_complete: skip closeout {slice_id} — "
                    f"non-closeout slices still pending: {pending}"
                )
                return False
            manifest["status"] = "COMPLETE"
            save_manifest(repo_root, manifest)
            return True
    return False
