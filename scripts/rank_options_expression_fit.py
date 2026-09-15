"""CLI helper for deterministic options expression fit ranking."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.viz.options_expression_fit_ranking_boundary import build_options_expression_fit_ranking_response


def build_query(args: argparse.Namespace) -> str:
    pairs: list[tuple[str, Any]] = [
        ("asset", args.asset),
        ("direction", args.direction),
        ("horizon", args.horizon),
        ("payoff_preference", args.payoff_preference),
    ]
    if args.expiry:
        pairs.append(("expiry", args.expiry))
    if args.target_horizon_days is not None:
        pairs.append(("target_horizon_days", args.target_horizon_days))
    if args.max_loss_usd is not None:
        pairs.append(("max_loss_usd", args.max_loss_usd))
    if args.forward_mult is not None:
        pairs.append(("forward_mult", args.forward_mult))
    if args.vol_mult is not None:
        pairs.append(("vol_mult", args.vol_mult))
    if args.offline:
        pairs.append(("offline", "1"))
    return "&".join(f"{key}={value}" for key, value in pairs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset", default="NVDA")
    parser.add_argument("--direction", choices=["long", "short", "neutral"], default="long")
    parser.add_argument("--horizon", choices=["any", "3m", "12m"], default="any")
    parser.add_argument("--target-horizon-days", type=int)
    parser.add_argument("--max-loss-usd", type=float)
    parser.add_argument(
        "--payoff-preference",
        choices=["defined_risk", "capital_light", "upside_leverage", "income_style", "watch_only"],
        default="defined_risk",
    )
    parser.add_argument("--expiry")
    parser.add_argument("--forward-mult", type=float)
    parser.add_argument("--vol-mult", type=float)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)
    payload = build_options_expression_fit_ranking_response({"QUERY_STRING": build_query(args)})
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
