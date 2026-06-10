"""CLI for operator/agent fix-status phone pings (ntfy)."""

from __future__ import annotations

import argparse
import sys

from scripts.ppe_progress_notify import notify_fix_resolved, notify_fix_working


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Send ntfy when fixing or after fixing a blocked PPE operator state"
    )
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--working", action="store_true", help="Ping: work started on a fix")
    mode.add_argument("--resolved", action="store_true", help="Ping: fix attempt finished")
    ap.add_argument("--issue", required=True, help="Short label, e.g. IDE_BUILD PRODUCT_BLOCKED")
    ap.add_argument("--detail", default="", help="Extra context when --working")
    ap.add_argument("--summary", default="", help="What happened when --resolved")
    ap.add_argument("--verdict", default="", help="New operator verdict when --resolved")
    ap.add_argument("--plan", default="", help="Active phase plan path")
    args = ap.parse_args(argv)

    if args.working:
        ok = notify_fix_working(args.issue, detail=args.detail, plan_path=args.plan)
    else:
        ok = notify_fix_resolved(
            args.issue,
            summary=args.summary,
            verdict=args.verdict,
            plan_path=args.plan,
        )

    if ok:
        return 0
    print(
        "ppe_notify_fix: not sent (set PPE_NTFY_TOPIC in ppe_operator_notify.local.cmd)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
