"""Founder collaboration pulses — layered L1–L4 text for humans and ntfy.

Canon: docs/SOP/FOUNDER_COLLABORATION_CHARTER_V1.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

CHARTER_JSON = "docs/SOP/FOUNDER_COLLABORATION_CHARTER_V1.json"
PULSE_LAST_REL = "artifacts/control_plane/FOUNDER_PULSE_LAST.json"

ACTIVE_VM_PHASES = frozenset(
    {
        "BUILD_IN_FLIGHT",
        "FINISH_IN_FLIGHT",
        "RUN_LOCAL_PENDING",
        "CLOSEOUT_PENDING",
    }
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_charter(repo: Path) -> dict[str, Any]:
    path = repo / CHARTER_JSON
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _plain_chapter(status: dict[str, Any]) -> str:
    name = str(status.get("chapter_name") or status.get("chapter") or "").strip()
    if name:
        return name
    plan = str(status.get("phase_plan_path") or "").strip()
    if plan:
        return Path(plan).stem.replace("_relay", "")
    return "unknown chapter"


def _mode_line(status: dict[str, Any]) -> str:
    cm = status.get("chapter_mode") or {}
    if isinstance(cm, dict):
        mode = str(cm.get("mode") or "").strip()
        if mode:
            return mode
    return str(status.get("mode") or "").strip() or "—"


def _vm_phase(status: dict[str, Any]) -> str:
    vm = status.get("vm_phase") or status.get("vm") or {}
    if isinstance(vm, dict):
        return str(vm.get("phase") or vm.get("raw_phase") or "").strip().upper()
    return str(vm or "").strip().upper()


def _recent_slices(repo: Path, *, hours: int = 24) -> list[dict[str, Any]]:
    path = repo / "artifacts/workflow_metrics/slices.jsonl"
    if not path.is_file():
        return []
    cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        at = str(row.get("completed_at") or "")
        try:
            ts = datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp()
        except ValueError:
            continue
        if ts >= cutoff:
            out.append(row)
    return out[-12:]


def build_morning_pulse(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    recent = _recent_slices(repo, hours=24)
    shipped = [str(r.get("slice_id") or "") for r in recent if r.get("status") == "closed"]
    lines = [
        "Good morning — yesterday in plain terms:",
        "",
        f"Shipped / closed ({len(shipped)}): "
        + (", ".join(shipped[-6:]) if shipped else "quiet on slices (check PRs on main)"),
        "",
        f"Now: {_plain_chapter(status)} · verdict {status.get('verdict') or '?'} · mode {_mode_line(status)}",
    ]
    blocker = str(status.get("blocker") or "").strip()
    if blocker:
        lines.append(f"Blocker: {blocker[:180]}")
    next_build = ""
    cm = status.get("chapter_mode") or {}
    if isinstance(cm, dict):
        next_build = str(cm.get("next_build_candidate") or "").strip()
    if next_build:
        lines.append(f"After closeout: {next_build}")
    lines.append("")
    lines.append("Your role today: see weekly digest Monday; alerts only if factory stalls.")
    return {
        "layer": "morning",
        "title": "PPE morning — yesterday + now",
        "body": "\n".join(lines),
        "founder_role": "listen",
    }


def build_completion_pulse(
    repo: Path,
    status: dict[str, Any],
    *,
    slice_id: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    finished = slice_id or str(status.get("last_completed_slice") or "work unit")
    lines = [
        f"Completion: {finished} finished.",
    ]
    if note:
        lines.append(note.strip())
    lines.append(f"Chapter: {_plain_chapter(status)} · mode {_mode_line(status)}")
    nxt = str(status.get("verdict") or "advance")
    lines.append(f"Next factory step: {nxt} (agents executing)")
    lines.append("Nothing required from you.")
    return {
        "layer": "completion",
        "title": f"PPE done — {finished}",
        "body": "\n".join(lines),
        "founder_role": "nothing",
    }


def _active_program_running(status: dict[str, Any], coord: dict[str, Any]) -> bool:
    phase = _vm_phase(status)
    if phase in ACTIVE_VM_PHASES:
        return True
    burst = status.get("burst") or {}
    if isinstance(burst, dict):
        remaining = burst.get("remaining")
        allowed = burst.get("burst_allowed")
        if allowed and remaining and int(remaining) > 0:
            return True
    if str(coord.get("verdict") or "") == "repair":
        return True
    manifest = str(status.get("manifest_status") or "").upper()
    if manifest == "RUNNING":
        return True
    return False


def assess_alert(repo: Path, status: dict[str, Any], coord: dict[str, Any]) -> dict[str, Any] | None:
    """Return alert pulse dict if Layer 3 should fire; else None."""
    if _active_program_running(status, coord):
        return None

    reasons: list[str] = []
    founder_asks: list[str] = []

    tier = str(coord.get("delegation_tier") or "auto")
    if tier == "human_only":
        reasons.append("Delegation gate requires founder authorization.")
        founder_asks.append("Authorize or adjust policy for blocked paths.")

    cm = status.get("chapter_mode") or {}
    closeout_only = isinstance(cm, dict) and cm.get("mode") == "CLOSEOUT_ONLY"
    verdict = str(status.get("verdict") or "")
    if closeout_only and verdict == "IDE_BUILD":
        issues = coord.get("chapter_issues") or []
        if issues:
            reasons.append("Bookkeeping deadlock: product on main but factory ledgers disagree.")

    coord_verdict = str(coord.get("verdict") or "")
    if coord_verdict in ("recovery", "park") and coord.get("blocks_build"):
        reasons.append(f"Relay blocked ({coord_verdict}) and no active program is fixing it.")

    if verdict == "SUPPLY_LOW":
        blocker = str(status.get("blocker") or "").lower()
        if "no ready" in blocker or "no promotable" in blocker:
            next_c = ""
            if isinstance(cm, dict):
                next_c = str(cm.get("next_build_candidate") or "").strip()
            if not next_c:
                reasons.append("No documented next BUILD candidate while queue is empty.")
                founder_asks.append("Confirm next product direction or SELECTION doc to promote.")

    if not reasons:
        return None

    body_lines = [
        "Alert: factory needs attention.",
        "",
        *[f"- {r}" for r in reasons],
        "",
        f"Chapter: {_plain_chapter(status)} · verdict {verdict} · mode {_mode_line(status)}",
    ]
    if founder_asks:
        body_lines.append("")
        body_lines.append("Decision needed: " + founder_asks[0])
    elif tier == "human_only":
        body_lines.append("")
        body_lines.append("External action or policy call — agents stopped per delegation envelope.")
    else:
        body_lines.append("")
        body_lines.append("Agents will default to repair/recovery unless you reply in charter thread.")

    return {
        "layer": "alert",
        "title": "PPE alert — factory blocked",
        "body": "\n".join(body_lines),
        "founder_role": "decision" if founder_asks else "listen",
        "reasons": reasons,
    }


def build_weekly_pulse(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    try:
        from scripts.ppe_tracking_hub import collect_tracking_snapshot

        snap = collect_tracking_snapshot(repo, days=7)
        summary = snap.get("summary") or {}
    except Exception:
        summary = {}

    lines = [
        "Weekly systems pulse:",
        "",
        f"Slices (7d): {summary.get('slices_logged', '?')} · weighted {summary.get('weighted_slices', '?')}",
        f"Closeouts (7d): {summary.get('context_closeouts', '?')}",
        f"Chapter now: {_plain_chapter(status)} · {_mode_line(status)}",
    ]
    cm = status.get("chapter_mode") or {}
    if isinstance(cm, dict):
        nxt = str(cm.get("next_build_candidate") or "").strip()
        if nxt:
            lines.append(f"Steering next BUILD: {nxt}")
    lines.extend(
        [
            "",
            "Full digest: docs/RELEASES/WEEKLY_DIGEST.md",
            "Steward backlog: digest-only unless you opt into a charter pass.",
        ]
    )
    return {
        "layer": "weekly",
        "title": "PPE weekly — systems pulse",
        "body": "\n".join(lines),
        "founder_role": "listen",
    }


def build_pulse(
    repo: Path,
    *,
    layer: str,
    slice_id: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    from scripts.ppe_coordination_check import assess_coordination_check
    from scripts.ppe_operator_status import prepare_operator_status

    repo = repo.resolve()
    status = prepare_operator_status(repo)
    coord = assess_coordination_check(repo, status=status)

    if layer == "morning":
        pulse = build_morning_pulse(repo, status)
    elif layer == "completion":
        pulse = build_completion_pulse(repo, status, slice_id=slice_id, note=note)
    elif layer == "alert":
        pulse = assess_alert(repo, status, coord)
        if pulse is None:
            pulse = {
                "layer": "alert",
                "title": "PPE — no alert",
                "body": "No Layer 3 alert: factory advancing or active program running.",
                "founder_role": "nothing",
            }
    elif layer == "weekly":
        pulse = build_weekly_pulse(repo, status)
    elif layer == "auto":
        alert = assess_alert(repo, status, coord)
        pulse = alert if alert else build_completion_pulse(repo, status, slice_id=slice_id, note=note)
    else:
        raise ValueError(f"unknown layer: {layer}")

    pulse["as_of"] = _utc_now()
    pulse["verdict"] = status.get("verdict")
    pulse["chapter_mode"] = _mode_line(status)
    return pulse


def write_pulse_artifact(repo: Path, pulse: dict[str, Any]) -> Path:
    path = repo / PULSE_LAST_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pulse, indent=2) + "\n", encoding="utf-8")
    return path


def maybe_notify(repo: Path, pulse: dict[str, Any]) -> dict[str, Any]:
    layer = str(pulse.get("layer") or "")
    if layer == "completion" and os.environ.get("PPE_FOUNDER_COMPLETION_NTFY", "0").strip().lower() not in (
        "1",
        "true",
        "yes",
    ):
        return {"sent": False, "reason": "completion_ntfy_disabled"}
    if layer == "alert":
        priority = "high"
        tags = ["ppe", "alert", "founder"]
    elif layer == "weekly":
        priority = "default"
        tags = ["ppe", "weekly", "digest"]
    elif layer == "morning":
        return {"sent": False, "reason": "use_ppe_morning_report"}
    else:
        priority = "default"
        tags = ["ppe", "completion"]

    try:
        from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy
    except ImportError:
        return {"sent": False, "reason": "notify_unavailable"}

    if not notify_enabled() or not ntfy_configured():
        return {"sent": False, "reason": "ntfy_not_configured"}

    title = str(pulse.get("title") or "PPE founder pulse")
    body = str(pulse.get("body") or "")
    sent = send_ntfy(title, body, tags=tags, priority=priority, bypass_throttle=(layer == "alert"))
    return {"sent": sent, "title": title}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Founder collaboration pulse (L1–L4)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument(
        "--layer",
        choices=["morning", "completion", "alert", "weekly", "auto"],
        default="auto",
    )
    ap.add_argument("--slice", dest="slice_id", default=None, help="For completion layer")
    ap.add_argument("--note", default=None, help="Extra completion line")
    ap.add_argument("--write", action="store_true", help="Write FOUNDER_PULSE_LAST.json")
    ap.add_argument("--notify", action="store_true", help="Send ntfy when configured")
    ap.add_argument("--json", action="store_true", help="Print JSON")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    pulse = build_pulse(repo, layer=args.layer, slice_id=args.slice_id, note=args.note)

    if args.write:
        write_pulse_artifact(repo, pulse)
    if args.notify:
        pulse["notify"] = maybe_notify(repo, pulse)

    if args.json:
        print(json.dumps(pulse, indent=2))
    else:
        print(str(pulse.get("body") or ""))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
