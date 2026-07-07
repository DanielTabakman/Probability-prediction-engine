"""Production witness: MSOS usage API accepts events (telemetry path live)."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE = "https://marketstructureos.com"
DEFAULT_OUT = Path("artifacts/health/msos_product_usage_telemetry_witness.json")
USER_AGENT = (
    "Mozilla/5.0 (compatible; ppe-msos-product-usage-witness/1; "
    "+https://marketstructureos.com)"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def probe_usage_api(base_url: str) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/api/usage/event"
    body = json.dumps(
        {
            "event_name": "witness_probe",
            "source": "production_witness",
            "path": "/api/usage/event",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Origin": base_url.rstrip("/"),
            "Referer": f"{base_url.rstrip('/')}/",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            payload = json.loads(raw) if raw.strip() else {}
            ok = resp.status == 200 and payload.get("ok") is True
            return {
                "ok": ok,
                "status": resp.status,
                "url": url,
                "response": payload,
            }
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        return {"ok": False, "status": exc.code, "url": url, "error": detail}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "url": url, "error": str(exc)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Witness MSOS product usage API on production.")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--write", type=Path, default=None)
    args = ap.parse_args(argv)
    result = probe_usage_api(args.base_url)
    report = {"generated_at_utc": _utc_now(), "base_url": args.base_url, "probe": result}
    out = args.write or DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"msos_product_usage_telemetry_witness: ok={result.get('ok')} wrote {out}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
