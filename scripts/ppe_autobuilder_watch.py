"""Scheduled autobuilder health watch — ntfy on degraded stack (Task Scheduler)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

STUCK_PHASES = frozenset(
    {
        "STACK_DOWN",
        "DEGRADED",
        "ERROR",
        "FIX_PLAN",
        "STALE_STATE",
    }
)


def run_watch(repo: Path, *, ping_webhook: bool = False, notify: bool = True) -> dict:
    from scripts.ppe_autobuilder import collect_autobuilder_status, run_diagnose, write_status_artifact

    repo = repo.resolve()
    status = collect_autobuilder_status(repo)
    write_status_artifact(repo, status)
    phase = str(status.get("phase") or "")
    out = {
        "phase": phase,
        "verdict": status.get("verdict"),
        "recommended_action": status.get("recommended_action"),
        "notified": False,
    }

    stack = status.get("stack") or {}
    needs_attention = phase in STUCK_PHASES or not stack.get("stack_ok")

    if needs_attention:
        run_diagnose(repo, ping_webhook=ping_webhook)
        if notify:
            try:
                from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy

                if notify_enabled() and ntfy_configured():
                    preview = status.get("propagation_preview") or {}
                    next_plan = preview.get("next_plan_path") or "-"
                    send_ntfy(
                        f"PPE autobuilder: {phase}",
                        f"verdict={status.get('verdict')} next={next_plan} action={status.get('recommended_action')}",
                        tags=["ppe", "autobuilder", phase.lower()],
                        priority="high" if phase == "STACK_DOWN" else "default",
                    )
                    out["notified"] = True
            except ImportError:
                pass

    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Autobuilder health watch (scheduled)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--ping-webhook", action="store_true")
    ap.add_argument("--no-notify", action="store_true")
    args = ap.parse_args(argv)
    out = run_watch(args.repo_root, ping_webhook=args.ping_webhook, notify=not args.no_notify)
    print(out)
    return 1 if out.get("phase") in STUCK_PHASES else 0


if __name__ == "__main__":
    raise SystemExit(main())
