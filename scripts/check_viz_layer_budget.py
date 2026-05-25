"""Enforce Streamlit viz layer line budgets (see docs/SOP/VIZ_LAYER_DISCIPLINE_V1.md)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Canonical constants (VIZ_LAYER_DISCIPLINE_V1 cites these symbols).
APP_PY_BASELINE_LINES = 2109
APP_PY_SHELL_MAX_LINES = 300

APP_PY = REPO_ROOT / "src" / "viz" / "app.py"
BTC_PAGE = REPO_ROOT / "src" / "viz" / "app_bitcoin_implied_lab.py"


def _line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for _ in path.read_text(encoding="utf-8").splitlines())


def check_budget(*, shell_mode: bool | None = None) -> tuple[bool, list[str]]:
    """
    Return (ok, messages).

    shell_mode: True = post-extract (app.py <= APP_PY_SHELL_MAX_LINES).
                False = pre-extract freeze (app.py <= baseline).
                None = auto (shell if page module exists).
    """
    messages: list[str] = []
    app_lines = _line_count(APP_PY)
    page_exists = BTC_PAGE.is_file()
    page_lines = _line_count(BTC_PAGE) if page_exists else 0

    if shell_mode is None:
        shell_mode = page_exists

    errors: list[str] = []
    if shell_mode:
        if app_lines > APP_PY_SHELL_MAX_LINES:
            errors.append(
                f"app.py has {app_lines} lines; max {APP_PY_SHELL_MAX_LINES} "
                f"(APP_PY_SHELL_MAX_LINES after page extraction)."
            )
        else:
            messages.append(
                f"app.py shell OK: {app_lines} lines (max {APP_PY_SHELL_MAX_LINES})."
            )
        if page_exists:
            messages.append(f"app_bitcoin_implied_lab.py: {page_lines} lines (no hard cap).")
    else:
        if app_lines > APP_PY_BASELINE_LINES:
            errors.append(
                f"app.py has {app_lines} lines; max {APP_PY_BASELINE_LINES} "
                f"(APP_PY_BASELINE_LINES — no growth until page extraction)."
            )
        else:
            messages.append(
                f"app.py baseline OK: {app_lines} lines (max {APP_PY_BASELINE_LINES})."
            )

    for err in errors:
        messages.append(err)
    return (len(errors) == 0, messages)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check viz layer line budgets.")
    parser.add_argument(
        "--shell-mode",
        action="store_true",
        help="Enforce post-extract shell max (APP_PY_SHELL_MAX_LINES).",
    )
    parser.add_argument(
        "--baseline-mode",
        action="store_true",
        help="Enforce pre-extract baseline freeze (APP_PY_BASELINE_LINES).",
    )
    args = parser.parse_args(argv)

    mode: bool | None = None
    if args.shell_mode:
        mode = True
    elif args.baseline_mode:
        mode = False

    ok, messages = check_budget(shell_mode=mode)
    for msg in messages:
        print(msg, file=sys.stderr if not ok and "max" in msg and "OK" not in msg else sys.stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
