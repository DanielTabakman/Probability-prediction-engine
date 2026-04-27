"""
One-command wrapper for the primary implied-lab UI smoke path (A_width_target_payoff).

The harness also supports a second gated scenario (C_directional_peak_disagreement);
invoke implied_lab_ui_smoke_harness.py with --scenario for that path.

Delegates to scripts/implied_lab_ui_smoke_harness.py with:
  --scenario A_width_target_payoff
  --port <ephemeral free port>

Pass/fail for this command remains the harness exit code; the wrapper additionally prints
Slice003 witness fields from the manifest for closeout triage.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "implied_lab_ui_smoke_harness.py"
OFFICIAL_SCENARIO = "A_width_target_payoff"
SMOKE_ROOT = ROOT / "artifacts" / "ui_smoke"


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _dir_names(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {p.name for p in root.iterdir() if p.is_dir()}


def main() -> int:
    if not HARNESS.is_file():
        print(f"Missing harness script: {HARNESS}", file=sys.stderr)
        return 2

    port = _pick_free_port()
    cmd = [
        sys.executable,
        str(HARNESS),
        "--port",
        str(port),
        "--scenario",
        OFFICIAL_SCENARIO,
    ]

    delegated = subprocess.list2cmdline(cmd)
    print("Delegated command:", delegated, flush=True)

    before = _dir_names(SMOKE_ROOT)
    proc = subprocess.run(cmd, cwd=str(ROOT))
    code = proc.returncode

    after = _dir_names(SMOKE_ROOT)
    new_ids = sorted(after - before)
    run_dir = SMOKE_ROOT / new_ids[-1] if new_ids else None
    manifest_path = run_dir / "ui_smoke_manifest.json" if run_dir else None

    screenshot_path: str | None = None
    slice003_summary = "(n/a)"
    slice004_summary = "(n/a)"
    witness_shot: str | None = None
    if manifest_path is not None and manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            close = data.get("workflow_hardening_slice003_closeout") or {}
            for row in data.get("scenarios", []):
                if row.get("scenario") != OFFICIAL_SCENARIO:
                    continue
                screenshot_path = row.get("screenshot_path") or None
                w = row.get("slice003_witness") or {}
                witness_shot = w.get("witness_screenshot_path") or None
                slice003_summary = (
                    f"classification={w.get('classification')} "
                    f"signal={close.get('width_vol_signal')} "
                    f"evidence_plane_complete={close.get('evidence_plane_complete')}"
                )
                wd = row.get("slice004_directional_witness") or {}
                slice004_summary = (
                    f"classification={wd.get('classification')} "
                    f"signal={close.get('directional_signal')}"
                )
                break
        except Exception:
            screenshot_path = None
            slice003_summary = "(manifest parse error)"
            slice004_summary = "(manifest parse error)"

    print(f"Exit code: {code}")
    print(f"Manifest path: {manifest_path if manifest_path and manifest_path.is_file() else '(unknown)'}")
    print(f"Screenshot path: {screenshot_path if screenshot_path else '(unknown)'}")
    print(f"Slice003 witness summary: {slice003_summary}")
    print(f"Slice004 directional witness summary: {slice004_summary}")
    print(f"Slice003 witness screenshot: {witness_shot if witness_shot else '(none)'}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
