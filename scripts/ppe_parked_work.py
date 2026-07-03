"""Park mixed-plane / blocked work for operator thread pickup.

Charter/explore threads write; operator thread reads and clears.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

PARKED_WORK_REL = "artifacts/control_plane/PARKED_WORK.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_parked_work(
    repo: Path,
    *,
    reason: str,
    thread_role: str = "charter",
    paths_by_plane: dict[str, list[str]] | None = None,
    note: str | None = None,
) -> Path:
    repo = repo.resolve()
    payload: dict[str, Any] = {
        "as_of": _utc_now(),
        "reason": reason,
        "thread_role": thread_role,
        "paths_by_plane": paths_by_plane or {},
        "note": note,
        "operator_action": "python scripts/ppe_branch_recovery.py --plan-only",
    }
    try:
        from scripts.ppe_repo_state import assess_repo_state

        state = assess_repo_state(repo)
        payload["repo_state"] = {
            "severity": state.get("severity_label"),
            "mixed_plane": state.get("mixed_plane"),
            "recommended_commands": state.get("recommended_commands"),
        }
        if not payload["paths_by_plane"]:
            payload["paths_by_plane"] = state.get("paths_by_plane") or {}
    except Exception:
        pass
    out = repo / PARKED_WORK_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def load_parked_work(repo: Path) -> dict[str, Any] | None:
    p = repo / PARKED_WORK_REL
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def clear_parked_work(repo: Path) -> bool:
    p = repo / PARKED_WORK_REL
    if p.is_file():
        p.unlink()
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Park blocked work for operator pickup.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--reason", default="mixed_plane")
    ap.add_argument("--thread-role", default="charter")
    ap.add_argument("--note", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.clear:
        cleared = clear_parked_work(repo)
        if args.json:
            print(json.dumps({"cleared": cleared}))
        return 0
    if args.write:
        path = write_parked_work(
            repo,
            reason=args.reason,
            thread_role=args.thread_role,
            note=args.note,
        )
        if args.json:
            print(json.dumps({"written": str(path.relative_to(repo))}))
        else:
            print(f"ppe_parked_work: wrote {path.relative_to(repo)}")
        return 0

    data = load_parked_work(repo)
    if args.json:
        print(json.dumps(data or {}, indent=2))
    else:
        print(f"ppe_parked_work: {'present' if data else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
