"""Thread insight capture — distill at closeout, route to committed stores.

Canon: docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md § Thread insight capture
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

INSIGHTS_JSON_REL = "docs/SOP/THREAD_INSIGHTS.json"
INSIGHTS_MD_REL = "docs/SOP/THREAD_INSIGHTS.md"

VALID_KINDS = frozenset({"decision", "surprise", "defer", "note"})
VALID_ROUTES = frozenset({"ship_now", "triggered", "human", "build", "drop"})
REMOVED_ROUTES = frozenset({"log"})

ROUTE_ONE_LINERS = (
    "Can ship in ≤15 min? → ship_now (implement in this thread before capture).",
    "Needs action when chapter X? → triggered.",
    "Needs your policy call? → human.",
    "Real product slice? → build.",
    "Explicitly rejected? → drop.",
    "No passive log route — every insight must be actionable or dropped.",
)

CAPTURE_EXAMPLE: dict[str, Any] = {
    "thread_role": "steward",
    "insights": [
        {
            "kind": "decision",
            "text": "Closeout prints numbered insight list; planning stays in what's next?",
            "route": "human",
            "title": "Closeout vs what's next split",
            "category": "operator",
        },
        {
            "kind": "defer",
            "text": "Revisit when wallet connect chapter is chartered.",
            "route": "triggered",
            "title": "Revisit multi-provider Web3 routing",
            "priority": "low",
            "trigger_chapters": ["msos_wallet_connect_v1"],
            "trigger_keywords": ["wallet connect", "web3"],
        },
        {
            "kind": "note",
            "text": "Fix typo in CONTEXT_RULES.md heading.",
            "route": "ship_now",
        },
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def insights_path(repo: Path) -> Path:
    return repo.resolve() / INSIGHTS_JSON_REL


def load_insights(repo: Path) -> dict[str, Any]:
    path = insights_path(repo)
    if not path.is_file():
        return {
            "version": 1,
            "notes": (
                "Audit trail of context-closeout captures (every item is actionable). "
                "Populated by --capture; items also route to backlogs or ship_now in-thread."
            ),
            "items": [],
        }
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_insights(repo: Path, payload: dict[str, Any]) -> Path:
    path = insights_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def render_insights_markdown(repo: Path, *, max_recent: int = 30) -> str:
    data = load_insights(repo)
    items = [i for i in (data.get("items") or []) if isinstance(i, dict)]
    items = sorted(items, key=lambda r: str(r.get("captured_at") or ""), reverse=True)
    recent = items[:max_recent]
    lines = [
        "# Thread insights",
        "",
        "**Purpose:** Durable recall from rich Cursor threads — distilled at context closeout.",
        "",
        "| Command | Action |",
        "|---------|--------|",
        "| `context_window_closeout.cmd --record --capture` | Closeout + apply pending capture file |",
        "| `python scripts/ppe_thread_capture.py apply --file <json>` | Route a capture file only |",
        "| `python scripts/ppe_thread_capture.py example` | Print capture JSON schema |",
        "",
        f"**Machine source:** [`THREAD_INSIGHTS.json`](THREAD_INSIGHTS.json) · **Showing:** {len(recent)} most recent",
        "",
        "> **Routing:** ship_now · triggered · human · build · drop — no passive `log`.",
        "",
    ]
    if not recent:
        lines.append("_No insights captured yet._")
        lines.append("")
        return "\n".join(lines)

    for row in recent:
        iid = str(row.get("id") or "?")
        kind = str(row.get("kind") or "note")
        route = str(row.get("route") or "?")
        captured = str(row.get("captured_at") or "?")[:10]
        text = str(row.get("text") or "").strip()
        dropped = row.get("dropped") is True
        routed = row.get("routed_to") if isinstance(row.get("routed_to"), dict) else {}
        title = f"### {iid}"
        if dropped:
            title += " _(dropped)_"
        lines.extend([title, ""])
        lines.append(f"- **captured:** {captured} · **kind:** {kind} · **route:** {route}")
        if row.get("chapter_id"):
            lines.append(f"- **chapter:** `{row.get('chapter_id')}`")
        if routed.get("type"):
            dest_id = routed.get("id") or routed.get("chapterId") or "?"
            lines.append(f"- **also filed:** {routed.get('type')} → `{dest_id}`")
        if row.get("route_error"):
            lines.append(f"- **route error:** {row.get('route_error')}")
        lines.append(f"- {text}")
        lines.append("")

    if len(items) > max_recent:
        lines.append(f"_… and {len(items) - max_recent} older entries in JSON._")
        lines.append("")
    lines.append("## Changelog")
    lines.append("")
    lines.append(f"| {datetime.now(timezone.utc).date().isoformat()} | Auto-render from JSON |")
    lines.append("")
    return "\n".join(lines)


def write_insights_markdown(repo: Path) -> Path:
    path = repo.resolve() / INSIGHTS_MD_REL
    path.write_text(render_insights_markdown(repo), encoding="utf-8")
    return path


def _validate_insight(raw: dict[str, Any], index: int) -> dict[str, Any]:
    kind = str(raw.get("kind") or "note").strip().lower()
    route = str(raw.get("route") or "").strip().lower()
    text = str(raw.get("text") or "").strip()
    if kind not in VALID_KINDS:
        raise ValueError(f"insights[{index}].kind must be one of {sorted(VALID_KINDS)}")
    if route in REMOVED_ROUTES:
        raise ValueError(
            f"insights[{index}].route=log is removed — use ship_now|triggered|human|build|drop "
            f"(see ROUTE_ONE_LINERS in ppe_thread_capture.py)"
        )
    if route not in VALID_ROUTES:
        raise ValueError(f"insights[{index}].route must be one of {sorted(VALID_ROUTES)}")
    if not route:
        raise ValueError(f"insights[{index}].route is required")
    if not text:
        raise ValueError(f"insights[{index}].text is required")
    if route in ("triggered", "human", "build") and not str(raw.get("title") or text[:80]).strip():
        raise ValueError(f"insights[{index}].title is required for route={route}")
    if route == "build" and not str(raw.get("chapter_id") or raw.get("chapterId") or "").strip():
        raise ValueError(f"insights[{index}].chapter_id is required for route=build")
    return {
        "kind": kind,
        "route": route,
        "text": text,
        "title": str(raw.get("title") or text[:80]).strip(),
        "priority": str(raw.get("priority") or "medium").strip().lower(),
        "category": str(raw.get("category") or "governance").strip().lower(),
        "policy_question": str(raw.get("policy_question") or raw.get("policyQuestion") or "").strip(),
        "chapter_id": str(raw.get("chapter_id") or raw.get("chapterId") or "").strip(),
        "reason": str(raw.get("reason") or text).strip(),
        "focus_tier": str(raw.get("focus_tier") or raw.get("focusTier") or "P2").strip().upper(),
        "idea_id": str(raw.get("idea_id") or raw.get("id") or "").strip(),
        "trigger_chapters": [
            str(x).strip() for x in (raw.get("trigger_chapters") or raw.get("triggerChapters") or []) if str(x).strip()
        ],
        "trigger_keywords": [
            str(x).strip() for x in (raw.get("trigger_keywords") or raw.get("triggerKeywords") or []) if str(x).strip()
        ],
        "not_for": [str(x).strip() for x in (raw.get("not_for") or raw.get("notFor") or []) if str(x).strip()],
    }


def load_capture_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("capture file must be a JSON object")
    insights = payload.get("insights")
    if not isinstance(insights, list) or not insights:
        raise ValueError("capture file must include a non-empty insights array")
    return payload


def _slug_from_title(title: str, backlog: dict[str, Any] | None = None) -> str:
    from scripts.ppe_triggered_ideas import _slug_id

    slug = _slug_id(title)
    for row in (backlog or {}).get("items") or []:
        if isinstance(row, dict) and str(row.get("id") or "") == slug:
            return slug
        if isinstance(row, dict) and str(row.get("title") or "").strip() == title.strip():
            return str(row.get("id") or slug)
    return slug


def _keywords_from_text(text: str) -> list[str]:
    words = [w.lower() for w in text.replace("/", " ").split() if len(w) >= 5]
    return words[:5]


def apply_capture(
    repo: Path,
    capture: dict[str, Any],
    *,
    closeout_id: str = "",
    head: str = "",
    chapter_id: str = "",
    thread_role: str = "",
) -> dict[str, Any]:
    from scripts.ppe_context_window_closeout import (
        add_build_backlog_item,
        add_human_backlog_item,
        add_triggered_idea_item,
    )

    repo = repo.resolve()
    role = (thread_role or str(capture.get("thread_role") or "steward")).strip().lower()
    insights_raw = capture.get("insights") or []
    validated = [_validate_insight(row, i) for i, row in enumerate(insights_raw) if isinstance(row, dict)]

    log_store = load_insights(repo)
    log_items = list(log_store.get("items") or [])
    counts = {"ship_now": 0, "triggered": 0, "human": 0, "build": 0, "drop": 0, "errors": 0}
    applied: list[dict[str, Any]] = []

    for item in validated:
        entry_id = str(uuid.uuid4())
        entry: dict[str, Any] = {
            "id": entry_id,
            "captured_at": _utc_now(),
            "closeout_id": closeout_id.strip() or None,
            "head": head.strip() or None,
            "chapter_id": chapter_id.strip() or None,
            "thread_role": role,
            "kind": item["kind"],
            "route": item["route"],
            "text": item["text"],
            "dropped": item["route"] == "drop",
        }
        routed_to: dict[str, Any] | None = None
        route_error: str | None = None

        if item["route"] == "drop":
            counts["drop"] += 1
        elif item["route"] == "ship_now":
            counts["ship_now"] += 1
            entry["shipped_in_thread"] = True
        elif item["route"] == "triggered":
            try:
                path = add_triggered_idea_item(
                    repo,
                    title=item["title"],
                    summary=item["text"],
                    priority=item["priority"] if item["priority"] in ("high", "medium", "low") else "low",
                    idea_id=item["idea_id"],
                    trigger_chapters=item["trigger_chapters"],
                    trigger_keywords=item["trigger_keywords"] or _keywords_from_text(item["text"]),
                    not_for=item["not_for"],
                )
                idea_id = item["idea_id"] or _slug_from_title(item["title"])
                routed_to = {"type": "triggered", "id": idea_id, "path": str(path.relative_to(repo))}
                counts["triggered"] += 1
            except SystemExit as exc:
                route_error = str(exc)
                counts["errors"] += 1
        elif item["route"] == "human":
            try:
                path = add_human_backlog_item(
                    repo,
                    title=item["title"],
                    summary=item["text"],
                    priority=item["priority"] if item["priority"] in ("high", "medium", "low") else "medium",
                    category=item["category"],
                    policy_question=item["policy_question"],
                )
                from scripts.ppe_human_backlog import load_backlog as load_human

                hid = _slug_from_title(item["title"], load_human(repo))
                routed_to = {"type": "human", "id": hid, "path": str(path.relative_to(repo))}
                counts["human"] += 1
            except SystemExit as exc:
                route_error = str(exc)
                counts["errors"] += 1
        elif item["route"] == "build":
            try:
                path = add_build_backlog_item(
                    repo,
                    chapter_id=item["chapter_id"],
                    reason=item["reason"],
                    priority=item["priority"] if item["priority"] in ("high", "medium", "low") else "medium",
                    focus_tier=item["focus_tier"],
                )
                routed_to = {
                    "type": "build",
                    "chapterId": item["chapter_id"],
                    "path": str(path.relative_to(repo)),
                }
                counts["build"] += 1
            except SystemExit as exc:
                route_error = str(exc)
                counts["errors"] += 1

        if routed_to:
            entry["routed_to"] = routed_to
        if route_error:
            entry["route_error"] = route_error
        log_items.append(entry)
        applied.append(
            {
                "id": entry_id,
                "kind": item["kind"],
                "route": item["route"],
                "routed_to": routed_to,
                "route_error": route_error,
            }
        )

    log_store["items"] = log_items
    save_insights(repo, log_store)
    write_insights_markdown(repo)

    return {
        "ok": counts["errors"] == 0,
        "counts": counts,
        "applied": applied,
        "insights_log": INSIGHTS_JSON_REL,
        "operator_summary": format_operator_capture_summary(capture, counts),
    }


def format_operator_capture_summary(
    capture: dict[str, Any],
    counts: dict[str, int] | None = None,
) -> str:
    """Numbered insight list for operator chat (mandatory at closeout)."""
    insights = [row for row in (capture.get("insights") or []) if isinstance(row, dict)]
    lines = [f"Thread closed — {len(insights)} insight(s) captured:"]
    for idx, raw in enumerate(insights, start=1):
        kind = str(raw.get("kind") or "note")
        route = str(raw.get("route") or "?")
        text = str(raw.get("text") or raw.get("title") or "").strip()
        lines.append(f"{idx}. [{kind}/{route}] {text}")
    if counts:
        lines.append(
            "Routed: "
            f"ship_now={counts.get('ship_now', 0)} "
            f"triggered={counts.get('triggered', 0)} "
            f"human={counts.get('human', 0)} "
            f"build={counts.get('build', 0)} "
            f"drop={counts.get('drop', 0)}"
        )
    return "\n".join(lines)


def default_capture_path(repo: Path) -> Path:
    return repo.resolve() / "artifacts/control_plane/THREAD_CAPTURE_PENDING.json"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Thread insight capture — route distilled insights to committed stores")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("example", help="Print example capture JSON schema")

    sub.add_parser("rules", help="Print one-line routing rules")

    ap_summary = sub.add_parser("summary", help="Print numbered operator summary from capture file")
    ap_summary.add_argument("--file", type=Path, required=True)

    ap_apply = sub.add_parser("apply", help="Apply a capture JSON file (no closeout ship)")
    ap_apply.add_argument("--file", type=Path, required=True)
    ap_apply.add_argument("--closeout-id", default="")
    ap_apply.add_argument("--head", default="")
    ap_apply.add_argument("--chapter-id", default="")
    ap_apply.add_argument("--thread-role", default="")
    ap_apply.add_argument("--json", action="store_true")

    sub.add_parser("render-md", help="Refresh THREAD_INSIGHTS.md from JSON")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.cmd == "example":
        print(json.dumps(CAPTURE_EXAMPLE, indent=2))
        return 0

    if args.cmd == "rules":
        for line in ROUTE_ONE_LINERS:
            print(line)
        return 0

    if args.cmd == "summary":
        capture = load_capture_file(args.file.resolve())
        print(format_operator_capture_summary(capture))
        return 0

    if args.cmd == "render-md":
        path = write_insights_markdown(repo)
        print(f"ppe_thread_capture: wrote {path.relative_to(repo)}")
        return 0

    if args.cmd == "apply":
        capture = load_capture_file(args.file.resolve())
        report = apply_capture(
            repo,
            capture,
            closeout_id=args.closeout_id,
            head=args.head,
            chapter_id=args.chapter_id,
            thread_role=args.thread_role,
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(report.get("operator_summary") or "")
            c = report["counts"]
            if report.get("ok"):
                print(
                    "ppe_thread_capture: applied "
                    f"ship_now={c['ship_now']} triggered={c['triggered']} human={c['human']} "
                    f"build={c['build']} drop={c['drop']} errors={c['errors']}"
                )
        return 0 if report.get("ok") else 1

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
