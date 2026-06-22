#!/usr/bin/env python3
"""Scan MSOS visitor-visible paths for banned internal jargon.

Canon: docs/SOP/MSOS_PUBLIC_COPY_V1.md
Process: docs/SOP/MSOS_COPY_AGENT_V1.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Blocking scan: copy agent + approved shippable strings
BLOCKING_ROOTS = [
    "apps/msos-web/src/content",
    "apps/msos-web/src/lib/publicCopy.ts",
    "apps/msos-web/src/lib/beliefPresets.ts",
    "apps/msos-web/src/data",
]

# Advisory scan (report only with --advisory): components may still inline strings
ADVISORY_ROOTS = [
    "apps/msos-web/src/components",
]

# Whole-word banned terms on public UI (case-insensitive)
BANNED_TERMS = [
    "workflow store",
    "display payload",
    "chromeless",
    "fixture",
    "storyboard",
    "slice",
    "screen 0",
    "snapshot feed",
    "stack trace",
    "frozen evaluation",
    "implied-lab freeze",
    "expression families",
    "optimization basis",
    "eligible rails",
    "materiality",
    "classification trace",
    "steward",
    "validation_reality_checks",
    "selection",
    "msos workflow",
]

# Standalone "PPE" or "embed" — allow "Probability Engine", code env names excluded by path
BANNED_STANDALONE = [
    (re.compile(r"\bPPE\b"), "PPE (use Probability Engine on homepage)"),
    (re.compile(r"\bembed\b", re.I), "embed (use chart or live quotes)"),
]

SKIP_FILES: set[str] = set()

# Import paths, CSS classes, module paths — not visitor copy
SKIP_LITERAL_PATTERNS = [
    re.compile(r"^@/"),
    re.compile(r"^\.\.?/"),
    re.compile(r"^metric-fixture$"),
    re.compile(r"^ppe-embed"),
    re.compile(r"^[\w-]+$"),  # single-token css/id hooks without spaces
]

STRING_LITERAL = re.compile(r"(['\"])(?:\\.|(?!\1).)*\1", re.DOTALL)


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _collect_files(roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        p = REPO_ROOT / root
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*")))
    return [f for f in files if f.is_file() and f.suffix in {".ts", ".tsx"}]


def _should_skip_literal(literal: str) -> bool:
    if len(literal.strip()) < 3:
        return True
    for pattern in SKIP_LITERAL_PATTERNS:
        if pattern.match(literal.strip()):
            return True
    return False


def _string_literals(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for m in STRING_LITERAL.finditer(text):
        raw = m.group(0)
        quote = raw[0]
        inner = raw[1:-1]
        if quote == "`" and "${" in inner:
            continue
        out.append((text[: m.start()].count("\n") + 1, inner))
    return out


def _check_literal(line_no: int, literal: str, rel_path: str) -> list[str]:
    errors: list[str] = []
    lower = literal.lower()
    for term in BANNED_TERMS:
        if term in lower:
            errors.append(f"{rel_path}:{line_no}: banned term {term!r} in {literal!r}")
    for pattern, label in BANNED_STANDALONE:
        if pattern.search(literal):
            errors.append(f"{rel_path}:{line_no}: banned {label} in {literal!r}")
    return errors


def _scan_roots(roots: list[str], *, verbose: bool) -> list[str]:
    errors: list[str] = []
    for path in _collect_files(roots):
        rel = _rel(path)
        if rel.replace("\\", "/") in SKIP_FILES:
            if verbose:
                print(f"skip {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for line_no, literal in _string_literals(text):
            if _should_skip_literal(literal):
                continue
            errors.extend(_check_literal(line_no, literal, rel))
    return errors


def validate(*, advisory: bool = False, verbose: bool = False) -> tuple[list[str], list[str]]:
    blocking = _scan_roots(BLOCKING_ROOTS, verbose=verbose)
    warnings: list[str] = []
    if advisory:
        warnings = _scan_roots(ADVISORY_ROOTS, verbose=verbose)
    return blocking, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate MSOS public copy for banned jargon.")
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="Also scan components/ and print warnings (non-blocking).",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    blocking, warnings = validate(advisory=args.advisory, verbose=args.verbose)
    if warnings:
        print("MSOS public copy advisory warnings:", file=sys.stderr)
        for warn in warnings:
            print(f"  {warn}", file=sys.stderr)
    if blocking:
        print("MSOS public copy validation FAILED:", file=sys.stderr)
        for err in blocking:
            print(f"  {err}", file=sys.stderr)
        return 1

    print("MSOS public copy validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
