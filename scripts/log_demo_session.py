"""Append demo / validation session rows for operator learning loop."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSONL_REL = "artifacts/validation/demo_sessions.jsonl"
VALIDATION_MD = ROOT / "docs/SOP/VALIDATION_REALITY_CHECKS.md"


def _utc_date() -> str:
    return datetime.now(tz=UTC).strftime("%Y-%m-%d")


def _yn(value: str | None) -> str:
    if not value:
        return "—"
    v = value.strip().upper()
    if v in ("Y", "YES", "TRUE", "1"):
        return "Y"
    if v in ("N", "NO", "FALSE", "0"):
        return "N"
    return value.strip()


def build_row(
    *,
    profile: str,
    clarity: str | None = None,
    return_again: str | None = None,
    asset: str | None = None,
    notes: str | None = None,
    check: str = "Demo session (MSOS walkthrough)",
) -> dict[str, str]:
    return {
        "date": _utc_date(),
        "check": check,
        "pass": _yn(clarity) if clarity else "—",
        "profile": profile.strip(),
        "clarity": _yn(clarity),
        "return_again": _yn(return_again),
        "asset": (asset or "BTC").strip().upper(),
        "notes": (notes or "").strip(),
    }


def append_jsonl(repo: Path, row: dict[str, str]) -> Path:
    out = repo / JSONL_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return out


def format_markdown_row(row: dict[str, str]) -> str:
    note_parts = [row["profile"]]
    if row.get("asset") and row["asset"] != "BTC":
        note_parts.append(f"asset={row['asset']}")
    if row.get("return_again") and row["return_again"] != "—":
        note_parts.append(f"return={row['return_again']}")
    if row.get("notes"):
        note_parts.append(row["notes"])
    notes = " · ".join(note_parts)
    return f"| {row['date']} | {row['check']} | {row['pass']} | {notes} |"


def append_validation_md(repo: Path, row: dict[str, str]) -> bool:
    path = repo / VALIDATION_MD.relative_to(ROOT)
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    marker = "| _fill_ | _e.g. research contact_ |"
    line = format_markdown_row(row)
    if marker in text:
        text = text.replace(marker, f"{line}\n| _fill_ | _e.g. research contact_ |", 1)
        path.write_text(text, encoding="utf-8")
        return True
    marker2 = "| _fill_ | _e.g. quant-curious friend_ |"
    if marker2 in text:
        text = text.replace(marker2, f"{line}\n| _fill_ | _e.g. quant-curious friend_ |", 1)
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Log a demo / validation session")
    ap.add_argument("--profile", required=True, help="Tester profile (e.g. 'options trader friend')")
    ap.add_argument("--clarity", help="Y/N — understood main chart / disagreement")
    ap.add_argument("--return", dest="return_again", help="Y/N — would open again")
    ap.add_argument("--asset", default="BTC", help="Primary asset shown (BTC, ETH, NVDA, …)")
    ap.add_argument("--notes", default="", help="Free-text notes / friction")
    ap.add_argument(
        "--append-validation-md",
        action="store_true",
        help="Also insert row into docs/SOP/VALIDATION_REALITY_CHECKS.md",
    )
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    row = build_row(
        profile=args.profile,
        clarity=args.clarity,
        return_again=args.return_again,
        asset=args.asset,
        notes=args.notes,
    )
    jsonl_path = append_jsonl(repo, row)
    md_ok = append_validation_md(repo, row) if args.append_validation_md else False

    print(format_markdown_row(row))
    print(f"log_demo_session: wrote {jsonl_path}")
    if args.append_validation_md:
        print(f"log_demo_session: VALIDATION_REALITY_CHECKS.md updated={md_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
