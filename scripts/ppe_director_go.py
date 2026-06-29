"""One-shot operator handoff: refresh status, copy director prompt, open Cursor."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_ide_handoff import _detached_open, copy_text_to_clipboard, resolve_cursor_executable
from scripts.ppe_operator_hint import PPE_GO_HINT, PPE_GO_VERDICTS
from scripts.ppe_operator_status import (
    STATUS_REPORT_REL,
    VERDICT_RUN_AUTO,
    VERDICT_SUPPLY_LOW,
    collect_operator_status,
    write_status_report,
)

DIRECTOR_PROMPT = "@ppe-director Director pass. Terminal loop running."
DIRECTOR_BURST_PROMPT = (
    "@ppe-director Burst mode. Execute verdicts until WATCH stop or max 3 workers. Terminal loop running."
)

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


def run_director_go(repo: Path, *, open_ide: bool = True, burst: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    status = collect_operator_status(repo)
    write_status_report(repo, status)

    verdict = str(status.get("verdict") or "ERROR")
    blocker = str(status.get("blocker") or "").strip()
    needs_handoff = verdict in HANDOFF_VERDICTS
    prompt = DIRECTOR_BURST_PROMPT if burst else DIRECTOR_PROMPT

    result: dict[str, Any] = {
        "verdict": verdict,
        "blocker": blocker,
        "needs_handoff": needs_handoff,
        "burst": burst,
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
        lines.extend(
            [
                f"  {PPE_GO_HINT}",
                "",
                "  (Cursor opening; prompt copied to clipboard)",
            ]
        )
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
        "--burst",
        action="store_true",
        help="Copy burst-mode @ppe-director prompt (chain workers until WATCH stop)",
    )
    args = ap.parse_args(argv)

    result = run_director_go(args.repo_root, open_ide=not args.no_open, burst=args.burst)
    print(format_user_banner(result), end="")

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
