"""Scan MSOS visitor surfaces for banned internal jargon (public copy gate).

Canon: docs/SOP/MSOS_PUBLIC_COPY_V1.md · docs/SOP/OPERATOR_UX_WITNESS_V1.md

Usage:
  python scripts/msos_public_copy_gate.py
  python scripts/msos_public_copy_gate.py --repo-root .
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"

BANNED_HTML_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bPPE\b", "PPE acronym"),
    (r"workflow store", "workflow store"),
    (r"display payload", "display payload"),
    (r"VALIDATION_REALITY_CHECKS", "internal validation doc name"),
    (r"Traceback \(most recent call last\)", "Python traceback"),
    (r"AttributeError", "Python AttributeError"),
    (r"Cannot find module", "Node/module error"),
    (r"snapshot feed degraded", "internal snapshot error string"),
)

WARN_HTML_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"Illustrative product storyboard", "storyboard disclaimer"),
    (r"Preview data healthy", "preview data pill"),
    (r"Live via PPE", "legacy Live via PPE label"),
    (r"\bfixture\b", "fixture jargon"),
    (r"\bstoryboard\b", "storyboard jargon"),
)

SOURCE_REL_DIRS = ("src/data", "src/components", "src/app")

SOURCE_EXCLUDE_PARTS = {"/api/", "\\api\\", "operator/feedback"}

STRING_LITERAL_RE = re.compile(r"""['"]([^'"]{3,})['"]""")


@dataclass
class CopyFinding:
    kind: str
    label: str
    detail: str
    path: str | None = None
    line: int | None = None


def _literal_is_technical(literal: str, line: str) -> bool:
    if "className" in line or "class=" in line or "metric-fixture" in line:
        return True
    if re.search(r"ppe[-_/]", literal, re.IGNORECASE):
        return True
    if literal.startswith("/api/") or literal.startswith("http"):
        return True
    return False


def scan_html(html: str, *, page_id: str) -> tuple[list[CopyFinding], list[CopyFinding]]:
    errors: list[CopyFinding] = []
    warnings: list[CopyFinding] = []
    scrubbed = re.sub(r'\sclass="[^"]*"', "", html)
    scrubbed = re.sub(r"\sclass='[^']*'", "", scrubbed)
    for pattern, label in BANNED_HTML_PATTERNS:
        flags = 0 if label == "PPE acronym" else re.IGNORECASE
        if re.search(pattern, scrubbed, flags):
            errors.append(
                CopyFinding(
                    kind="error",
                    label=label,
                    detail=f"{page_id}: matched /{pattern}/",
                    path=page_id,
                )
            )
    for pattern, label in WARN_HTML_PATTERNS:
        if re.search(pattern, scrubbed, re.IGNORECASE):
            warnings.append(
                CopyFinding(
                    kind="warning",
                    label=label,
                    detail=f"{page_id}: matched /{pattern}/",
                    path=page_id,
                )
            )
    return errors, warnings


def _should_scan_source_file(path: Path) -> bool:
    rel = path.as_posix()
    if not rel.endswith((".ts", ".tsx")):
        return False
    if any(part in rel for part in SOURCE_EXCLUDE_PARTS):
        return False
    return True


def scan_source_tree(repo_root: Path | None = None) -> tuple[list[CopyFinding], list[CopyFinding]]:
    root = repo_root or REPO_ROOT
    msos = root / "apps" / "msos-web"
    errors: list[CopyFinding] = []
    warnings: list[CopyFinding] = []

    for rel_dir in ("src/data", "src/components", "src/app"):
        scan_base = msos / rel_dir
        if not scan_base.is_dir():
            continue
        for path in sorted(scan_base.rglob("*")):
            if not path.is_file() or not _should_scan_source_file(path):
                continue
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(root).as_posix()
            for line_no, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("//") or stripped.startswith("*"):
                    continue
                if "process.env" in line or "NEXT_PUBLIC_" in line:
                    continue
                for match in STRING_LITERAL_RE.finditer(line):
                    literal = match.group(1)
                    if _literal_is_technical(literal, line):
                        continue
                    for pattern, label in BANNED_HTML_PATTERNS:
                        flags = 0 if label == "PPE acronym" else re.IGNORECASE
                        if re.search(pattern, literal, flags):
                            errors.append(
                                CopyFinding(
                                    kind="error",
                                    label=label,
                                    detail=literal[:120],
                                    path=rel,
                                    line=line_no,
                                )
                            )
                    for pattern, label in WARN_HTML_PATTERNS:
                        if re.search(pattern, literal, re.IGNORECASE):
                            warnings.append(
                                CopyFinding(
                                    kind="warning",
                                    label=label,
                                    detail=literal[:120],
                                    path=rel,
                                    line=line_no,
                                )
                            )
    return errors, warnings


def run_gate(*, repo_root: Path | None = None) -> dict:
    root = repo_root or REPO_ROOT
    errors, warnings = scan_source_tree(root)
    return {
        "passed": len(errors) == 0,
        "errors": [f.__dict__ for f in errors],
        "warnings": [f.__dict__ for f in warnings],
        "summary": {"errors": len(errors), "warnings": len(warnings)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MSOS public copy gate (banned visitor jargon)")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = run_gate(repo_root=args.repo_root)
    if args.json:
        import json

        print(json.dumps(report, indent=2))
    else:
        if report["errors"]:
            print("msos_public_copy_gate: FAIL", file=sys.stderr)
            for item in report["errors"]:
                loc = f"{item['path']}:{item['line']}" if item.get("path") else item.get("path")
                print(f"  ERROR {item['label']} @ {loc} — {item['detail']}", file=sys.stderr)
        else:
            print("msos_public_copy_gate: PASS (source scan)", file=sys.stderr)
        for item in report["warnings"]:
            loc = f"{item['path']}:{item['line']}" if item.get("path") else item.get("path")
            print(f"  warn {item['label']} @ {loc}", file=sys.stderr)

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
