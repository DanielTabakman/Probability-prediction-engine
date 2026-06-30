"""Mid-month credit burn policy — Option A default, Option B boost when credits underused.

Operator records Cursor/agent usage monthly; after day 16 (configurable), if usage
is below threshold, autoRemoteBuild turns on for the rest of the month.

Canon: docs/SOP/HUMAN_STEWARD_BACKLOG.json (product lane automation decision)
Config: docs/SOP/PPE_AUTO_OPERATOR.local.json → remoteBuildPolicy
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

BUDGET_REL = "artifacts/control_plane/CREDIT_BUDGET.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def budget_path(repo: Path) -> Path:
    return repo.resolve() / BUDGET_REL


def load_credit_budget(repo: Path) -> dict[str, Any] | None:
    p = budget_path(repo)
    if not p.is_file():
        return None
    try:
        raw = json.loads(p.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return None
    return raw if isinstance(raw, dict) else None


def save_credit_budget(repo: Path, payload: dict[str, Any]) -> Path:
    p = budget_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return p


def _policy(cfg: dict[str, Any]) -> dict[str, Any]:
    raw = cfg.get("remoteBuildPolicy")
    return raw if isinstance(raw, dict) else {}


def _month_key(when: date | None = None) -> str:
    d = when or date.today()
    return f"{d.year:04d}-{d.month:02d}"


def record_usage(
    repo: Path,
    *,
    used_pct: float,
    notes: str = "",
    when: date | None = None,
) -> Path:
    if not 0.0 <= used_pct <= 1.0:
        raise SystemExit("used_pct must be between 0 and 1 (e.g. 0.15 for 15%)")
    payload: dict[str, Any] = {
        "month": _month_key(when),
        "used_pct": round(used_pct, 4),
        "updated_at_utc": _utc_now(),
    }
    if notes.strip():
        payload["notes"] = notes.strip()
    return save_credit_budget(repo, payload)


def resolve_auto_remote_build(
    cfg: dict[str, Any],
    *,
    budget: dict[str, Any] | None = None,
    when: date | None = None,
) -> tuple[bool, str]:
    """Return (enabled, reason) for effective autoRemoteBuild."""
    today = when or date.today()
    base_on = cfg.get("autoRemoteBuild", False) is not False
    policy = _policy(cfg)
    if not policy.get("midMonthBurnBoost", True):
        return base_on, "base config (midMonthBurnBoost off)"

    after_day = int(policy.get("enableAfterDay", 16))
    if today.day < after_day:
        return base_on, f"before day {after_day} — manual IDE BUILD (Option A)"

    threshold = float(policy.get("underuseThresholdPct", 0.35))
    if budget is None:
        return base_on, f"on/after day {after_day} but no CREDIT_BUDGET — staying on base config"

    if str(budget.get("month") or "") != _month_key(today):
        return base_on, f"on/after day {after_day} but budget month stale — staying on base config"

    used = budget.get("used_pct")
    if used is None:
        return base_on, f"on/after day {after_day} but used_pct missing — staying on base config"

    try:
        used_f = float(used)
    except (TypeError, ValueError):
        return base_on, "invalid used_pct in CREDIT_BUDGET"

    if used_f < threshold:
        pct = int(round(used_f * 100))
        lim = int(round(threshold * 100))
        return True, f"mid-month burn boost: {pct}% used < {lim}% threshold (Option B until month end)"

    pct = int(round(used_f * 100))
    return base_on, f"credits {pct}% used — no boost (stay Option A)"


def status_lines(repo: Path) -> list[str]:
    from scripts.ppe_operator_config import load_operator_config

    cfg = load_operator_config(repo)
    budget = load_credit_budget(repo)
    enabled, reason = resolve_auto_remote_build(cfg, budget=budget)
    policy = _policy(cfg)
    lines = [
        "Remote BUILD policy",
        f"- effective autoRemoteBuild: {'ON' if enabled else 'OFF'}",
        f"- reason: {reason}",
    ]
    if budget:
        lines.append(
            f"- CREDIT_BUDGET: month={budget.get('month')} used={budget.get('used_pct')} "
            f"updated={budget.get('updated_at_utc', '?')}"
        )
    else:
        lines.append("- CREDIT_BUDGET: (not set — record with ppe_remote_build_policy.cmd record --used-pct 0.15)")
    lines.append(
        f"- midMonthBurnBoost after day {policy.get('enableAfterDay', 16)} "
        f"when used < {int(float(policy.get('underuseThresholdPct', 0.35)) * 100)}%"
    )
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mid-month credit burn → autoRemoteBuild boost")
    ap.add_argument("--repo-root", type=Path, default=_REPO)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Print effective autoRemoteBuild policy")

    rec = sub.add_parser("record", help="Record monthly credit usage (0–1 fraction)")
    rec.add_argument("--used-pct", type=float, required=True, help="Fraction used, e.g. 0.15 for 15%")
    rec.add_argument("--notes", default="", help="Optional note (plan name, dashboard date)")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.cmd == "status":
        for line in status_lines(repo):
            print(line)
        return 0

    if args.cmd == "record":
        out = record_usage(repo, used_pct=args.used_pct, notes=args.notes)
        print(f"ppe_remote_build_policy: wrote {out.relative_to(repo)}")
        for line in status_lines(repo):
            print(line)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
