"""Repo layer map — machine-readable presets stay valid."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.repo_layer_paths import (
    audit_paths,
    infer_layer_preset,
    resolve_slice_layer_scope,
    scope_from_preset,
    load_presets,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PRESETS_PATH = REPO_ROOT / "docs" / "SOP" / "REPO_LAYER_PATH_PREFIXES.json"
CANON_DOC = REPO_ROOT / "docs" / "SOP" / "REPO_LAYER_MAP_V1.md"


def _load_presets() -> dict:
    return json.loads(PRESETS_PATH.read_text(encoding="utf-8"))


def test_repo_layer_canon_doc_exists() -> None:
    assert CANON_DOC.is_file()


def test_repo_layer_presets_json_schema() -> None:
    data = _load_presets()
    assert data["version"] == 1
    assert "layers" in data
    assert "presets" in data
    assert "import_rules" in data

    expected_layers = {
        "msos-shell",
        "ppe-ui",
        "ppe-core",
        "dev-factory",
        "platform",
        "product-canon",
    }
    assert set(data["layers"]) == expected_layers

    for layer_id, layer in data["layers"].items():
        assert "primary_paths" in layer
        assert layer["primary_paths"]

    expected_presets = {
        "MSOS_UI",
        "PPE_UI",
        "PPE_CORE",
        "CONTROL",
        "PLATFORM",
        "DOCS_CANON",
        "DOCS_ONLY",
        "MSOS_PROXY",
    }
    assert set(data["presets"]) == expected_presets

    for preset_id, preset in data["presets"].items():
        assert "allowed_paths" in preset
        assert "forbidden_paths" in preset
        assert preset["allowed_paths"]
        if preset.get("layer") is not None:
            assert preset["layer"] in data["layers"]


def test_repo_layer_primary_paths_exist_or_reserved() -> None:
    """Primary paths must exist except msos-web (chartered, README-only until P2)."""
    data = _load_presets()
    for layer in data["layers"].values():
        for rel in layer["primary_paths"]:
            path = REPO_ROOT / rel.rstrip("/")
            if rel.startswith("apps/msos-web"):
                assert path.is_dir(), f"reserved dir missing: {rel}"
                continue
            assert path.exists(), f"missing primary path for layer: {rel}"


def test_ppe_ui_preset_allows_viz_blocks_engine() -> None:
    presets = load_presets(REPO_ROOT)
    scope = scope_from_preset(presets, "PPE_UI")
    assert not audit_paths(["src/viz/app_panels.py"], scope)
    assert audit_paths(["src/engine/implied_distribution.py"], scope)


def test_infer_msos_control_slice() -> None:
    assert infer_layer_preset("MSOS-P1-Control-Slice001", "EVIDENCE-PLANE") == "CONTROL"


def test_resolve_slice_layer_preset_from_plan_field() -> None:
    scope = resolve_slice_layer_scope(
        REPO_ROOT,
        slice_obj={"layerPreset": "DOCS_CANON", "touchSet": ["docs/SOP/MSOS_P1_STACK_ROUTING_ADR.md"]},
        slice_id="MSOS-P1-Product-Slice002",
        declared_plane="CONTROL-PLANE",
    )
    assert scope.layer_preset == "DOCS_CANON"
    assert not audit_paths(["docs/SOP/MSOS_P1_STACK_ROUTING_ADR.md"], scope)
    assert audit_paths(["src/viz/app.py"], scope)
