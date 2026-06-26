"""Asset registry scaffold (config/assets.yaml) — no runtime wiring until Core-Slice002."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS_PATH = REPO_ROOT / "config" / "assets.yaml"


def load_assets_registry() -> dict:
    with ASSETS_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("assets registry root must be a mapping")
    return data


def test_assets_registry_schema() -> None:
    reg = load_assets_registry()
    assert reg.get("version") == 1
    default_id = reg.get("default_asset_id")
    assert default_id == "BTC"
    assets = reg.get("assets")
    assert isinstance(assets, dict)
    assert set(assets) >= {"BTC", "ETH"}
    for asset_id in ("BTC", "ETH"):
        entry = assets[asset_id]
        assert entry.get("venue") == "deribit"
        assert entry.get("deribit_currency") == asset_id
        assert entry.get("price_unit") == "USD"
        assert isinstance(entry.get("spread_width"), (int, float))
        assert entry.get("spread_width") > 0
        assert isinstance(entry.get("label"), str) and entry["label"]
