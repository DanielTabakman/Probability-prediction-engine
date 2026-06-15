"""One-shot heal: manifest RUNNING without ACTIVE_RUN -> READY."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def heal(repo: Path) -> bool:
    manifest_path = repo / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json"
    active_path = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    if not manifest_path.is_file():
        print("heal_stale_manifest: missing manifest", file=sys.stderr)
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    before = str(manifest.get("status") or "").upper()
    print(f"heal_stale_manifest: status before={before!r} active_run={active_path.is_file()}")
    if before != "RUNNING":
        print("heal_stale_manifest: nothing to do")
        return True
    if active_path.is_file():
        print("heal_stale_manifest: ACTIVE_RUN present — not healing", file=sys.stderr)
        return False
    manifest["status"] = "READY"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("heal_stale_manifest: status after=READY")
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Heal stale RUNNING manifest")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    return 0 if heal(args.repo_root.resolve()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
