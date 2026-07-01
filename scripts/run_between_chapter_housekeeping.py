"""Run between-chapter housekeeping maintenance (queue + structural health)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

EVIDENCE_REL = "docs/SOP/REPO_BETWEEN_CHAPTER_HOUSEKEEPING_EVIDENCE_STATUS.md"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run(cmd: list[str], repo: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def run_housekeeping(repo: Path) -> dict:
    repo = repo.resolve()
    py = sys.executable
    steps: list[dict] = []

    for label, cmd in (
        ("queue_health", [py, "scripts/ppe_queue_health.py", "--repo-root", str(repo), "--apply"]),
        ("codebase_health_gate", [py, "scripts/run_codebase_health_gate.py", "--repo-root", str(repo)]),
    ):
        code, output = _run(cmd, repo)
        steps.append({"step": label, "exit_code": code, "output_tail": output[-2000:]})

    from scripts.ppe_structural_health import structural_health_block

    structural = structural_health_block(repo)
    return {
        "ok": all(s["exit_code"] == 0 for s in steps),
        "steps": steps,
        "structural_health": structural,
        "completed_at": _utc_now(),
    }


def _touch_evidence(repo: Path, result: dict) -> None:
    path = repo / EVIDENCE_REL
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    stamp = str(result.get("completed_at") or _utc_now())
    if "| Scheduled | — |" in text:
        text = text.replace("| Scheduled | — |", f"| Scheduled | {stamp} |", 1)
    if "| Completed | — |" in text:
        ok = "OK" if result.get("ok") else "FAIL"
        text = text.replace("| Completed | — |", f"| Completed | {stamp} ({ok}) |", 1)
    path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Between-chapter housekeeping runner")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skip-evidence-touch", action="store_true")
    args = ap.parse_args(argv)

    result = run_housekeeping(args.repo_root.resolve())
    if not args.skip_evidence_touch:
        _touch_evidence(args.repo_root.resolve(), result)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
