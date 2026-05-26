"""Cursor Agent health gate before run_ppe / run_phase (blocks on API failure)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_AGENT = Path(os.environ.get("LOCALAPPDATA", "")) / "cursor-agent" / "agent.ps1"
PROMPT_PROBE = "Reply with exactly: OK"
PROBE_TIMEOUT_SEC = 60


def _agent_cmd() -> list[str]:
    explicit = os.environ.get("ACP_AGENT_COMMAND", "").strip()
    if explicit:
        p = Path(explicit)
        if p.suffix.lower() == ".ps1":
            return [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(p),
            ]
        return [explicit]
    agent = DEFAULT_AGENT
    if agent.is_file():
        return [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(agent),
        ]
    return ["agent"]


def _run(argv: list[str], *, cwd: Path | None = None, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd or Path.cwd(),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _network_hint() -> list[str]:
    hints: list[str] = []
    curl = "curl.exe"
    try:
        proc = subprocess.run(
            [
                curl,
                "--ssl-no-revoke",
                "-sS",
                "-o",
                "NUL",
                "-w",
                "%{http_code}",
                "https://api2.cursor.sh/",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        code = (proc.stdout or "").strip()
        if proc.returncode != 0 or not code.isdigit():
            hints.append(
                "HTTPS to api2.cursor.sh failed (curl exit "
                f"{proc.returncode}). Restricted Wi‑Fi often blocks TLS revocation "
                "(CRYPT_E_REVOCATION_OFFLINE). Try home network or VPN off."
            )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return hints


def run_agent_healthcheck(
    repo_root: Path | None = None,
    *,
    skip_probe: bool = False,
) -> dict[str, object]:
    """Return {ok, errors, warnings, probe_output}."""
    errors: list[str] = []
    warnings: list[str] = []
    probe_output = ""

    base = _agent_cmd()
    status = _run([*base, "status"], timeout=30)
    status_out = ((status.stdout or "") + (status.stderr or "")).strip()
    if status.returncode != 0:
        errors.append(f"agent status failed (exit {status.returncode}): {status_out[:300]}")
    elif "logged in" not in status_out.lower():
        errors.append(f"agent status: not logged in? {status_out[:300]}")

    if not skip_probe and not errors:
        probe = _run(
            [*base, "--trust", "-p", PROMPT_PROBE],
            cwd=repo_root,
            timeout=PROBE_TIMEOUT_SEC,
        )
        probe_output = ((probe.stdout or "") + (probe.stderr or "")).strip()
        if probe.returncode != 0:
            errors.append(
                f"agent probe failed (exit {probe.returncode}): {probe_output[:400]}"
            )
        elif "OK" not in probe_output and "[unavailable]" in probe_output:
            errors.append(f"agent probe returned unavailable: {probe_output[:400]}")
        elif "OK" not in probe_output and "error" in probe_output.lower():
            errors.append(f"agent probe error: {probe_output[:400]}")

    warnings.extend(_network_hint())
    if errors:
        errors.append(
            "See docs/SOP/PPE_AGENT_AND_NETWORK_TROUBLESHOOTING.md. "
            "Emergency bypass: set PPE_SKIP_AGENT_CHECK=1"
        )

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "probe_output": probe_output,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE Cursor Agent health gate")
    ap.add_argument("--repo-root", type=Path, default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Print checks only, always exit 0")
    args = ap.parse_args(argv)

    if os.environ.get("PPE_SKIP_AGENT_CHECK", "").strip().lower() in ("1", "true", "yes"):
        print("ppe_agent_healthcheck: skipped (PPE_SKIP_AGENT_CHECK)")
        return 0

    repo = (args.repo_root or Path.cwd()).resolve()
    if args.dry_run:
        print("ppe_agent_healthcheck: would run agent status + probe")
        return 0

    result = run_agent_healthcheck(repo)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1

    for w in result.get("warnings") or []:
        print(f"WARN: {w}")
    for e in result.get("errors") or []:
        print(f"ERROR: {e}", file=sys.stderr)
    if result["ok"]:
        print("OK: Cursor Agent health check passed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
