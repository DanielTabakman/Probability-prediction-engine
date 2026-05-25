"""Verify changed paths stay within steward-declared touch-set prefixes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[1]


def _normalize(path: str) -> str:
    return PurePosixPath(path.replace("\\", "/")).as_posix()


def path_allowed(path: str, prefixes: tuple[str, ...]) -> bool:
    p = _normalize(path)
    for prefix in prefixes:
        pre = _normalize(prefix)
        if not pre.endswith("/") and "/" in pre:
            if p == pre or p.startswith(pre + "/"):
                return True
        elif pre.endswith("/"):
            if p.startswith(pre):
                return True
        else:
            if p == pre or p.startswith(pre + "/"):
                return True
    return False


def check_touch_set(
    changed: tuple[str, ...],
    allowed_prefixes: tuple[str, ...],
    forbidden_prefixes: tuple[str, ...] = (),
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not allowed_prefixes:
        return False, ["no --allowed-prefixes provided"]

    for raw in changed:
        p = _normalize(raw)
        if not p:
            continue
        for forbidden in forbidden_prefixes:
            if path_allowed(p, (forbidden,)):
                errors.append(f"forbidden touch: {p} matches {forbidden}")
        if not path_allowed(p, allowed_prefixes):
            errors.append(f"outside touch set: {p}")

    return (len(errors) == 0, errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check git paths against touch-set prefixes.")
    parser.add_argument(
        "--allowed-prefixes",
        action="append",
        default=[],
        help="Allowed path prefix (repeatable).",
    )
    parser.add_argument(
        "--forbidden-prefixes",
        action="append",
        default=[],
        help="Forbidden path prefix (repeatable).",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Changed paths (posix). Default: git diff --name-only HEAD.",
    )
    args = parser.parse_args(argv)

    if args.paths is not None:
        changed = tuple(_normalize(p) for p in args.paths if p.strip())
    else:
        import subprocess

        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(result.stderr or result.stdout, file=sys.stderr)
            return 2
        changed = tuple(_normalize(ln) for ln in result.stdout.splitlines() if ln.strip())

    allowed = tuple(args.allowed_prefixes)
    forbidden = tuple(args.forbidden_prefixes or [])
    ok, errors = check_touch_set(changed, allowed, forbidden)

    if ok:
        print(f"touch_set OK ({len(changed)} path(s))")
        return 0

    for err in errors:
        print(err, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
