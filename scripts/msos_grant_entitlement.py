#!/usr/bin/env python3
"""Grant or update MSOS entitlement tier (operator CLI)."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_TIERS = ("free", "research_beta", "paid")
VALID_SUBSCRIPTION_STATUSES = ("none", "active", "past_due", "canceled")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _default_db_path(repo_root: Path) -> Path:
    return repo_root / "data" / "msos_workflow" / "msos_entitlements.sqlite3"


def _normalize_email(raw: str) -> str:
    email = raw.strip().lower()
    if not email or "@" not in email:
        raise SystemExit(f"invalid email: {raw!r}")
    return email


def grant_entitlement(
    db_path: Path,
    *,
    email: str,
    tier: str,
    granted_by: str,
    notes: str | None = None,
    subscription_status: str = "none",
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS msos_entitlements (
              owner_email TEXT PRIMARY KEY NOT NULL,
              tier TEXT NOT NULL,
              granted_at_utc TEXT NOT NULL,
              granted_by TEXT NOT NULL,
              notes TEXT,
              stripe_customer_id TEXT,
              stripe_subscription_id TEXT,
              subscription_status TEXT NOT NULL DEFAULT 'none'
            )
            """
        )
        now = _utc_now()
        existing = conn.execute(
            "SELECT owner_email FROM msos_entitlements WHERE owner_email = ?",
            (email,),
        ).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE msos_entitlements
                SET tier = ?, granted_at_utc = ?, granted_by = ?, notes = ?,
                    subscription_status = ?
                WHERE owner_email = ?
                """,
                (tier, now, granted_by, notes, subscription_status, email),
            )
        else:
            conn.execute(
                """
                INSERT INTO msos_entitlements
                (owner_email, tier, granted_at_utc, granted_by, notes, subscription_status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (email, tier, now, granted_by, notes, subscription_status),
            )
        conn.commit()
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grant MSOS entitlement tier for an owner email.")
    parser.add_argument("--email", required=True, help="Owner email (Cloudflare Access identity)")
    parser.add_argument(
        "--tier",
        required=True,
        choices=VALID_TIERS,
        help="Entitlement tier to grant",
    )
    parser.add_argument(
        "--granted-by",
        default="operator",
        help="Audit label (default: operator)",
    )
    parser.add_argument("--notes", default="", help="Optional operator notes")
    parser.add_argument(
        "--subscription-status",
        default="none",
        choices=VALID_SUBSCRIPTION_STATUSES,
        help="Subscription status column (default: none)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        help="Override entitlements SQLite path (default: data/msos_workflow/...)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    db_path = args.db_path or _default_db_path(repo_root)
    email = _normalize_email(args.email)
    notes = args.notes.strip() or None

    grant_entitlement(
        db_path,
        email=email,
        tier=args.tier,
        granted_by=args.granted_by,
        notes=notes,
        subscription_status=args.subscription_status,
    )
    print(f"granted tier={args.tier} email={email} db={db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
