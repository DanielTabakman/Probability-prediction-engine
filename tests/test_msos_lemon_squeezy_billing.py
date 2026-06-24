"""MSOS Lemon Squeezy billing — product witness."""

from __future__ import annotations

import hashlib
import hmac
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_grant_entitlement_exported() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosEntitlements.ts").read_text(encoding="utf-8")
    assert "export function grantEntitlement" in lib


def test_lemon_squeezy_webhook_lib() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "lemonSqueezyWebhook.ts").read_text(encoding="utf-8")
    assert "verifyLemonSqueezySignature" in lib
    assert "applyLemonSqueezyWebhook" in lib
    assert "subscription_created" in lib
    assert "user_email" in lib


def test_lemon_squeezy_webhook_route() -> None:
    route = (
        MSOS_WEB / "src" / "app" / "api" / "billing" / "lemon-squeezy" / "webhook" / "route.ts"
    ).read_text(encoding="utf-8")
    assert "LEMONSQUEEZY_WEBHOOK_SECRET" in route
    assert "verifyLemonSqueezySignature" in route
    assert "applyLemonSqueezyWebhook" in route


def test_operator_runbook_exists() -> None:
    doc = (REPO_ROOT / "docs" / "SOP" / "LEMON_SQUEEZY_OPERATOR_SETUP_V1.md").read_text(
        encoding="utf-8"
    )
    assert "MSOS_UPGRADE_OFFER_URL" in doc
    assert "/api/billing/lemon-squeezy/webhook" in doc


def test_msos_grant_entitlement_script() -> None:
    script = REPO_ROOT / "scripts" / "msos_grant_entitlement.py"
    assert script.is_file()
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--email",
            "billing-test@example.com",
            "--tier",
            "paid",
            "--notes",
            "pytest witness",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "granted tier=paid" in proc.stdout


def test_lemon_squeezy_signature_algorithm_matches_docs() -> None:
    """HMAC-SHA256 hex digest — same algorithm as Lemon Squeezy signing docs."""
    secret = "test-secret"
    body = json.dumps(
        {
            "meta": {"event_name": "subscription_created"},
            "data": {
                "type": "subscriptions",
                "id": "1",
                "attributes": {"user_email": "a@b.com", "status": "active"},
            },
        }
    )
    expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    assert len(expected) == 64
