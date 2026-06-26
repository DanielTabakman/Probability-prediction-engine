"""Tests for Cloudflare staging DNS helper."""

from __future__ import annotations

import scripts.cloudflare_ensure_staging_dns as cf


def test_ensure_staging_cname_noop_when_match() -> None:
    calls: list[tuple[str, str, dict | None]] = []

    def fake_api(method: str, path: str, *, token: str, body: dict | None = None) -> dict:
        calls.append((method, path, body))
        if method == "GET" and "dns_records" in path:
            return {
                "success": True,
                "result": [
                    {
                        "id": "rec1",
                        "name": "staging.marketstructureos.com",
                        "content": "marketstructureos.com",
                        "proxied": True,
                    }
                ],
            }
        return {"success": True, "result": []}

    original = cf._api_request
    cf._api_request = fake_api
    try:
        msg = cf.ensure_staging_cname(
            token="tok",
            zone_id="zone",
            staging_label="staging",
            apex_host="marketstructureos.com",
        )
    finally:
        cf._api_request = original
    assert "unchanged" in msg
    assert calls[0][0] == "GET"
