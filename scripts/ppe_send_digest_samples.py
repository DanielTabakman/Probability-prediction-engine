"""Send sample morning + weekly digest ntfy messages (for phone layout testing)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy


def sample_morning_body(repo: Path | None = None) -> str:
    if repo is not None:
        from scripts.ppe_operator_status import collect_operator_status
        from scripts.ppe_morning_report import build_morning_report

        _, body = build_morning_report(repo.resolve(), collect_operator_status(repo.resolve()))
        return f"{body}\n\n[SAMPLE - live data from repo]"
    return _static_sample_morning_body()


def _static_sample_morning_body() -> str:
    return """Good morning - metrics for 2026-06-12. [SAMPLE - not real data]

Yesterday's output:
- Slices closed: 4 (2 product, 1 control, 1 smoke)
  MVP1-DistQuantV2-Product-Slice003, MVP1-DistQuantV2-Product-Slice004, MVP1-DistQuantV2-Control-Slice001, MVP1-DistQuantV2-Smoke-Slice005
- Chapters closed: 1
  mvp1_distribution_quant_research_v2

Product changes:
- Product code: +842/-126 lines - engine, viz, data
-   - MVP1-DistQuantV2-Product-Slice003: extended CSV and summary panel quant columns
-   - MVP1-DistQuantV2-Product-Slice004: tail quantile collector MVP and daily rollup hook
-   - control-plane: relay operator hardening for unattended loop
-   - (+3 more commits)

Runtime:
- Loop up: 21h 10m (88% uptime - target 24/7)
- Loop down: 2h 50m (12%)
  maintenance: 1h 30m (you took loop offline on purpose)
  gap: 1h 20m (should have been running)
- Blocked while loop up: 45m (IDE_BUILD / fix / error)

Today's build plan:
- Chapter: MSOS_storyboard_visual_parity_v1 (homepage routes vs storyboard HTML)
- Relay batch today: MSOS-DistDemo-Control-Slice001 (control), MSOS-DistDemo-Smoke-Slice002 (smoke), MSOS-DistDemo-Product-Slice002 (product)
- Chapter progress: 1/8 slices done
- Manifest: READY
- Expectation: auto-loop runs relay batches until an IDE or fix gate.

Get ahead (keep loop up):
- Should run unattended: MSOS-DistDemo-Control-Slice001, MSOS-DistDemo-Smoke-Slice002
- Will block today: IDE BUILD for MSOS-DistDemo-Product-Slice002 when relay reaches it.
- Get ahead: Starter ready: IDE_BUILD_STARTER_MSOS-DistDemo-Product-Slice002.md — do IDE BUILD before loop stops.
- Right now: Nothing needed on your phone - auto-loop is running.

Business playbook:
- Phase 2: weekly tester loop
- Score: 2/10 tester sessions (0 this week) · Report: DRAFT
- This week: Book one 20–30 min guided demo before Thursday.
- Pick one name from your outreach list (BTC options / quant-curious).
- Run demo: open docs/SOP/DEMO_OPERATOR_SCRIPT.md (~5 min) on marketstructureos.com learn loop."""


def sample_weekly_body() -> str:
    return """Strong week. 6 user-facing changes just landed. [SAMPLE - not real data]

What's different for you
- Dist-quant lab: CSV export and summary panel now show tail quantiles and P(>K) columns
- Implied lab trust strip surfaces MVP1 decision lines without opening expanders
- Command Center preview shell is live for signed-in users (preview data only)
- Distribution demo page wiring matches storyboard spacing and typography
- PPE lab onboarding copy is shorter and clearer for first-time visitors
- +1 more ship(s) this week

Behind the curtain
12 planning and CI merges kept automation moving.

On deck
- Building next: MSOS P4 visual parity chapter
- MVP1 lab still has active slices in flight

14 merges to main. Tap for the long read on GitHub.

Business playbook
- Phase 2: weekly tester loop
- Score: 2/10 tester sessions (1 this week) · Report: DRAFT
- This week: Add 1 more session(s) this week (2/10 total logged).
- Open docs/SOP/VALIDATION_REALITY_CHECKS.md § MSOS P8.
- Book 1 guided tester call this week (20–30 min). See STEWARD_VALIDATION_GUIDE_V1.md Phase 2.

Extra padding so you can see how a longer weekly digest feels on your phone:
Lorem-style filler lines that mimic a busy week with longer bullet text in the digest.
The weekly notifier caps around 3500 characters - this sample is intentionally plump.
If you can read all of this comfortably in the ntfy app, we are in good shape.
Lock screen will still only show the first line or two until you tap open.
Line 10 of filler for scroll testing on a small phone screen.
Line 11 of filler for scroll testing on a small phone screen.
Line 12 of filler for scroll testing on a small phone screen.
Line 13: MSOS homepage hero copy aligned to storyboard v3 spacing tokens.
Line 14: Streamlit implied lab compact mode smoke passed on Windows runner.
Line 15: Steward scoreboard nudges include Mon/Thu commitment lines when configured.
Line 16: Operator maintenance mode excludes intentional downtime from 24/7 gap metric.
Line 17: Phone commands now include maintenance on/off for desktop work sessions.
Line 18: Weekly digest click URL opens GitHub when repo is public on origin.
Line 19: Morning report tracks slice/chapter counts and product diff from git log.
Line 20: Extra line to approach the 3500 character weekly phone cap for layout testing.
End of sample weekly digest body."""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Send sample morning + weekly ntfy digests")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--morning-only", action="store_true")
    ap.add_argument("--weekly-only", action="store_true")
    ap.add_argument("--large", action="store_true", help="Use [SAMPLE LARGE] in titles")
    ap.add_argument("--live", action="store_true", help="Morning body from live operator status")
    args = ap.parse_args(argv)

    label = "SAMPLE LARGE" if args.large else "SAMPLE"

    try:
        from scripts.ppe_operator_config import apply_operator_env

        apply_operator_env(args.repo_root.resolve())
    except Exception:
        pass

    if not notify_enabled():
        print("ppe_send_digest_samples: PPE_NOTIFY is off", file=sys.stderr)
        return 1
    if not ntfy_configured():
        print("ppe_send_digest_samples: PPE_NTFY_TOPIC not set", file=sys.stderr)
        return 1

    send_weekly = not args.morning_only
    send_morning = not args.weekly_only

    results: list[tuple[str, bool, int]] = []

    if send_morning:
        body = sample_morning_body(args.repo_root.resolve() if args.live else None)
        ok = send_ntfy(
            f"PPE morning report [{label}]",
            body,
            tags=["ppe", "morning", "digest", "sample"],
            priority="default",
            bypass_throttle=True,
        )
        results.append(("morning", ok, len(body)))

    if send_weekly:
        body = sample_weekly_body()
        if len(body) > 3500:
            body = body[:3497] + "..."
        ok = send_ntfy(
            f"This week in PPE - Jun 2-8 [{label}]",
            body,
            tags=["ppe", "weekly", "digest", "sample"],
            priority="default",
            bypass_throttle=True,
        )
        results.append(("weekly", ok, len(body)))

    for name, ok, size in results:
        status = "sent" if ok else "FAILED"
        print(f"ppe_send_digest_samples: {name} {status} ({size} chars)")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
