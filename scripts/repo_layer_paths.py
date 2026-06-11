"""Repo layer map — presets, inference, and path audits (see docs/SOP/REPO_LAYER_MAP_V1.md)."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PRESETS_REL = "docs/SOP/REPO_LAYER_PATH_PREFIXES.json"


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def presets_path(repo_root: Path) -> Path:
    return repo_root.resolve() / PRESETS_REL


def load_presets(repo_root: Path) -> dict[str, Any]:
    p = presets_path(repo_root)
    if not p.is_file():
        raise FileNotFoundError(f"Missing {PRESETS_REL}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


@dataclass(frozen=True)
class LayerScope:
    layer: str | None
    layer_preset: str | None
    allowed_paths: tuple[str, ...]
    forbidden_paths: tuple[str, ...]
    touch_set: tuple[str, ...]

    def to_envelope_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "layer_preset": self.layer_preset,
            "allowed_paths": list(self.allowed_paths),
            "forbidden_paths": list(self.forbidden_paths),
            "touch_set": list(self.touch_set),
        }

    @classmethod
    def from_envelope(cls, data: dict[str, Any] | None) -> LayerScope | None:
        if not isinstance(data, dict):
            return None
        return cls(
            layer=data.get("layer"),
            layer_preset=data.get("layer_preset"),
            allowed_paths=tuple(_norm(p) for p in (data.get("allowed_paths") or []) if p),
            forbidden_paths=tuple(_norm(p) for p in (data.get("forbidden_paths") or []) if p),
            touch_set=tuple(_norm(p) for p in (data.get("touch_set") or []) if p),
        )


def preset_by_name(presets_doc: dict[str, Any], name: str) -> dict[str, Any]:
    presets = presets_doc.get("presets") or {}
    if name not in presets:
        raise KeyError(f"unknown layer preset {name!r}")
    return presets[name]


def scope_from_preset(presets_doc: dict[str, Any], preset_name: str, *, touch_set: list[str] | None = None) -> LayerScope:
    preset = preset_by_name(presets_doc, preset_name)
    return LayerScope(
        layer=preset.get("layer"),
        layer_preset=preset_name,
        allowed_paths=tuple(_norm(p) for p in preset.get("allowed_paths") or []),
        forbidden_paths=tuple(_norm(p) for p in preset.get("forbidden_paths") or []),
        touch_set=tuple(_norm(p) for p in (touch_set or [])),
    )


def infer_layer_preset(slice_id: str, declared_plane: str) -> str:
    sid = slice_id.upper()
    plane = declared_plane.upper()

    if "MSOS" in sid:
        if "PROXY" in sid:
            return "MSOS_PROXY"
        if plane == "PRODUCT-PLANE" and "PRODUCT" in sid:
            return "MSOS_UI"
        if "WITNESS" in sid or "CLOSEOUT" in sid or "CONTROL" in sid:
            return "CONTROL"
        return "DOCS_CANON"

    if "CLOSEOUT" in sid or "CONTROL" in sid or "WITNESS" in sid or "RECONCILE" in sid:
        return "CONTROL"

    if plane == "PRODUCT-PLANE" and "PRODUCT" in sid:
        return "PPE_UI"

    if plane == "EVIDENCE-PLANE":
        return "CONTROL"

    return "CONTROL"


def resolve_slice_layer_scope(
    repo_root: Path,
    *,
    slice_obj: dict[str, Any] | None,
    slice_id: str,
    declared_plane: str,
) -> LayerScope:
    presets_doc = load_presets(repo_root)
    touch = []
    if slice_obj:
        raw_touch = slice_obj.get("touchSet") or slice_obj.get("touch_set")
        if isinstance(raw_touch, list):
            touch = [_norm(str(p)) for p in raw_touch if str(p).strip()]

    if slice_obj and slice_obj.get("layerPreset"):
        scope = scope_from_preset(presets_doc, str(slice_obj["layerPreset"]), touch_set=touch)
    elif slice_obj and (slice_obj.get("allowedPaths") or slice_obj.get("allowed_paths")):
        allowed = slice_obj.get("allowedPaths") or slice_obj.get("allowed_paths") or []
        forbidden = slice_obj.get("forbiddenPaths") or slice_obj.get("forbidden_paths") or []
        scope = LayerScope(
            layer=str(slice_obj.get("layer") or ""),
            layer_preset=str(slice_obj.get("layerPreset") or "") or None,
            allowed_paths=tuple(_norm(p) for p in allowed if p),
            forbidden_paths=tuple(_norm(p) for p in forbidden if p),
            touch_set=tuple(touch),
        )
    else:
        preset_name = infer_layer_preset(slice_id, declared_plane)
        scope = scope_from_preset(presets_doc, preset_name, touch_set=touch)

    # touchSet entries are explicit allows (narrowing hints for stewards).
    if touch and scope.touch_set:
        return scope
    if touch:
        return LayerScope(
            layer=scope.layer,
            layer_preset=scope.layer_preset,
            allowed_paths=scope.allowed_paths,
            forbidden_paths=scope.forbidden_paths,
            touch_set=tuple(touch),
        )
    return scope


def _path_matches_prefix(path: str, prefix: str) -> bool:
    p = _norm(path)
    pref = _norm(prefix)
    if not pref:
        return False
    if pref.endswith("/"):
        return p.startswith(pref) or p == pref.rstrip("/")
    if p == pref or p.startswith(pref + "/"):
        return True
    # Prefix entries like tests/test_msos_web_ match tests/test_msos_web_strategy_lab.py
    return len(p) > len(pref) and p.startswith(pref)


def path_allowed(path: str, scope: LayerScope) -> bool:
    p = _norm(path)
    if scope.touch_set and p in scope.touch_set:
        return True
    for forbidden in scope.forbidden_paths:
        if _path_matches_prefix(p, forbidden):
            return False
    if not scope.allowed_paths:
        return True
    return any(_path_matches_prefix(p, allowed) for allowed in scope.allowed_paths)


def audit_paths(paths: list[str], scope: LayerScope) -> list[str]:
    """Return violation messages (empty if ok)."""
    violations: list[str] = []
    seen: set[str] = set()
    for raw in paths:
        p = _norm(raw)
        if not p or p in seen:
            continue
        seen.add(p)
        if not path_allowed(p, scope):
            violations.append(
                f"path {p!r} outside layer scope "
                f"(preset={scope.layer_preset!r}, layer={scope.layer!r})"
            )
    return violations


def git_changed_paths(
    repo_root: Path,
    *,
    base_ref: str,
    head_ref: str = "HEAD",
) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        proc2 = subprocess.run(
            ["git", "diff", "--name-only", base_ref, head_ref],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc2.returncode != 0:
            return []
        out = proc2.stdout
    else:
        out = proc.stdout
    return [_norm(line) for line in out.splitlines() if line.strip()]


def git_dirty_paths(repo_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        path = _norm(line[3:].strip())
        if path and not path.startswith("_worktrees/"):
            paths.append(path)
    return paths


def audit_git_diff(
    repo_root: Path,
    scope: LayerScope,
    *,
    base_ref: str,
    head_ref: str = "HEAD",
) -> list[str]:
    return audit_paths(git_changed_paths(repo_root, base_ref=base_ref, head_ref=head_ref), scope)


def audit_git_dirty(repo_root: Path, scope: LayerScope) -> list[str]:
    return audit_paths(git_dirty_paths(repo_root), scope)


def find_slice_in_plan(plan: dict[str, Any], slice_id: str) -> dict[str, Any] | None:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and str(sl.get("sliceId") or "") == slice_id:
            return sl
    return None


def scope_for_active_manifest(repo_root: Path) -> LayerScope | None:
    """Best-effort scope from manifest + active orchestrator slice or first plan slice."""
    try:
        from scripts.ppe_manifest import load_manifest, load_phase_plan
    except ImportError:
        return None

    try:
        manifest = load_manifest(repo_root)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    plan_rel = str(manifest.get("phasePlanPath") or "").strip()
    if not plan_rel:
        return None

    try:
        plan = load_phase_plan(repo_root, plan_rel)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    slice_id = ""
    active_path = repo_root / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    if active_path.is_file():
        try:
            active = json.loads(active_path.read_text(encoding="utf-8-sig"))
            if isinstance(active, dict):
                slice_id = str(active.get("slice_id") or active.get("sliceId") or "")
        except json.JSONDecodeError:
            pass

    slice_obj: dict[str, Any] | None = None
    declared_plane = "EVIDENCE-PLANE"
    if slice_id:
        slice_obj = find_slice_in_plan(plan, slice_id)
        if slice_obj:
            declared_plane = str(slice_obj.get("declaredPlane") or "EVIDENCE-PLANE")
    else:
        for sl in plan.get("slices") or []:
            if not isinstance(sl, dict):
                continue
            slice_id = str(sl.get("sliceId") or sl.get("slice_id") or "")
            if not slice_id:
                continue
            slice_obj = sl
            declared_plane = str(sl.get("declaredPlane") or "EVIDENCE-PLANE")
            break

    if not slice_id:
        return None

    return resolve_slice_layer_scope(
        repo_root,
        slice_obj=slice_obj,
        slice_id=slice_id,
        declared_plane=declared_plane,
    )


def format_build_packet_layer_block(scope: LayerScope) -> str:
    lines = [
        f"LAYER: {scope.layer or '(see preset)'}",
        f"LAYER_PRESET: {scope.layer_preset or ''}",
        "ALLOWED_PATHS:",
    ]
    for p in scope.allowed_paths:
        lines.append(f"  - {p}")
    if scope.touch_set:
        lines.append("TOUCH_SET (explicit allows):")
        for p in scope.touch_set:
            lines.append(f"  - {p}")
    lines.append("FORBIDDEN_PATHS:")
    for p in scope.forbidden_paths:
        lines.append(f"  - {p}")
    return "\n".join(lines)
