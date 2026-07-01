"""Cursor stop hook — remind agent to auto-ship when scoped dirty work remains."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _repo_from_payload(payload: dict) -> Path | None:
    roots = payload.get("workspace_roots")
    if isinstance(roots, list):
        for root in roots:
            text = str(root or "").strip()
            if not text:
                continue
            candidate = Path(text)
            if (candidate / "scripts" / "ppe_worker_lease.py").is_file():
                return candidate.resolve()
            if (candidate / ".git").exists():
                return candidate.resolve()
    if (_REPO / "scripts" / "ppe_worker_lease.py").is_file():
        return _REPO
    return None


def build_stop_followup(payload: dict, *, repo: Path) -> str | None:
    if str(payload.get("status") or "") != "completed":
        return None
    if int(payload.get("loop_count") or 0) >= 1:
        return None

    from scripts.ppe_worker_lease import operator_ship_hint

    hint = operator_ship_hint(repo)
    if not hint:
        return None

    return (
        "PPE auto-ship: scoped dirty work remains. Ship without asking the operator — "
        f"run: `{hint}` (see AGENTS.md)."
    )


def main(argv: list[str] | None = None) -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("{}")
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print("{}")
        return 0
    if not isinstance(payload, dict):
        print("{}")
        return 0

    repo = _repo_from_payload(payload)
    if repo is None:
        print("{}")
        return 0

    followup = build_stop_followup(payload, repo=repo)
    if not followup:
        print("{}")
        return 0

    print(json.dumps({"followup_message": followup}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
