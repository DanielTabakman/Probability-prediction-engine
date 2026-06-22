"""Bounded gate-failure retry for IDE BUILD closeout."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPAIR_STATE_REL = "artifacts/orchestrator/BUILD_REPAIR_STATE.json"
REPAIR_HINT_REL = "artifacts/orchestrator/BUILD_REPAIR_HINT.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_repair_max_attempts(repo: Path) -> int:
    env = os.environ.get("PPE_BUILD_REPAIR_MAX_ATTEMPTS", "").strip()
    if env.isdigit():
        return max(1, int(env))
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo.resolve())
        ab = cfg.get("autobuilder")
        if isinstance(ab, dict):
            raw = ab.get("buildRepairMaxAttempts")
            if isinstance(raw, int) and raw > 0:
                return raw
    except ImportError:
        pass
    return 3


def repair_state_path(repo: Path) -> Path:
    return (repo.resolve() / REPAIR_STATE_REL).resolve()


def repair_hint_path(repo: Path) -> Path:
    return (repo.resolve() / REPAIR_HINT_REL).resolve()


def load_repair_state(repo: Path) -> dict[str, Any]:
    path = repair_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_repair_state(repo: Path, data: dict[str, Any]) -> Path:
    path = repair_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = _utc_now()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def write_repair_hint(
    repo: Path,
    *,
    slice_id: str,
    attempt: int,
    max_attempts: int,
    gate_output: str,
) -> Path:
    path = repair_hint_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "# BUILD repair hint",
            "",
            f"**Slice:** `{slice_id}`",
            f"**Attempt:** {attempt} / {max_attempts}",
            f"**As-of:** {_utc_now()}",
            "",
            "## Agent action",
            "",
            "Fix gate failures below, then re-run `python scripts/run_pushable_gate.py`.",
            "Spawn `@ppe-build-worker` only if attempts exhausted.",
            "",
            "## Gate output (tail)",
            "",
            "```",
            gate_output[-4000:] if gate_output else "(no output)",
            "```",
            "",
        ]
    )
    path.write_text(body, encoding="utf-8")
    return path


def run_pushable_gate(repo: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "scripts/run_pushable_gate.py"],
        cwd=repo.resolve(),
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out


def run_bounded_gate(
    repo: Path,
    *,
    slice_id: str,
    reset: bool = False,
) -> dict[str, Any]:
    """One gate attempt per call; track attempts across closeout retries."""
    repo = repo.resolve()
    max_attempts = build_repair_max_attempts(repo)
    state = {} if reset else load_repair_state(repo)
    if reset or str(state.get("slice_id") or "") != slice_id:
        state = {"slice_id": slice_id, "attempts": 0, "exhausted": False}

    if state.get("exhausted"):
        return {
            "ok": False,
            "exhausted": True,
            "attempts": int(state.get("attempts") or max_attempts),
            "max_attempts": max_attempts,
            "hint_path": str(repair_hint_path(repo).relative_to(repo)).replace("\\", "/"),
            "message": "repair attempts exhausted — escalate to @ppe-triage-worker",
        }

    attempt = int(state.get("attempts") or 0) + 1
    rc, last_out = run_pushable_gate(repo)
    state["attempts"] = attempt
    state["last_rc"] = rc
    state["last_at"] = _utc_now()

    if rc == 0:
        state = {"slice_id": slice_id, "attempts": 0, "exhausted": False}
        save_repair_state(repo, state)
        hint = repair_hint_path(repo)
        if hint.is_file():
            hint.unlink()
        return {
            "ok": True,
            "attempts": attempt,
            "max_attempts": max_attempts,
            "exhausted": False,
        }

    exhausted = attempt >= max_attempts
    state["exhausted"] = exhausted
    save_repair_state(repo, state)
    hint = write_repair_hint(
        repo,
        slice_id=slice_id,
        attempt=attempt,
        max_attempts=max_attempts,
        gate_output=last_out,
    )
    msg = (
        f"gate failed after {attempt} attempt(s) — escalate to triage"
        if exhausted
        else f"gate failed (attempt {attempt}/{max_attempts}) — fix and re-run closeout"
    )
    return {
        "ok": False,
        "exhausted": exhausted,
        "attempts": attempt,
        "max_attempts": max_attempts,
        "hint_path": str(hint.relative_to(repo)).replace("\\", "/"),
        "message": msg,
    }
