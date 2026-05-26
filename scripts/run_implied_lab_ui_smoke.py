"""
One-command wrapper for the primary implied-lab UI smoke path.

Auto-selects scenario from UI mode:
  - Default MVP1 and full lab: A_width_target_payoff (harness skips hidden controls)
  - Dual-smoke / explicit compact path: MVP1_compact_verification via harness --scenario

Delegates to scripts/implied_lab_ui_smoke_harness.py with:
  --scenario <primary>
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
SMOKE_ROOT = ROOT / "artifacts" / "ui_smoke"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.implied_lab_ui_smoke_harness import (  # noqa: E402
    primary_smoke_scenario,
    ui_smoke_env_summary,
)
from scripts.ui_smoke_diagnose import (  # noqa: E402
    diagnose_manifest,
    format_diagnosis,
)


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

    scenario = primary_smoke_scenario()
    env_summary = ui_smoke_env_summary()
    print(
        f"Primary smoke scenario: {scenario} "
        f"(PPE_POST_MVP1_LAB_UI={env_summary['ppe_post_mvp1_lab_ui'] or '(unset)'})",
        flush=True,
    )

    port = _pick_free_port()
    cmd = [
        sys.executable,
        str(HARNESS),
        "--port",
        str(port),
        "--scenario",
        scenario,
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
                if row.get("scenario") != scenario:
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
            if code != 0:
                diagnosis = diagnose_manifest(data)
                if diagnosis:
                    print(format_diagnosis(diagnosis), flush=True)
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
