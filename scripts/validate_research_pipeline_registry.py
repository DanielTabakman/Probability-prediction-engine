"""Validate config/research_pipeline_registry.json against repo paths."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research_pipeline_registry import collectors, load_registry, tests  # noqa: E402


def validate_registry(repo: Path) -> list[str]:
    errors: list[str] = []
    reg = load_registry(repo)
    collector_ids = {str(c.get("id") or "") for c in collectors(repo)}

    for spec in collectors(repo):
        cid = str(spec.get("id") or "")
        for key in ("script", "cmd", "install_task"):
            rel = str(spec.get(key) or "").strip()
            if rel and not (repo / rel).is_file():
                errors.append(f"collector {cid}: missing {key} {rel}")

    test_ids: set[str] = set()
    for spec in tests(repo):
        tid = str(spec.get("id") or "")
        if tid in test_ids:
            errors.append(f"duplicate test id {tid}")
        test_ids.add(tid)
        for key in ("script", "cmd"):
            rel = str(spec.get(key) or "").strip()
            if rel and not (repo / rel).is_file():
                errors.append(f"test {tid}: missing {key} {rel}")
        for cid in spec.get("reads_collectors") or []:
            if str(cid) not in collector_ids:
                errors.append(f"test {tid}: unknown collector {cid}")

    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate research pipeline registry")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    errors = validate_registry(args.repo_root.resolve())
    if errors:
        for err in errors:
            print(f"validate_research_pipeline_registry: {err}", file=sys.stderr)
        return 1
    print("validate_research_pipeline_registry: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
