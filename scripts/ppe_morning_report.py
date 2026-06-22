"""8am local digest: yesterday metrics, today's plan, blockers, business playbook."""

from __future__ import annotations

import json
import os
import subprocess
from collections import Counter
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import (
    _load_send_state,
    _prune_send_state,
    ntfy_configured,
    notify_enabled,
    send_ntfy,
)
from scripts.ppe_operator_daily_metrics import (
    day_window_local,
    format_duration,
    format_pct,
    get_day_metrics,
    yesterday_local_date,
)
from scripts.ppe_operator_day_plan import (
    build_morning_title,
    build_plan_lines,
    business_playbook_lines,
    forecast_blockers,
    operator_today_lines,
)
from scripts.ppe_phone_status import _clean_blocker, _extract_slice_id

MORNING_STATE_REL = "artifacts/control_plane/MORNING_REPORT_STATE.json"
MORNING_ARTIFACT_REL = "artifacts/control_plane/MORNING_REPORT_LATEST.md"
MORNING_DIGEST_REL = "docs/RELEASES/MORNING_REPORT_LATEST.md"
MAX_BODY_CHARS = 3800


def morning_report_enabled() -> bool:
    raw = os.environ.get("PPE_NTFY_MORNING_REPORT", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def _parse_report_clock(value: str) -> time:
    parts = (value or "08:00").strip().split(":")
    if len(parts) != 2:
        return time(8, 0)
    try:
        return time(int(parts[0]), int(parts[1]))
    except ValueError:
        return time(8, 0)


def morning_report_time() -> time:
    return _parse_report_clock(os.environ.get("PPE_NTFY_MORNING_REPORT_AT", "08:00"))


def morning_report_window_minutes() -> int:
    raw = os.environ.get("PPE_NTFY_MORNING_REPORT_WINDOW_MIN", "45").strip()
    try:
        return max(15, int(raw))
    except ValueError:
        return 45


def state_path(repo: Path) -> Path:
    return repo / MORNING_STATE_REL


def load_state(repo: Path) -> dict[str, Any]:
    path = state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(repo: Path, state: dict[str, Any]) -> None:
    path = state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _local_today() -> str:
    return datetime.now().astimezone().date().isoformat()


def is_morning_report_window(now: datetime | None = None) -> bool:
    now = now or datetime.now().astimezone()
    target = morning_report_time()
    start = datetime.combine(now.date(), target, tzinfo=now.tzinfo)
    end = start + timedelta(minutes=morning_report_window_minutes())
    return start <= now < end


def _product_changes(repo: Path, local_date: str) -> list[str]:
    start, end = day_window_local(local_date)
    since = start.isoformat()
    until = end.isoformat()
    paths = ("src/", "apps/msos-web/")
    lines: list[str] = []

    try:
        stat_proc = subprocess.run(
            [
                "git",
                "log",
                f"--since={since}",
                f"--until={until}",
                "--numstat",
                "--format=",
                "--",
                *paths,
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        stat_proc = None

    added = deleted = 0
    touched: set[str] = set()
    if stat_proc and stat_proc.returncode == 0:
        for row in (stat_proc.stdout or "").splitlines():
            parts = row.split("\t")
            if len(parts) != 3:
                continue
            try:
                added += int(parts[0]) if parts[0] != "-" else 0
                deleted += int(parts[1]) if parts[1] != "-" else 0
            except ValueError:
                continue
            touched.add(parts[2].split("/")[1] if "/" in parts[2] else parts[2])

    try:
        subj_proc = subprocess.run(
            [
                "git",
                "log",
                f"--since={since}",
                f"--until={until}",
                "--format=%s",
                "--no-merges",
                "--",
                *paths,
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        subj_proc = None

    subjects = []
    if subj_proc and subj_proc.returncode == 0:
        subjects = [line.strip() for line in (subj_proc.stdout or "").splitlines() if line.strip()]

    if not subjects and not touched:
        return ["No product commits on src/ or apps/msos-web/."]

    if touched:
        areas = ", ".join(sorted(touched)[:5])
        if len(touched) > 5:
            areas += f" (+{len(touched) - 5} areas)"
        stat = f"+{added}/-{deleted} lines" if added or deleted else "files touched"
        lines.append(f"Product code: {stat} - {areas}")
    for subject in subjects[:3]:
        lines.append(f"  - {subject[:90]}")
    if len(subjects) > 3:
        lines.append(f"  - (+{len(subjects) - 3} more commits)")
    return lines


def _yesterday_output_lines(day_metrics: dict[str, Any]) -> list[str]:
    slices = [row for row in (day_metrics.get("slicesCompleted") or []) if isinstance(row, dict)]
    chapters = [row for row in (day_metrics.get("chaptersCompleted") or []) if isinstance(row, dict)]
    lines: list[str] = []

    if not slices and not chapters:
        lines.append("No slices or chapters closed.")
        return lines

    if slices:
        kinds = Counter(str(row.get("kind") or "other") for row in slices)
        breakdown = ", ".join(f"{count} {kind}" for kind, count in sorted(kinds.items()))
        lines.append(f"Slices closed: {len(slices)} ({breakdown})")
        names = ", ".join(str(row.get("id") or "") for row in slices[:4] if row.get("id"))
        if len(slices) > 4:
            names += f" (+{len(slices) - 4} more)"
        if names:
            lines.append(f"  {names}")

    if chapters:
        lines.append(f"Chapters closed: {len(chapters)}")
        names = ", ".join(str(row.get("id") or "") for row in chapters if row.get("id"))
        if names:
            lines.append(f"  {names}")

    return lines


def _runtime_lines(repo: Path, day_metrics: dict[str, Any], *, local_date: str, sends: list | None) -> list[str]:
    from scripts.ppe_operator_daily_metrics import uptime_trend_line

    running = int(day_metrics.get("runningSec") or 0)
    down = int(day_metrics.get("downSec") or 0)
    intentional = int(day_metrics.get("downIntentionalSec") or 0)
    unexpected = int(day_metrics.get("downUnexpectedSec") or 0)
    blocked = int(day_metrics.get("blockedSec") or 0)
    total = running + down

    if total <= 0:
        return ["No uptime samples yet - keep watch_operator_mobile running for metrics."]

    uptime_target = format_pct(running, total)
    lines = [
        f"Loop up: {format_duration(running)} ({uptime_target} uptime - target 24/7)",
        f"Loop down: {format_duration(down)} ({format_pct(down, total)})",
    ]
    trend = uptime_trend_line(repo, local_date, sends=sends)
    if trend:
        lines.append(f"  {trend}")
    if down:
        lines.append(f"  maintenance: {format_duration(intentional)} (offline on purpose)")
        lines.append(f"  gap: {format_duration(unexpected)} (should have been running)")
    if blocked:
        lines.append(f"Blocked while loop up: {format_duration(blocked)} (IDE_BUILD / fix / error)")
    return lines


def _trim_body(body: str, *, limit: int = MAX_BODY_CHARS) -> str:
    if len(body) <= limit:
        return body
    return body[: limit - 3] + "..."


def _morning_click_url(repo: Path) -> str | None:
    try:
        from scripts.ppe_weekly_digest import resolve_blob_click_url

        return resolve_blob_click_url(repo, MORNING_DIGEST_REL)
    except ImportError:
        return None


def write_morning_report_files(repo: Path, *, title: str, body: str) -> None:
    repo = repo.resolve()
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    md = f"# {title}\n\n_Generated {generated} UTC_\n\n{body}\n"
    for rel in (MORNING_ARTIFACT_REL, MORNING_DIGEST_REL):
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def build_morning_report(repo: Path, status: dict[str, Any]) -> tuple[str, str]:
    repo = repo.resolve()
    yday = yesterday_local_date()
    sends = _prune_send_state(_load_send_state(repo))
    day_metrics = get_day_metrics(repo, yday, sends=sends)
    forecast = forecast_blockers(repo, status)

    lines = [f"Good morning - metrics for {yday}.", "", "Yesterday's output:"]
    for item in _yesterday_output_lines(day_metrics):
        lines.append(f"- {item}")

    lines.extend(["", "Product changes:"])
    for item in _product_changes(repo, yday):
        lines.append(f"- {item}")

    lines.extend(["", "Runtime:"])
    for item in _runtime_lines(repo, day_metrics, local_date=yday, sends=sends):
        lines.append(f"- {item}")

    lines.extend(["", "Today's build plan:"])
    for item in build_plan_lines(repo, status):
        lines.append(f"- {item}")

    lines.extend(["", "Get ahead (keep loop up):"])
    for item in forecast:
        lines.append(f"- {item}")

    op_lines = operator_today_lines(repo, status)
    verdict = str(status.get("verdict") or "")
    blocker = str(status.get("blocker") or "")
    slice_id = _extract_slice_id(blocker)
    detail = _clean_blocker(blocker, verdict=verdict, slice_id=slice_id)
    if op_lines:
        lines.append(f"- Right now: {op_lines[0]}")
    if detail and verdict not in ("RUN_AUTO",):
        lines.append(f"- {detail}")

    lines.extend(["", "Business playbook:"])
    for item in business_playbook_lines(repo):
        lines.append(f"- {item}")

    click = _morning_click_url(repo)
    if click:
        lines.extend(["", f"Full report: {click}"])

    body = _trim_body("\n".join(lines))
    title = build_morning_title(status, forecast)
    return title, body


def maybe_send_morning_report(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    repo = repo.resolve()
    if not notify_enabled() or not ntfy_configured() or not morning_report_enabled():
        return {"sent": False, "reason": "disabled"}
    if not is_morning_report_window():
        return {"sent": False, "reason": "outside_window"}

    prior = load_state(repo)
    today = _local_today()
    if str(prior.get("last_morning_report_date") or "") == today:
        return {"sent": False, "reason": "already_sent_today"}

    title, body = build_morning_report(repo, status)
    write_morning_report_files(repo, title=title, body=body)
    sent = send_ntfy(
        title,
        body,
        tags=["ppe", "morning", "digest"],
        priority="default",
        bypass_throttle=True,
    )
    if sent:
        save_state(repo, {"last_morning_report_date": today, "sent_at": datetime.now(timezone.utc).isoformat()})
    return {"sent": sent, "title": title, "body": body}


def send_morning_report_once(repo: Path, *, force: bool = False) -> dict[str, Any]:
    """Send morning digest now (Task Scheduler fallback). Respects once-per-day unless force."""
    repo = repo.resolve()
    if not notify_enabled() or not ntfy_configured() or not morning_report_enabled():
        return {"sent": False, "reason": "disabled"}

    try:
        from scripts.ppe_operator_status import collect_operator_status
    except ImportError:
        return {"sent": False, "reason": "status_unavailable"}

    status = collect_operator_status(repo)
    if not force:
        prior = load_state(repo)
        today = _local_today()
        if str(prior.get("last_morning_report_date") or "") == today:
            return {"sent": False, "reason": "already_sent_today"}

    title, body = build_morning_report(repo, status)
    write_morning_report_files(repo, title=title, body=body)
    sent = send_ntfy(
        title,
        body,
        tags=["ppe", "morning", "digest"],
        priority="default",
        bypass_throttle=True,
    )
    if sent:
        save_state(
            repo,
            {
                "last_morning_report_date": _local_today(),
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "source": "scheduler",
            },
        )
    return {"sent": sent, "title": title, "body": body}


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(description="PPE 8am morning digest")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--send-once", action="store_true", help="Send now (Task Scheduler fallback)")
    ap.add_argument("--force", action="store_true", help="Send even if already sent today")
    ap.add_argument("--print", action="store_true", help="Print report body without sending")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.print:
        from scripts.ppe_operator_status import collect_operator_status

        title, body = build_morning_report(repo, collect_operator_status(repo))
        if args.json:
            print(json.dumps({"title": title, "body": body}, indent=2))
        else:
            print(f"{title}\n\n{body}")
        return 0

    if args.send_once or args.force:
        result = send_morning_report_once(repo, force=args.force)
        print(json.dumps(result, indent=2) if args.json else result)
        return 0 if result.get("sent") or result.get("reason") == "already_sent_today" else 1

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
