"""
CI entry: single MVP1 compact implied-lab UI smoke (no dual pass).

See docs/SOP/COMMIT_POLICY_V1.md — PR CI runs this; stewards run dual smoke before merge.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "implied_lab_ui_smoke_harness.py"
SCENARIO = "MVP1_compact_verification"

STREAMLIT_READY_TIMEOUT_S = 300.0
HARNESS_SUBPROCESS_BUFFER_S = 120.0

sys.path.insert(0, str(ROOT))
from scripts.implied_lab_ui_smoke_harness import default_scenario_timeout_s  # noqa: E402


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def main() -> int:
    port = _pick_free_port()
    scenario_timeout_s = default_scenario_timeout_s(SCENARIO)
    proc_timeout_s = STREAMLIT_READY_TIMEOUT_S + scenario_timeout_s + HARNESS_SUBPROCESS_BUFFER_S
    cmd = [
        sys.executable,
        str(HARNESS),
        "--port",
        str(port),
        "--scenario",
        SCENARIO,
        "--timeout-s",
        str(STREAMLIT_READY_TIMEOUT_S),
        "--scenario-timeout-s",
        str(scenario_timeout_s),
    ]
    print(
        f"[ci_compact_smoke] scenario={SCENARIO} port={port} subprocess_timeout_s={proc_timeout_s:.0f}",
        flush=True,
    )
    t0 = time.monotonic()
    completed = subprocess.run(cmd, cwd=str(ROOT), timeout=proc_timeout_s)
    elapsed = time.monotonic() - t0
    print(f"[ci_compact_smoke] exit={completed.returncode} elapsed_s={elapsed:.1f}", flush=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
