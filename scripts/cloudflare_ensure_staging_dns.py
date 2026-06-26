#!/usr/bin/env python3
"""Ensure staging.marketstructureos.com DNS exists (Cloudflare API).

Creates a proxied CNAME staging -> apex so the same VPS/Caddy stack serves staging
without needing the origin IPv4.

Requires env:
  CLOUDFLARE_API_TOKEN — API token with Zone.DNS Edit
  CLOUDFLARE_ZONE_ID   — zone id for marketstructureos.com

Usage:
  python scripts/cloudflare_ensure_staging_dns.py
  python scripts/cloudflare_ensure_staging_dns.py --zone marketstructureos.com --staging staging
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_ZONE = "marketstructureos.com"
DEFAULT_STAGING = "staging"
DEFAULT_APEX = "marketstructureos.com"


def _api_request(
    method: str,
    path: str,
    *,
    token: str,
    body: dict | None = None,
) -> dict:
    url = f"https://api.cloudflare.com/client/v4{path}"
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"Cloudflare API {method} {path} failed: HTTP {exc.code} {detail}") from exc
    if not payload.get("success"):
        raise RuntimeError(f"Cloudflare API error: {payload.get('errors')}")
    return payload


def resolve_zone_id(token: str, zone_name: str) -> str:
    explicit = os.environ.get("CLOUDFLARE_ZONE_ID", "").strip()
    if explicit:
        return explicit
    payload = _api_request("GET", f"/zones?name={zone_name}", token=token)
    results = payload.get("result") or []
    if not results:
        raise RuntimeError(f"zone not found: {zone_name}")
    return str(results[0]["id"])


def ensure_staging_cname(
    *,
    token: str,
    zone_id: str,
    staging_label: str,
    apex_host: str,
) -> str:
    fqdn = f"{staging_label}.{apex_host.removeprefix('*.')}"
    if apex_host.startswith("*."):
        apex_host = apex_host[2:]
    target = apex_host if "." in apex_host else f"{apex_host}"

    list_path = f"/zones/{zone_id}/dns_records?type=CNAME&name={fqdn}"
    existing = _api_request("GET", list_path, token=token).get("result") or []
    for row in existing:
        if str(row.get("name", "")).lower() == fqdn.lower():
            content = str(row.get("content", ""))
            proxied = bool(row.get("proxied"))
            if content.rstrip(".") == target.rstrip(".") and proxied:
                return f"OK: CNAME {fqdn} -> {content} (proxied, unchanged)"
            record_id = row["id"]
            _api_request(
                "PATCH",
                f"/zones/{zone_id}/dns_records/{record_id}",
                token=token,
                body={
                    "type": "CNAME",
                    "name": staging_label,
                    "content": target,
                    "proxied": True,
                },
            )
            return f"OK: updated CNAME {fqdn} -> {target} (proxied)"

    _api_request(
        "POST",
        f"/zones/{zone_id}/dns_records",
        token=token,
        body={
            "type": "CNAME",
            "name": staging_label,
            "content": target,
            "proxied": True,
        },
    )
    return f"OK: created CNAME {fqdn} -> {target} (proxied)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ensure Cloudflare staging DNS CNAME")
    parser.add_argument("--zone", default=DEFAULT_ZONE)
    parser.add_argument("--staging", default=DEFAULT_STAGING)
    parser.add_argument("--apex", default=DEFAULT_APEX, help="CNAME target (apex hostname)")
    args = parser.parse_args(argv)

    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not token:
        print("CLOUDFLARE_API_TOKEN not set — skip DNS automation", file=sys.stderr)
        return 2

    zone_id = resolve_zone_id(token, args.zone)
    message = ensure_staging_cname(
        token=token,
        zone_id=zone_id,
        staging_label=args.staging,
        apex_host=args.apex,
    )
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
