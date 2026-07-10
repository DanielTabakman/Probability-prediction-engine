"""One-shot operator handoff: refresh status, copy director prompt, open Cursor."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.ppe_burst_plan import refresh_burst_plan
from scripts.ppe_ide_handoff import _detached_open, copy_text_to_clipboard, resolve_cursor_executable
from scripts.ppe_operator_hint import PPE_GO_HINT, PPE_GO_VERDICTS
from scripts.ppe_thread_roles import OPERATOR_THREAD_OPENER, prepend_role_opener
from scripts.ppe_operator_status import (
    STATUS_BRIEF_REL,
    STATUS_REPORT_REL,
    VERDICT_RUN_AUTO,
    VERDICT_SUPPLY_LOW,
    prepare_operator_status,
    write_status_report,
)

DIRECTOR_PROMPT = prepend_role_opener(
    "@ppe-director Director pass. Terminal loop running.",
    OPERATOR_THREAD_OPENER,
)
LITE_STATUS_REL = STATUS_BRIEF_REL
BURST_PLAN_REL = "artifacts/control_plane/BURST_PLAN.json"


def _burst_prompt_from_plan(plan: dict[str, Any]) -> str:
    return str(plan.get("prompt") or DIRECTOR_PROMPT)


def _first_nonempty(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _load_whats_next_line(repo: Path) -> str:
    try:
        from scripts.ppe_context_window_closeout import load_whats_next_markdown

        text = load_whats_next_markdown(repo) or ""
    except Exception:
        text = ""
    legacy_next_action = ""
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("**Next action summary:**"):
            return line.replace("**Next action summary:**", "", 1).strip()
        if line.startswith("**Next action:**"):
            legacy_next_action = line.replace("**Next action:**", "", 1).strip()
    return _summarize_inline(legacy_next_action)


def _summarize_inline(text: str, *, max_chars: int = 280) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= max_chars:
        return compact
    cut = compact[: max_chars - 3].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return f"{cut}..."


def _strip_markdown_value(line: str) -> str:
    value = line.split(":", 1)[1].strip() if ":" in line else line.strip()
    value = value.replace("**", "").strip()
    if value.startswith("`") and "`" in value[1:]:
        return value.split("`", 2)[1].strip()
    return value.strip("`").strip()


def load_cached_lite_status(repo: Path) -> dict[str, Any]:
    status_path = repo / STATUS_REPORT_REL
    status: dict[str, Any] = {
        "verdict": "UNKNOWN",
        "cached": True,
        "commands": [],
    }
    if status_path.is_file():
        try:
            for raw in status_path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = raw.strip()
                if line.startswith("**Verdict:**"):
                    status["verdict"] = _strip_markdown_value(line)
                elif line.startswith("**Mode:**"):
                    status["chapter_mode"] = {"mode": _strip_markdown_value(line)}
                elif line.startswith("Chapter:"):
                    status["chapter_name"] = _strip_markdown_value(line)
                elif line.startswith("Plan:"):
                    status["phase_plan_path"] = _strip_markdown_value(line)
                elif line.startswith("Blocker:"):
                    status["blocker"] = _strip_markdown_value(line)
                elif line.startswith("1."):
                    cmd = line.split(".", 1)[1].strip()
                    if cmd:
                        status.setdefault("commands", []).append(cmd)
        except OSError:
            pass

    burst_path = repo / BURST_PLAN_REL
    if burst_path.is_file():
        try:
            burst = json.loads(burst_path.read_text(encoding="utf-8"))
            if isinstance(burst, dict):
                status["burst_plan"] = {
                    "overall_band": burst.get("overall_band"),
                    "remaining_count": burst.get("remaining_count"),
                    "direct_action": burst.get("direct_action"),
                    "burst_allowed": burst.get("burst_allowed"),
                }
                if status.get("verdict") == "UNKNOWN" and burst.get("verdict"):
                    status["verdict"] = burst.get("verdict")
                if not status.get("phase_plan_path") and burst.get("phase_plan_path"):
                    status["phase_plan_path"] = burst.get("phase_plan_path")
                direct = str(burst.get("direct_action") or "").strip()
                if direct and not status.get("commands"):
                    status["commands"] = [direct]
        except (OSError, json.JSONDecodeError):
            pass
    return status


def format_lite_status(status: dict[str, Any], repo: Path) -> str:
    verdict = str(status.get("verdict") or "ERROR")
    blocker = _first_nonempty(status.get("blocker"), status.get("guard", {}).get("detail") if isinstance(status.get("guard"), dict) else "")
    phase_plan = str(status.get("phase_plan_path") or "").strip()
    chapter = _first_nonempty(status.get("chapter_name"), status.get("chapter_id"))
    mode = ""
    chapter_mode = status.get("chapter_mode")
    if isinstance(chapter_mode, dict):
        mode = _first_nonempty(chapter_mode.get("mode"))
    commands = [str(x).strip() for x in (status.get("commands") or []) if str(x).strip()]
    whats_next = _load_whats_next_line(repo)
    burst = status.get("burst_plan") if isinstance(status.get("burst_plan"), dict) else {}

    lines = [
        "# Operator Status Brief",
        "",
        f"Verdict: `{verdict}`",
    ]
    if mode:
        lines.append(f"Mode: `{mode}`")
    if chapter:
        lines.append(f"Chapter: {chapter}")
    if phase_plan:
        lines.append(f"Plan: `{phase_plan}`")
    if blocker:
        lines.append(f"Blocker: {blocker}")
    if burst:
        lines.append(
            "Burst cache: "
            f"band={burst.get('overall_band')} "
            f"remaining={burst.get('remaining_count')} "
            f"allowed={burst.get('burst_allowed')} "
            f"direct_action={burst.get('direct_action')}"
        )
    if whats_next:
        lines.extend(["", f"What's next: {whats_next}"])
    if commands:
        lines.extend(["", "Agent action:"])
        lines.extend(f"- `{cmd}`" for cmd in commands[:2])
    lines.extend(
        [
            "",
            "Lite mode skipped burst refresh, director handoff, and auto-dispatch.",
            "",
        ]
    )
    return "\n".join(lines)


def write_lite_status_report(repo: Path, status: dict[str, Any]) -> Path:
    out = repo / LITE_STATUS_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(format_lite_status(status, repo), encoding="utf-8")
    return out

HANDOFF_VERDICTS = PPE_GO_VERDICTS

USER_LINES: dict[str, list[str]] = {
    VERDICT_RUN_AUTO: [
        "Nothing to do — terminal loop is running.",
    ],
    VERDICT_SUPPLY_LOW: [
        "Queue is idle — add a queued row to PHASE_CHAPTER_BACKLOG.json",
        "or run SELECTION. Loop will idle-sleep until work appears.",
    ],
}


def open_cursor_focus(repo: Path, focus: Path | None) -> dict[str, Any]:
    exe = resolve_cursor_executable()
    if not exe:
        return {"ok": False, "reason": "Cursor executable not found (install Cursor IDE)"}
    repo = repo.resolve()
    opened = _detached_open([exe, str(repo)], cwd=repo)
    if focus and focus.is_file():
        _detached_open([exe, "-r", str(focus.resolve())], cwd=repo)
    return opened


def run_director_go(
    repo: Path,
    *,
    open_ide: bool = True,
    burst: bool = True,
    lite: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    if lite:
        status = load_cached_lite_status(repo)
        brief = write_lite_status_report(repo, status)
        return {
            "verdict": str(status.get("verdict") or "ERROR"),
            "blocker": str(status.get("blocker") or "").strip(),
            "needs_handoff": False,
            "burst": False,
            "lite": True,
            "burst_plan": None,
            "prompt": None,
            "clipboard": None,
            "cursor": None,
            "brief_path": str(brief),
            "status": status,
        }

    status = prepare_operator_status(repo)
    write_status_report(repo, status, sync_burst=burst)

    verdict = str(status.get("verdict") or "ERROR")
    blocker = str(status.get("blocker") or "").strip()
    needs_handoff = verdict in HANDOFF_VERDICTS

    burst_plan: dict[str, Any] | None = status.get("burst_plan") if burst else None
    if burst and burst_plan is None:
        burst_plan = refresh_burst_plan(repo, status)
        status["burst_plan"] = burst_plan
    if burst and burst_plan:
        prompt = _burst_prompt_from_plan(burst_plan)
    else:
        prompt = DIRECTOR_PROMPT

    result: dict[str, Any] = {
        "verdict": verdict,
        "blocker": blocker,
        "needs_handoff": needs_handoff,
        "burst": burst,
        "burst_plan": burst_plan,
        "prompt": prompt if needs_handoff else None,
        "clipboard": None,
        "cursor": None,
    }

    if needs_handoff:
        result["clipboard"] = copy_text_to_clipboard(prompt)
        if open_ide:
            focus = repo / STATUS_REPORT_REL
            result["cursor"] = open_cursor_focus(repo, focus if focus.is_file() else None)

    return result


def format_user_banner(result: dict[str, Any]) -> str:
    verdict = result.get("verdict", "ERROR")
    if result.get("lite"):
        status = result.get("status") if isinstance(result.get("status"), dict) else {}
        commands = [str(x).strip() for x in (status.get("commands") or []) if str(x).strip()]
        lines = [
            "",
            "========================================",
            "  PPE GO LITE",
            f"  VERDICT: {verdict}",
            "========================================",
            "",
        ]
        blocker = str(result.get("blocker") or "").strip()
        if blocker:
            lines.extend([f"  {blocker}", ""])
        if commands:
            lines.append(f"  Agent action: {commands[0]}")
            lines.append("")
        if result.get("brief_path"):
            lines.append(f"  Brief: {result.get('brief_path')}")
            lines.append("")
        lines.append("  Lite: skipped burst refresh, director handoff, and auto-dispatch.")
        lines.extend(["", "========================================", ""])
        return "\n".join(lines)

    lines = [
        "",
        "========================================",
        "  PPE GO",
        f"  VERDICT: {verdict}",
        "========================================",
        "",
    ]
    blocker = str(result.get("blocker") or "").strip()
    if blocker:
        lines.append(f"  {blocker}")
        lines.append("")

    if result.get("needs_handoff"):
        clip = result.get("clipboard") or {}
        role_line = (
            "  THREAD_ROLE: operator (prompt copied to clipboard)"
            if clip.get("ok")
            else "  THREAD_ROLE: operator"
        )
        lines.extend(
            [
                role_line,
                f"  {PPE_GO_HINT}",
                "",
            ]
        )
        if result.get("burst") and isinstance(result.get("burst_plan"), dict):
            bp = result["burst_plan"]
            lines.append(
                f"  Burst: max_workers={bp.get('max_cycles')} band={bp.get('overall_band')} "
                f"remaining={bp.get('remaining_count')}"
            )
            lines.append("")
        if clip.get("ok"):
            lines.append("  (Cursor opening; prompt copied to clipboard)")
        else:
            lines.append("  (Cursor opening)")
    else:
        for line in USER_LINES.get(verdict, ["See artifacts/orchestrator/OPERATOR_STATUS.md"]):
            lines.append(f"  {line}")

    lines.extend(["", "========================================", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Refresh operator status and hand off to @ppe-director")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--no-open", action="store_true", help="Do not open Cursor (tests / CI)")
    ap.add_argument(
        "--single",
        action="store_true",
        help="Single @ppe-director handoff (no adaptive burst preflight)",
    )
    ap.add_argument(
        "--lite",
        action="store_true",
        help="Short read-only operator summary; skip burst refresh, director handoff, and auto-dispatch",
    )
    args = ap.parse_args(argv)

    result = run_director_go(
        args.repo_root,
        open_ide=not args.no_open and not args.lite,
        burst=not args.single,
        lite=args.lite,
    )
    try:
        print(format_user_banner(result), end="")
    except UnicodeEncodeError:
        safe = format_user_banner(result).encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8"
        )
        print(safe, end="")

    verdict = str(result.get("verdict") or "")
    if verdict == VERDICT_RUN_AUTO:
        return 0
    if result.get("needs_handoff"):
        clip = result.get("clipboard") or {}
        if clip.get("ok") is False and not clip.get("skipped"):
            prompt = result.get("prompt") or DIRECTOR_PROMPT
            print("Warning: clipboard copy failed — paste manually:", prompt, file=sys.stderr)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
