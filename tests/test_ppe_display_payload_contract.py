"""Python display-payload kinds must match MSOS web parse contract."""

from __future__ import annotations

from pathlib import Path

from scripts.msos_production_demo_witness import validate_display_api_response

REPO = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO / "apps" / "msos-web"


def test_python_display_kinds_referenced_in_ts() -> None:
    from src.viz.embed_display_boundary import DISPLAY_PAYLOAD_KIND

    payload_lib = (MSOS_WEB / "src" / "lib" / "ppeDisplayPayload.ts").read_text(encoding="utf-8")
    assert DISPLAY_PAYLOAD_KIND in payload_lib
    assert "isDisplayPayload" in payload_lib

    web_glob = list((MSOS_WEB / "src").rglob("*.ts"))
    web_text = "\n".join(p.read_text(encoding="utf-8") for p in web_glob)
    from src.viz.embed_display_boundary import BELIEF_OVERLAY_KIND, CATALOG_PAYLOAD_KIND

    assert BELIEF_OVERLAY_KIND in web_text or "belief_overlay" in web_text
    assert CATALOG_PAYLOAD_KIND in web_text or "asset_catalog" in web_text


def test_golden_display_payload_validates_like_production_witness() -> None:
    from src.viz.embed_display_boundary import DISPLAY_PAYLOAD_KIND

    golden = {
        "kind": DISPLAY_PAYLOAD_KIND,
        "spot_usd": 64000.0,
        "asset": {"id": "ETH", "label": "ETH options"},
        "series_by_expiry": [
            {"expiry_date": "2030-01-01", "prices_usd": [1.0, 2.0], "pdf_pct": [50.0, 50.0]}
        ],
    }
    import json

    body = json.dumps(golden)
    ok, err, data = validate_display_api_response(200, body, expected_asset_id="ETH")
    assert ok is True, err
    assert data is not None
    assert data["kind"] == DISPLAY_PAYLOAD_KIND
