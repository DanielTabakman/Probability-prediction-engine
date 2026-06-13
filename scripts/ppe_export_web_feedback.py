"""Read and export MSOS web feedback (JSONL store shared with apps/msos-web)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

TRADER_LABELS = {
    "btc_options": "BTC options",
    "crypto_vol": "Other crypto vol",
    "equities": "Equities / stock options",
    "exploring": "Just exploring",
}


def default_feedback_file(repo: Path) -> Path:
    raw = (os.environ.get("PPE_WEB_FEEDBACK_DIR") or "").strip()
    if raw:
        return Path(raw).expanduser() / "ppe_web_feedback.jsonl"
    return repo / "data" / "ppe_web_feedback.jsonl"


def load_entries(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    rows.sort(key=lambda r: str(r.get("created_at_utc") or ""), reverse=True)
    return rows


def format_table(rows: list[dict[str, Any]], *, limit: int) -> str:
    lines = [
        "| When (UTC) | Understood | Return | Profile | Note | Page |",
        "|------------|------------|--------|---------|------|------|",
    ]
    for row in rows[:limit]:
        profile = TRADER_LABELS.get(str(row.get("trader_profile") or ""), row.get("trader_profile"))
        understood = row.get("understood")
        if understood == "yes":
            u = "Y"
        elif understood == "not_yet":
            u = "Not yet"
        else:
            u = str(understood)
        wr = "Y" if row.get("would_return") == "yes" else "N"
        note = (row.get("note") or "—").replace("|", "\\|")
        lines.append(
            "| {when} | {u} | {wr} | {profile} | {note} | {page} |".format(
                when=str(row.get("created_at_utc") or "").replace("T", " ").replace("Z", ""),
                u=u,
                wr=wr,
                profile=profile,
                note=note,
                page=row.get("page_path") or "—",
            )
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export MSOS web feedback JSONL")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--markdown", action="store_true", help="Print markdown table")
    parser.add_argument("--json", action="store_true", help="Print JSON array")
    args = parser.parse_args(argv)

    path = default_feedback_file(args.repo_root.resolve())
    rows = load_entries(path)

    if args.json:
        print(json.dumps(rows[: args.limit], indent=2))
    elif args.markdown:
        if not rows:
            print("_No web feedback submissions yet._")
        else:
            print(format_table(rows, limit=args.limit))
    else:
        print(f"file: {path}")
        print(f"count: {len(rows)}")
        for row in rows[: args.limit]:
            profile = TRADER_LABELS.get(str(row.get("trader_profile") or ""), row.get("trader_profile"))
            print(
                f"{row.get('created_at_utc')}  understood={row.get('understood')}  "
                f"return={row.get('would_return')}  profile={profile}  note={row.get('note') or ''}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
