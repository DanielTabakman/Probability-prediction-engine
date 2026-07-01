"""Canonical desktop → VM SSH helpers (timeouts, cache, brief parsing)."""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VM_SSH_HOST = os.environ.get("PPE_VM_SSH_HOST", "ppe-vm").strip() or "ppe-vm"
VM_REPO = r"C:\Users\ppeloop\Probability-prediction-engine"

SSH_ARGS: tuple[str, ...] = (
    "-o",
    "BatchMode=yes",
    "-o",
    "ConnectTimeout=15",
    "-o",
    "ServerAliveInterval=10",
    "-o",
    "ServerAliveCountMax=3",
)

DEFAULT_SSH_TIMEOUT_SECONDS = 120
VM_STATUS_CACHE_REL = "artifacts/orchestrator/VM_STATUS_CACHE.json"
VM_STATUS_CACHE_TTL_SECONDS = 300

_BRIEF_RE = re.compile(
    r"PHASE=(?P<phase>\S+)\s+VERDICT=(?P<verdict>\S+)\s+slice=(?P<slice>\S+)"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def cache_path(repo: Path) -> Path:
    return (repo / VM_STATUS_CACHE_REL).resolve()


def parse_autobuilder_brief(stdout: str) -> dict[str, str]:
    text = (stdout or "").strip()
    match = _BRIEF_RE.search(text)
    if not match:
        return {"raw": text}
    return {
        "phase": match.group("phase"),
        "verdict": match.group("verdict"),
        "slice": match.group("slice"),
        "raw": text,
    }


def ssh_vm(
    command: str,
    *,
    timeout: int = DEFAULT_SSH_TIMEOUT_SECONDS,
    host: str = VM_SSH_HOST,
) -> dict[str, Any]:
    """Run one SSH command against the loop VM with canonical opts and a hard timeout."""
    proc = subprocess.run(
        ["ssh", *SSH_ARGS, host, command],
        capture_output=True,
        text=True,
        check=False,
        timeout=max(5, int(timeout)),
    )
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": False,
        "parsed": parse_autobuilder_brief(stdout) if "PHASE=" in stdout else None,
    }


def vm_status_brief_command() -> str:
    return f"cd /d {VM_REPO} && ppe_autobuilder.cmd status --brief"


def vm_finish_command(*, pull_main: bool = False) -> str:
    if pull_main:
        return f"cd /d {VM_REPO} && git pull origin main && finish_ide_build.cmd"
    return f"cd /d {VM_REPO} && finish_ide_build.cmd"


def vm_advance_command() -> str:
    return f"cd /d {VM_REPO} && ppe_autobuilder.cmd advance"


def load_vm_status_cache(repo: Path) -> dict[str, Any] | None:
    path = cache_path(repo)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def write_vm_status_cache(repo: Path, payload: dict[str, Any]) -> Path:
    path = cache_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def cache_is_fresh(cache: dict[str, Any] | None, *, ttl_seconds: int = VM_STATUS_CACHE_TTL_SECONDS) -> bool:
    if not cache:
        return False
    as_of = str(cache.get("as_of") or "").strip()
    if not as_of:
        return False
    try:
        if as_of.endswith("Z"):
            as_of = as_of[:-1] + "+00:00"
        ts = datetime.fromisoformat(as_of)
        age = (datetime.now(timezone.utc) - ts).total_seconds()
    except ValueError:
        return False
    return age <= max(30, int(ttl_seconds))


def fetch_vm_brief(
    repo: Path,
    *,
    use_cache: bool = True,
    timeout: int = DEFAULT_SSH_TIMEOUT_SECONDS,
    write_cache: bool = True,
) -> dict[str, Any]:
    """Fetch VM autobuilder brief; reuse local cache when fresh."""
    repo = repo.resolve()
    if use_cache:
        cached = load_vm_status_cache(repo)
        if cache_is_fresh(cached):
            return {**(cached or {}), "source": "cache"}

    try:
        ssh = ssh_vm(vm_status_brief_command(), timeout=timeout)
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "timed_out": True,
            "source": "ssh",
            "error": f"ssh timed out after {timeout}s",
        }

    payload: dict[str, Any] = {
        "as_of": _utc_now(),
        "ok": ssh.get("ok"),
        "exit_code": ssh.get("exit_code"),
        "stdout": ssh.get("stdout"),
        "stderr": ssh.get("stderr"),
        "parsed": ssh.get("parsed"),
        "source": "ssh",
    }
    if write_cache and ssh.get("ok"):
        write_vm_status_cache(repo, payload)
    return payload


def resolve_vm_trust(
    *,
    local_verdict: str,
    vm_brief: dict[str, Any] | None,
    vm_mirror: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Decide whether desktop agents should wait, act, or trust VM in-flight work."""
    vm_phase = ""
    vm_verdict = ""
    source = "none"

    mirror = vm_mirror if isinstance(vm_mirror, dict) else None
    if mirror and str(mirror.get("phase") or "").strip():
        vm_phase = str(mirror.get("phase") or "").strip()
        vm_verdict = str(mirror.get("verdict") or "").strip()
        source = "mirror"

    brief = vm_brief if isinstance(vm_brief, dict) else None
    parsed = (brief or {}).get("parsed") if isinstance((brief or {}).get("parsed"), dict) else None
    if parsed:
        vm_phase = vm_phase or str(parsed.get("phase") or "").strip()
        vm_verdict = vm_verdict or str(parsed.get("verdict") or "").strip()
        if source == "none":
            source = str(brief.get("source") or "ssh")

    in_flight_phases = frozenset({"FINISH_IN_FLIGHT", "BUILD_IN_FLIGHT"})
    wait = vm_phase in in_flight_phases
    action = "wait"
    note = ""
    if wait:
        note = (
            f"VM phase `{vm_phase}` — closeout/build already running on loop host; "
            "do not spawn parallel SSH probes or @ppe-director."
        )
    elif local_verdict == "RUN_LOCAL" and vm_verdict == "RUN_LOCAL":
        action = "desktop_continue"
        note = "VM agrees RUN_LOCAL — run DESKTOP_CONTINUE.cmd --no-pause once."
    elif local_verdict and vm_verdict and local_verdict != vm_verdict:
        action = "trust_vm"
        note = f"Trust VM verdict `{vm_verdict}` over stale local `{local_verdict}`."

    return {
        "vm_phase": vm_phase or None,
        "vm_verdict": vm_verdict or None,
        "source": source,
        "wait_for_vm": wait,
        "recommended_action": action,
        "agent_note": note,
    }
