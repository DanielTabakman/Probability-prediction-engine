"""Write a lightweight dev note summarizing recent progress.

Inputs (best-effort):
- artifacts/logbook/ppe_events.jsonl (workflow events)
- git log (recent commits)

Outputs:
- artifacts/dev_notes/LATEST.md
- artifacts/dev_notes/LATEST.json (cursor state for incremental notes)
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _write_json(p: Path, obj: dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _tail_lines(p: Path, n: int) -> list[str]:
    if not p.is_file():
        return []
    # Readlines is fine at PPE scale; keep it simple.
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-n:] if len(lines) > n else lines


def _git(repo: Path, args: list[str]) -> str:
    out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    if out.returncode != 0:
        return ""
    return out.stdout.strip()


@dataclass(frozen=True)
class SliceAttempt:
    slice_id: str
    exit_code: int | None
    started_ts: str | None
    ended_ts: str | None
    summary: str


def _parse_events(lines: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def _attempts_from_events(events: list[dict[str, Any]]) -> list[SliceAttempt]:
    # We only log start/end right now; pair them by slice_id in order.
    in_flight: dict[str, dict[str, Any]] = {}
    attempts: list[SliceAttempt] = []
    for e in events:
        et = str(e.get("event_type") or "")
        summary = str(e.get("summary") or "")
        ts = str(e.get("ts_utc") or "") or None
        if "slice " not in summary:
            continue
        # Parse slice_id from the wrapper summary string.
        # Examples:
        # - Start slice MVP1-... (plane=..., spec=...)
        # - End slice MVP1-... exit_code=2
        parts = summary.split()
        if len(parts) < 3:
            continue
        slice_id = parts[2]
        if et.endswith(".start"):
            in_flight[slice_id] = {"ts": ts, "summary": summary}
        elif et.endswith(".end"):
            exit_code: int | None = None
            if "exit_code=" in summary:
                try:
                    exit_code = int(summary.split("exit_code=")[-1].strip())
                except Exception:
                    exit_code = None
            start = in_flight.pop(slice_id, None)
            attempts.append(
                SliceAttempt(
                    slice_id=slice_id,
                    exit_code=exit_code,
                    started_ts=(start or {}).get("ts"),
                    ended_ts=ts,
                    summary=summary,
                )
            )
    return attempts


def _render_md(*, repo: Path, attempts: list[SliceAttempt], recent_commits: list[str]) -> str:
    lines: list[str] = []
    lines.append(f"# PPE dev note (LATEST) — {_utc_now_iso()}")
    lines.append("")
    if recent_commits:
        lines.append("## Recent shipped commits (origin/main)")
        lines.append("")
        for c in recent_commits:
            lines.append(f"- {c}")
        lines.append("")
    if attempts:
        lines.append("## Recent slice attempts (from ppe_events.jsonl tail)")
        lines.append("")
        for a in attempts[-12:]:
            ec = "?" if a.exit_code is None else str(a.exit_code)
            lines.append(f"- `{a.slice_id}`: exit `{ec}` (start={a.started_ts or '—'} end={a.ended_ts or '—'})")
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This is a lightweight progress snapshot. Source: `artifacts/logbook/ppe_events.jsonl` + `git log origin/main`.")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Write PPE dev note (LATEST.md).")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--events-tail", type=int, default=200)
    ap.add_argument("--commits", type=int, default=15)
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    artifacts = repo / "artifacts"
    dev_dir = artifacts / "dev_notes"
    state_path = dev_dir / "LATEST.json"
    md_path = dev_dir / "LATEST.md"

    prev = _read_json(state_path) if state_path.is_file() else {}
    last_main = str(prev.get("origin_main_head") or "").strip()

    # Recent commits on origin/main.
    raw = _git(repo, ["log", "origin/main", f"-{int(args.commits)}", "--oneline"])
    recent_commits = [ln for ln in raw.splitlines() if ln.strip()] if raw else []

    # Event attempts (tail only).
    ev_path = artifacts / "logbook" / "ppe_events.jsonl"
    events = _parse_events(_tail_lines(ev_path, int(args.events_tail)))
    attempts = _attempts_from_events(events)

    md = _render_md(repo=repo, attempts=attempts, recent_commits=recent_commits)
    dev_dir.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")

    new_state = {"generated_at": _utc_now_iso(), "origin_main_head": (_git(repo, ["rev-parse", "origin/main"]) or last_main).strip()}
    _write_json(state_path, new_state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

