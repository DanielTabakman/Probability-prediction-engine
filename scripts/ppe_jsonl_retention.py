"""Rotate large append-only JSONL telemetry files (product usage, web feedback)."""

from __future__ import annotations

import argparse
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MAX_MB = 32
DEFAULT_KEEP = 3

TARGETS = (
    ("ppe_product_usage.jsonl", "PPE_PRODUCT_USAGE_JSONL", "PPE_PRODUCT_USAGE_DIR"),
    ("ppe_web_feedback.jsonl", None, "PPE_WEB_FEEDBACK_DIR"),
)


def resolve_jsonl_path(repo: Path, filename: str, jsonl_env: str | None, dir_env: str | None) -> Path:
    if jsonl_env:
        raw = os.environ.get(jsonl_env, "").strip()
        if raw:
            p = Path(raw).expanduser()
            return p if not p.is_dir() else p / filename
    if dir_env:
        raw = os.environ.get(dir_env, "").strip()
        if raw:
            return Path(raw).expanduser() / filename
    return repo / "data" / filename


def rotate_file(path: Path, *, max_bytes: int, keep: int, dry_run: bool = False) -> bool:
    if not path.is_file():
        return False
    if path.stat().st_size <= max_bytes:
        return False
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = path.with_name(f"{path.stem}.{ts}{path.suffix}")
    if dry_run:
        print(f"ppe_jsonl_retention: would rotate {path} -> {archive.name}")
        return True
    shutil.move(path, archive)
    path.touch()
    archives = sorted(path.parent.glob(f"{path.stem}.*{path.suffix}"), reverse=True)
    for old in archives[keep:]:
        old.unlink(missing_ok=True)
    print(f"ppe_jsonl_retention: rotated {path} (kept {min(len(archives), keep)} archive(s))")
    return True


def apply_retention(repo: Path, *, max_mb: float = DEFAULT_MAX_MB, keep: int = DEFAULT_KEEP, dry_run: bool = False) -> int:
    max_bytes = int(max_mb * 1024 * 1024)
    rotated = 0
    for filename, jsonl_env, dir_env in TARGETS:
        path = resolve_jsonl_path(repo, filename, jsonl_env, dir_env)
        if rotate_file(path, max_bytes=max_bytes, keep=keep, dry_run=dry_run):
            rotated += 1
    return rotated


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rotate telemetry JSONL files when over size threshold.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--max-mb", type=float, default=DEFAULT_MAX_MB)
    ap.add_argument("--keep", type=int, default=DEFAULT_KEEP)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if not args.apply and not args.dry_run:
        print("ppe_jsonl_retention: pass --apply or --dry-run")
        return 1
    apply_retention(args.repo_root.resolve(), max_mb=args.max_mb, keep=args.keep, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
