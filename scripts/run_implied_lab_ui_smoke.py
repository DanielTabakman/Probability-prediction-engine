"""
One-command wrapper for the primary implied-lab UI smoke path (A_width_target_payoff).

The harness also supports a second gated scenario (C_directional_peak_disagreement);
invoke implied_lab_ui_smoke_harness.py with --scenario for that path.

Delegates to scripts/implied_lab_ui_smoke_harness.py with:
  --scenario A_width_target_payoff
  --port <ephemeral free port>

Does not change harness behavior, pass/fail semantics for this command, or artifact layout.
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
    lab_mounted: bool | None = None
    lab_mount_blocker: str = ""
    if manifest_path is not None and manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for row in data.get("scenarios", []):
                if row.get("scenario") == OFFICIAL_SCENARIO:
                    screenshot_path = row.get("screenshot_path") or None
                    lab_mounted = row.get("lab_mounted")
                    lab_mount_blocker = str(row.get("lab_mount_blocker") or "")
                    break
        except Exception:
            screenshot_path = None

    print(f"Exit code: {code}")
    print(f"Manifest path: {manifest_path if manifest_path and manifest_path.is_file() else '(unknown)'}")
    print(f"Screenshot path: {screenshot_path if screenshot_path else '(unknown)'}")
    if lab_mounted is not None:
        print(f"Implied lab mounted: {lab_mounted}")
    if lab_mount_blocker:
        print(f"Lab mount blocker (infra/data classification): {lab_mount_blocker}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
