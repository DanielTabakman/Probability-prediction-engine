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


LAYER_PRESET_INDEX: dict[str, str] = {
    "PPE_UI": "docs/SOP/agent_index/ppe-ui.md",
    "PPE_CORE": "docs/SOP/agent_index/ppe-core.md",
    "MSOS_UI": "docs/SOP/agent_index/msos-shell.md",
    "MSOS_PROXY": "docs/SOP/agent_index/msos-shell.md",
    "CONTROL": "docs/SOP/agent_index/dev-factory.md",
    "PLATFORM": "docs/SOP/REPO_LAYER_MAP_V1.md",
    "DOCS_CANON": "docs/SOP/REPO_LAYER_MAP_V1.md",
    "DOCS_ONLY": "docs/SOP/agent_index/dev-factory.md",
}


def slice_touch_set(slice_obj: dict[str, Any]) -> list[str]:
    raw = slice_obj.get("touchSet") or slice_obj.get("touch_set")
    if not isinstance(raw, list):
        return []
    return [str(p).strip() for p in raw if str(p).strip()]


def slice_declared_plane(slice_obj: dict[str, Any]) -> str:
    return str(slice_obj.get("declaredPlane") or "").strip().upper()


def is_product_plane_slice(slice_obj: dict[str, Any]) -> bool:
    return slice_declared_plane(slice_obj) == "PRODUCT-PLANE"


def layer_index_path(layer_preset: str | None) -> str | None:
    if not layer_preset:
        return None
    return LAYER_PRESET_INDEX.get(str(layer_preset).strip())


def _validate_acceptance_entries(slice_id: str, acceptance: Any) -> list[str]:
    errors: list[str] = []
    if acceptance is None:
        return errors
    if not isinstance(acceptance, list):
        return [f"{slice_id}: acceptance must be an array"]
    for j, item in enumerate(acceptance):
        if not isinstance(item, dict):
            errors.append(f"{slice_id}: acceptance[{j}] must be an object")
            continue
        if not str(item.get("id") or "").strip():
            errors.append(f"{slice_id}: acceptance[{j}] missing id")
        if not str(item.get("check") or "").strip():
            errors.append(f"{slice_id}: acceptance[{j}] missing check")
    return errors


def validate_phase_plan(plan: dict[str, Any], *, strict_agent_schema: bool = False) -> list[str]:
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
        sid = str(sl.get("sliceId") or "").strip()
        if not sid:
            errors.append(f"slice[{i}]: missing sliceId")
            continue
        if "closeout" in sl:
            has_closeout = True
        if strict_agent_schema and is_product_plane_slice(sl) and not slice_touch_set(sl):
            errors.append(f"{sid}: PRODUCT-PLANE slice missing non-empty touchSet")
        if "acceptance" in sl:
            errors.extend(_validate_acceptance_entries(sid, sl.get("acceptance")))
    if not has_closeout:
        errors.append("phase plan: no slice with 'closeout' block (chapter closeout required)")
    return errors


def format_acceptance_checklist(acceptance: list[dict[str, Any]]) -> str:
    lines = ["| ID | Check | Verify |", "|----|-------|--------|"]
    for item in acceptance:
        aid = str(item.get("id") or "").strip()
        check = str(item.get("check") or "").strip()
        verify = str(item.get("verify") or "").strip() or "—"
        lines.append(f"| `{aid}` | {check} | `{verify}` |")
    return "\n".join(lines)


def recommended_loads_for_slice(
    repo_root: Path,
    *,
    slice_obj: dict[str, Any],
    slice_id: str,
    phase_plan: str,
    layer_preset: str | None,
) -> list[str]:
    loads: list[str] = [
        "docs/SOP/AGENT_CONTINUITY_BRIEF.md",
        f"artifacts/orchestrator/IDE_BUILD_STARTER_{slice_id.replace('/', '_').replace(chr(92), '_')}.md",
        "docs/SOP/AI_HUMAN_DIVISION_V1.md",
    ]
    idx = layer_index_path(layer_preset)
    if idx:
        loads.append(idx)
    norm_plan = phase_plan.replace("\\", "/").strip()
    if norm_plan:
        loads.append(norm_plan)
    for path in slice_touch_set(slice_obj):
        if path not in loads:
            loads.append(path)
    for item in slice_obj.get("acceptance") or []:
        if not isinstance(item, dict):
            continue
        verify = str(item.get("verify") or "").strip()
        if verify.startswith("tests/") and verify not in loads:
            test_path = verify.split("::", 1)[0]
            loads.append(test_path)
    return loads


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
                strict = status in ("READY", "RUNNING")
                errors.extend(validate_phase_plan(plan, strict_agent_schema=strict))

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
