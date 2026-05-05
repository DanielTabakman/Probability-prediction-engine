"""
Dual implied-lab UI smoke for MVP1 post–Phase 4 follow-up:

1) Default MVP1 chrome (no PPE_POST_MVP1_LAB_UI): `MVP1_compact_verification`
2) Full post-MVP lab (PPE_POST_MVP1_LAB_UI=1): `A_width_target_payoff`

Each pass runs `implied_lab_ui_smoke_harness.py` in a fresh subprocess with its own
Streamlit instance and ephemeral port. Exit code 0 only if both passes succeed.

Optional logbook lines (local artifacts/logbook) when `scripts/log_event.py` is available.
"""

from __future__ import annotations

import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "implied_lab_ui_smoke_harness.py"
LOG_EVENT = ROOT / "scripts" / "log_event.py"


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _run_harness(*, env: dict[str, str], scenario: str) -> int:
    port = _pick_free_port()
    cmd = [
        sys.executable,
        str(HARNESS),
        "--port",
        str(port),
        "--scenario",
        scenario,
    ]
    return subprocess.run(cmd, cwd=str(ROOT), env=env).returncode


def _maybe_log(event_type: str, summary: str, exit_code: int) -> None:
    if not LOG_EVENT.is_file():
        return
    subprocess.run(
        [
            sys.executable,
            str(LOG_EVENT),
            "--event-type",
            event_type,
            "--summary",
            f"{summary} (exit_code={exit_code})",
            "--actor",
            "mvp1_dual_smoke",
            "--ref",
            "kind=script,path=scripts/run_mvp1_dual_implied_lab_smoke.py",
        ],
        cwd=str(ROOT),
    )


def main() -> int:
    if not HARNESS.is_file():
        print(f"Missing harness: {HARNESS}", file=sys.stderr)
        return 2

    base = dict(**__import__("os").environ)

    env_mvp1 = dict(base)
    env_mvp1.pop("PPE_POST_MVP1_LAB_UI", None)

    env_full = dict(base)
    env_full["PPE_POST_MVP1_LAB_UI"] = "1"

    print("=== Pass 1: MVP1 default (no PPE_POST_MVP1_LAB_UI) — MVP1_compact_verification ===", flush=True)
    c1 = _run_harness(env=env_mvp1, scenario="MVP1_compact_verification")
    _maybe_log(
        "ui_smoke.mvp1_compact",
        f"MVP1_compact_verification exit_code={c1}",
        c1,
    )
    if c1 != 0:
        print(f"FAIL: MVP1_compact_verification returned {c1}", file=sys.stderr)
        return c1

    print("=== Pass 2: PPE_POST_MVP1_LAB_UI=1 — A_width_target_payoff ===", flush=True)
    c2 = _run_harness(env=env_full, scenario="A_width_target_payoff")
    _maybe_log(
        "ui_smoke.post_mvp_a",
        f"A_width_target_payoff exit_code={c2}",
        c2,
    )
    if c2 != 0:
        print(f"FAIL: A_width_target_payoff returned {c2}", file=sys.stderr)
        return c2

    print("OK: both dual-smoke passes succeeded.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
