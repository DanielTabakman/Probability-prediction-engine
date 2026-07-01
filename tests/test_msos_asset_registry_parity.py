"""MSOS pickers must track registry enabled assets — no module-specific allowlists."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.data.assets_registry import list_enabled_asset_ids
from src.viz.embed_display_boundary import build_asset_catalog_response, validate_asset_catalog_payload

MSOS_WEB = Path(__file__).resolve().parents[1] / "apps" / "msos-web"


def test_catalog_json_matches_registry_enabled_ids() -> None:
    catalog = build_asset_catalog_response()
    ok, err = validate_asset_catalog_payload(catalog)
    assert ok is True, err

    catalog_ids: list[str] = []
    for group in catalog["groups"]:
        for asset in group["assets"]:
            catalog_ids.append(str(asset["id"]).upper())

    assert sorted(catalog_ids) == sorted(list_enabled_asset_ids())
    assert catalog["default_asset_id"] in catalog_ids


def test_exposure_menu_uses_catalog_not_hardcoded_allowlist() -> None:
    client = (MSOS_WEB / "src" / "components" / "ExposureMenuClient.tsx").read_text(encoding="utf-8")
    page = (MSOS_WEB / "src" / "app" / "exposure" / "page.tsx").read_text(encoding="utf-8")
    lib = (MSOS_WEB / "src" / "lib" / "ppeExposureMenu.ts").read_text(encoding="utf-8")

    assert "LabAssetPicker" in client
    assert "fetchAssetCatalogServer" in page
    assert "normalizeCatalogAssetId" in lib or "normalizeExposureAssetId" in lib
    assert "EXPOSURE_PROOF_ASSETS" not in lib
    assert "EXPOSURE_PROOF_ASSETS" not in client


def test_msos_modules_do_not_declare_module_asset_allowlists() -> None:
    """Guard against reintroducing per-module proof/allowlist constants."""
    forbidden_patterns = (
        "EXPOSURE_PROOF_ASSETS",
        "proof_assets:",
    )
    scan_roots = (
        MSOS_WEB / "src" / "lib",
        MSOS_WEB / "src" / "components",
        MSOS_WEB / "src" / "app",
    )
    hits: list[str] = []
    for root in scan_roots:
        for path in root.rglob("*"):
            if path.suffix not in (".ts", ".tsx"):
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                if pattern in text:
                    hits.append(f"{path.relative_to(MSOS_WEB)}: {pattern}")
    assert hits == [], f"module allowlists found: {hits}"


@pytest.mark.parametrize("asset_id", ["SOL", "SPY", "QQQ", "IWM", "ETH"])
def test_enabled_asset_has_exposure_asset_class_binding(asset_id: str) -> None:
    from scripts.exposure_path_core import load_exposure_path_catalog, resolve_path_ids_for_asset
    from src.data.assets_registry import asset_class

    cat = load_exposure_path_catalog()
    bindings = cat.get("asset_bindings") or {}
    key = asset_class(asset_id)
    assert key in bindings, f"{asset_id} asset_class {key!r} missing from exposure catalog bindings"
    long_paths = resolve_path_ids_for_asset(asset_id, "long", cat)
    assert len(long_paths) >= 2, f"{asset_id} should activate multiple long exposure paths"
