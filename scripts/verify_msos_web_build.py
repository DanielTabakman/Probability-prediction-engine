#!/usr/bin/env python3
"""Run `next build` for apps/msos-web — catches Edge middleware and import-cycle failures.

Witness tests only read source files; this script compiles the Next.js app like production.

Usage:
  python scripts/verify_msos_web_build.py
  python scripts/verify_msos_web_build.py --witness-only

Env:
  PPE_MSOS_WEB_BUILD=1  — require npm locally (default: skip build if npm missing off-CI)
  GITHUB_ACTIONS=1      — npm/build required (set automatically in CI)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
MIDDLEWARE = MSOS_WEB / "src" / "middleware.ts"


def witness_middleware_edge_safe() -> list[str]:
    errors: list[str] = []
    if not MIDDLEWARE.is_file():
        errors.append(f"missing {MIDDLEWARE.relative_to(REPO_ROOT)}")
        return errors
    text = MIDDLEWARE.read_text(encoding="utf-8")
    if 'from "crypto"' in text or "from 'crypto'" in text:
        errors.append("middleware must not import Node crypto (Edge runtime 500 on every route)")
    if "crypto.randomUUID()" not in text:
        errors.append("middleware must use Web Crypto crypto.randomUUID() for session ids")
    return errors


def _npm_on_path() -> bool:
    return shutil.which("npm") is not None


def run_npm_build() -> int:
    if not MSOS_WEB.is_dir():
        print(f"ERROR: missing {MSOS_WEB}", file=sys.stderr)
        return 1
    lock = MSOS_WEB / "package-lock.json"
    if not lock.is_file():
        print(f"ERROR: missing {lock}", file=sys.stderr)
        return 1

    for cmd in (["npm", "ci"], ["npm", "run", "build"]):
        print(f"+ {' '.join(cmd)}  (cwd={MSOS_WEB})")
        proc = subprocess.run(cmd, cwd=MSOS_WEB)
        if proc.returncode != 0:
            return proc.returncode
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify MSOS Next.js production build.")
    ap.add_argument(
        "--witness-only",
        action="store_true",
        help="Static middleware checks only (no npm)",
    )
    args = ap.parse_args(argv)

    witness_errors = witness_middleware_edge_safe()
    if witness_errors:
        for err in witness_errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    if args.witness_only:
        print("msos web build witness: OK")
        return 0

    in_ci = os.environ.get("GITHUB_ACTIONS", "").strip() == "true"
    require_local = os.environ.get("PPE_MSOS_WEB_BUILD", "").strip() == "1"

    if not _npm_on_path():
        if in_ci or require_local:
            print("ERROR: npm not found on PATH (required for msos web build)", file=sys.stderr)
            return 1
        print("SKIP: npm not on PATH — msos web build witness only (set PPE_MSOS_WEB_BUILD=1 to require)")
        return 0

    rc = run_npm_build()
    if rc == 0:
        print("msos web build: OK")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
