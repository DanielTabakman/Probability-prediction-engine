"""Refuse to start the operator stack unless this machine is the chartered loop host."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

GUARD_EXIT = 8


def loop_host_start_allowed() -> tuple[bool, str, str]:
    """Return (allowed, reason_code, detail)."""
    forbidden = os.environ.get("PPE_STACK_FORBIDDEN", "").strip().lower() in ("1", "true", "yes", "on")
    if forbidden:
        return (
            False,
            "stack_forbidden",
            "PPE_STACK_FORBIDDEN is set — this machine is the daily-driver host; loop runs on the VM only.",
        )

    loop_host = os.environ.get("PPE_LOOP_HOST", "").strip() == "1"
    if loop_host:
        return True, "loop_host", "PPE_LOOP_HOST=1"

    force = os.environ.get("PPE_FORCE_STACK", "").strip() == "1"
    if force:
        return True, "force", "PPE_FORCE_STACK=1 override (escape hatch only)"

    return (
        False,
        "not_loop_host",
        "PPE_LOOP_HOST is not set — copy ppe_operator_loop_host.local.cmd.example on the VM only. "
        "See docs/SOP/PPE_VM_LOOP_HOST_V1.md",
    )


def loop_host_blocked() -> dict[str, str] | None:
    allowed, code, detail = loop_host_start_allowed()
    if allowed:
        return None
    return {"guard_code": code, "guard_detail": detail}


def require_loop_host(*, quiet: bool = False) -> None:
    blocked = loop_host_blocked()
    if blocked is None:
        if not quiet:
            _, code, _ = loop_host_start_allowed()
            print(f"ppe_loop_host_guard: ok ({code})")
        return
    print(
        f"ppe_loop_host_guard: blocked ({blocked['guard_code']}) — {blocked['guard_detail']}",
        file=sys.stderr,
    )
    raise SystemExit(GUARD_EXIT)


def guard_or_exit(*, quiet: bool = False) -> None:
    require_loop_host(quiet=quiet)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Loop-host guard — VM-only stack start")
    ap.add_argument("--require", action="store_true", help="Exit 8 when stack start is not allowed")
    ap.add_argument("--check", action="store_true", help="Print JSON status and exit 0/8")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    allowed, code, detail = loop_host_start_allowed()
    if args.check:
        print(json.dumps({"allowed": allowed, "code": code, "detail": detail}, indent=2))
        return 0 if allowed else GUARD_EXIT

    if args.require:
        if allowed:
            if not args.quiet:
                print(f"ppe_loop_host_guard: ok ({code})")
            return 0
        print(f"ppe_loop_host_guard: blocked ({code}) — {detail}", file=sys.stderr)
        return GUARD_EXIT

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
