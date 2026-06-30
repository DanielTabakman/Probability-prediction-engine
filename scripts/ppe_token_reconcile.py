"""Monthly Cursor billing reconcile vs advisory slice-cost ledger."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BILLING_MANUAL_REL = "artifacts/control_plane/cursor_billing_manual.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def billing_manual_path(repo: Path) -> Path:
    return repo / BILLING_MANUAL_REL


def load_manual_entries(repo: Path) -> list[dict[str, Any]]:
    path = billing_manual_path(repo)
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        entries = data.get("entries")
        if isinstance(entries, list):
            return [row for row in entries if isinstance(row, dict)]
    return []


def save_manual_entries(repo: Path, entries: list[dict[str, Any]]) -> Path:
    path = billing_manual_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "updated_at_utc": _utc_now(), "entries": entries}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def record_manual_month(repo: Path, *, month: str, cursor_usd: float, notes: str = "") -> dict[str, Any]:
    month_key = month.strip()[:7]
    entries = load_manual_entries(repo)
    row = {
        "month": month_key,
        "cursor_usd": round(float(cursor_usd), 2),
        "notes": notes.strip(),
        "recorded_at_utc": _utc_now(),
    }
    entries = [e for e in entries if str(e.get("month") or "")[:7] != month_key]
    entries.append(row)
    entries.sort(key=lambda e: str(e.get("month") or ""))
    save_manual_entries(repo, entries)
    return row


def latest_manual_entry(repo: Path) -> dict[str, Any] | None:
    entries = load_manual_entries(repo)
    if not entries:
        return None
    return max(entries, key=lambda e: str(e.get("month") or ""))


def reconcile(repo: Path, *, days: int = 30) -> dict[str, Any]:
    from scripts.ppe_workflow_cost import summarize_by_lane

    lane = summarize_by_lane(repo, days=days)
    est_usd = float(lane.get("est_usd_total") or 0.0)
    manual = latest_manual_entry(repo)
    cursor_usd = float(manual.get("cursor_usd") or 0.0) if manual else None
    delta: float | None = None
    ratio: float | None = None
    if cursor_usd is not None and cursor_usd > 0:
        delta = round(cursor_usd - est_usd, 2)
        ratio = round(cursor_usd / est_usd, 2) if est_usd > 0 else None
    return {
        "days": days,
        "est_usd": round(est_usd, 2),
        "cursor_usd": cursor_usd,
        "manual_month": str(manual.get("month") or "")[:7] if manual else None,
        "delta": delta,
        "ratio": ratio,
    }


def billing_recommendation(repo: Path, *, days: int = 30) -> str | None:
    data = reconcile(repo, days=days)
    cursor_usd = data.get("cursor_usd")
    if cursor_usd is None:
        return (
            "BILLING: no manual Cursor USD recorded — run ppe_token_reconcile.cmd record "
            "--month YYYY-MM --usd N."
        )
    delta = data.get("delta")
    ratio = data.get("ratio")
    if delta is not None and delta > 50:
        return (
            f"BILLING: manual Cursor ${cursor_usd:.0f} exceeds advisory ledger by ${delta:.0f} "
            "— review slice-cost assumptions."
        )
    if ratio is not None and ratio > 1.5:
        return f"BILLING: Cursor/reconcile ratio {ratio:.2f} — run ppe_token_reconcile.cmd summary."
    return None


def digest_reconcile_line(repo: Path, *, days: int = 30) -> str | None:
    data = reconcile(repo, days=days)
    cursor_usd = data.get("cursor_usd")
    if cursor_usd is None:
        return None
    est_usd = float(data.get("est_usd") or 0.0)
    delta = data.get("delta")
    delta_s = f" delta=${delta:+.0f}" if delta is not None else ""
    return (
        f"- Cursor billing reconcile: ledger~${est_usd:.0f} vs manual ${cursor_usd:.0f}"
        f"{delta_s} (ppe_token_reconcile.cmd)."
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Reconcile Cursor billing vs advisory workflow cost ledger.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)

    p_rec = sub.add_parser("record", help="Record manual Cursor dashboard USD for a month")
    p_rec.add_argument("--month", required=True, help="YYYY-MM")
    p_rec.add_argument("--usd", type=float, required=True)
    p_rec.add_argument("--notes", default="")

    p_sum = sub.add_parser("summary")
    p_sum.add_argument("--days", type=int, default=30)

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.command == "record":
        row = record_manual_month(repo, month=args.month, cursor_usd=args.usd, notes=args.notes)
        print(f"ppe_token_reconcile: recorded {row['month']} cursor_usd={row['cursor_usd']}")
        return 0

    data = reconcile(repo, days=args.days)
    print(json.dumps(data, indent=2))
    rec = billing_recommendation(repo, days=args.days)
    if rec:
        print(f"ppe_token_reconcile: {rec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
