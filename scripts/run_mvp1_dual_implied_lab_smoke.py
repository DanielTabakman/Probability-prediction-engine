"""
Dual implied-lab UI smoke for MVP1 post–Phase 4 follow-up:

1) Default MVP1 chrome (no PPE_POST_MVP1_LAB_UI): `MVP1_compact_verification`
2) Full post-MVP lab (PPE_POST_MVP1_LAB_UI=1): `A_width_target_payoff`

Each pass runs `implied_lab_ui_smoke_harness.py` in a fresh subprocess with its own
Streamlit instance and ephemeral port. Exit code 0 only if both passes succeed.

Subprocess wall-clock caps (Streamlit ready + scenario budget + buffer) prevent
silent external kills mid-scenario; see IMPLIED_LAB_OPERATOR_RUNBOOK.md §6.

Optional logbook lines (local artifacts/logbook) when `scripts/log_event.py` is available.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "implied_lab_ui_smoke_harness.py"
LOG_EVENT = ROOT / "scripts" / "log_event.py"

STREAMLIT_READY_TIMEOUT_S = 300.0
HARNESS_SUBPROCESS_BUFFER_S = 120.0

# Import defaults from harness (single source of truth for per-scenario budgets).
sys.path.insert(0, str(ROOT))
from scripts.implied_lab_ui_smoke_harness import (  # noqa: E402
    default_scenario_timeout_s,
)


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _harness_subprocess_timeout_s(scenario: str) -> float:
    return (
        STREAMLIT_READY_TIMEOUT_S
        + default_scenario_timeout_s(scenario)
        + HARNESS_SUBPROCESS_BUFFER_S
    )


def _run_harness(*, env: dict[str, str], scenario: str) -> int:
    port = _pick_free_port()
    scenario_timeout_s = default_scenario_timeout_s(scenario)
    proc_timeout_s = _harness_subprocess_timeout_s(scenario)
    cmd = [
        sys.executable,
        str(HARNESS),
        "--port",
        str(port),
        "--scenario",
        scenario,
        "--timeout-s",
        str(STREAMLIT_READY_TIMEOUT_S),
        "--scenario-timeout-s",
        str(scenario_timeout_s),
    ]
    print(
        f"[dual_smoke] scenario={scenario} port={port} "
        f"scenario_timeout_s={scenario_timeout_s:.0f} "
        f"subprocess_timeout_s={proc_timeout_s:.0f}",
        flush=True,
    )
    t0 = time.monotonic()
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(ROOT),
            env=env,
            timeout=proc_timeout_s,
        )
        elapsed = time.monotonic() - t0
        print(
            f"[dual_smoke] scenario={scenario} finished exit={completed.returncode} "
            f"elapsed_s={elapsed:.1f}",
            flush=True,
        )
        return int(completed.returncode)
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - t0
        print(
            f"[dual_smoke] FAIL: scenario={scenario} subprocess TIMEOUT after {elapsed:.1f}s "
            f"(cap={proc_timeout_s:.0f}s; no scenario done line => environment/process kill class)",
            file=sys.stderr,
            flush=True,
        )
        return 124


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
    run_t0 = time.monotonic()

    env_mvp1 = dict(base)
    env_mvp1.pop("PPE_POST_MVP1_LAB_UI", None)

    env_full = dict(base)
    env_full["PPE_POST_MVP1_LAB_UI"] = "1"

    print(
        "=== Pass 1: MVP1 default (no PPE_POST_MVP1_LAB_UI) — MVP1_compact_verification ===",
        flush=True,
    )
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

    total_s = time.monotonic() - run_t0
    print(
        f"OK: both dual-smoke passes succeeded (total_elapsed_s={total_s:.1f}).",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
