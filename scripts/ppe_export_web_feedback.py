"""Export MSOS web feedback JSONL for operator review and validation rollup."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSONL = ROOT / "apps" / "msos-web" / "data" / "ppe_web_feedback.jsonl"
WEB_FEEDBACK_FILENAME = "ppe_web_feedback.jsonl"


def resolve_feedback_path(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    env_dir = os.environ.get("PPE_WEB_FEEDBACK_DIR", "").strip()
    if env_dir:
        return Path(env_dir) / WEB_FEEDBACK_FILENAME
    return DEFAULT_JSONL


def load_records(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            records.append(row)
    return records


def format_markdown(records: list[dict], *, source_path: Path) -> str:
    now = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# MSOS web feedback export ({now})",
        "",
        f"Source: `{source_path}` · **{len(records)}** submission(s)",
        "",
    ]
    if not records:
        lines.append("_No submissions yet._")
        return "\n".join(lines) + "\n"

    by_source = Counter(str(r.get("source") or "unknown") for r in records)
    avg_use = sum(int(r.get("usefulness") or 0) for r in records) / len(records)
    avg_repeat = sum(int(r.get("repeat_use_intent") or 0) for r in records) / len(records)
    comprehension_y = sum(1 for r in records if str(r.get("comprehension")).upper() == "Y")
    return_y = sum(1 for r in records if str(r.get("return_intent")).upper() == "Y")

    lines.extend(
        [
            "## Summary",
            "",
            f"- Average usefulness: **{avg_use:.1f}** / 5",
            f"- Average repeat intent: **{avg_repeat:.1f}** / 5",
            f"- Comprehension Y: **{comprehension_y}**",
            f"- Return intent Y: **{return_y}**",
            "",
            "### By source",
            "",
        ]
    )
    for source, count in sorted(by_source.items()):
        lines.append(f"- `{source}`: {count}")
    lines.extend(["", "## Submissions", ""])
    lines.append(
        "| When (UTC) | Source | Profile | Comp | Return | Category | Use | Repeat | Notes |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    for row in sorted(records, key=lambda r: str(r.get("created_at_utc") or ""), reverse=True):
        notes = (row.get("objections_text") or row.get("session_note") or "").replace("|", "/")
        if len(notes) > 80:
            notes = notes[:77] + "…"
        lines.append(
            "| {when} | {source} | {profile} | {comp} | {ret} | {cat} | {use} | {repeat} | {notes} |".format(
                when=str(row.get("created_at_utc") or "—")[:19],
                source=str(row.get("source") or "—"),
                profile=str(row.get("tester_profile") or "—").replace("|", "/"),
                comp=str(row.get("comprehension") or "—"),
                ret=str(row.get("return_intent") or "—"),
                cat=str(row.get("confusion_category") or "—").replace("|", "/"),
                use=str(row.get("usefulness") or "—"),
                repeat=str(row.get("repeat_use_intent") or "—"),
                notes=notes or "—",
            )
        )

    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export MSOS web feedback JSONL.")
    parser.add_argument("--path", type=Path, default=None)
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--write", type=Path, default=None)
    args = parser.parse_args(argv)

    path = resolve_feedback_path(args.path)
    records = load_records(path)
    md = format_markdown(records, source_path=path)

    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(md, encoding="utf-8")
        print(f"ppe_export_web_feedback: wrote {args.write} ({len(records)} rows from {path})")
        return 0

    if args.markdown or not sys.stdout.isatty():
        print(md, end="")
        return 0

    print(f"ppe_export_web_feedback: {len(records)} row(s) in {path}")
    print("Use --markdown or --write <path> for a rollup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
