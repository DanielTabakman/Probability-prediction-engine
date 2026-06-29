"""Refresh and open the MSOS module map dashboard in the default browser."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def _repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "docs" / "SOP").is_dir():
            return parent
    return Path.cwd()


def _import_render():
    repo = _repo_root()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from scripts.render_msos_module_map import (  # noqa: PLC0415
        DEFAULT_OUTPUT,
        DEFAULT_REGISTRY,
        write_html,
    )

    return DEFAULT_REGISTRY, DEFAULT_OUTPUT, write_html


def open_path(path: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"module map missing: {resolved}")

    if sys.platform == "win32":
        os.startfile(resolved)  # noqa: S606 — Windows default handler (browser)
        return

    opened = webbrowser.open(resolved.as_uri())
    if not opened:
        if sys.platform == "darwin":
            subprocess.run(["open", str(resolved)], check=False)
        else:
            subprocess.run(["xdg-open", str(resolved)], check=False)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Refresh and open MSOS module map dashboard.")
    ap.add_argument("--repo-root", type=Path, default=None)
    ap.add_argument("--no-open", action="store_true", help="Regenerate only; do not launch browser")
    args = ap.parse_args(argv)

    repo = (args.repo_root or _repo_root()).resolve()
    default_registry, default_output, write_html = _import_render()
    registry = (repo / default_registry).resolve()
    output = (repo / default_output).resolve()

    if not registry.is_file():
        print(f"registry missing: {registry}", file=sys.stderr)
        return 2

    write_html(registry_path=registry, output_path=output, repo_root=repo)
    print(f"refreshed {output.relative_to(repo)}")

    if args.no_open:
        return 0

    open_path(output)
    print("opened in default browser")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
