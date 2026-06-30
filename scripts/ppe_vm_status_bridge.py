"""Merge VM autobuilder status when desktop local OPERATOR_STATUS is stale."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

VM_SSH_HOST = "ppeloop@desktop-caqll8k"
VM_REPO = r"C:\Users\ppeloop\Probability-prediction-engine"
VM_FETCH_TIMEOUT_SEC = 25

# When VM verdict is "ahead" of local on desktop, prefer VM for agent routing.
_AHEAD_VERDICTS = frozenset({"IDE_BUILD", "RUN_LOCAL", "RUN_AUTO"})


def vm_bridge_enabled(*, loop_host_allowed: bool | None = None) -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    if os.environ.get("PPE_VM_STATUS_BRIDGE", "").strip().lower() in ("0", "false", "no", "off"):
        return False
    if loop_host_allowed is None:
        try:
            from scripts.ppe_chapter_mode import is_loop_host_allowed

            loop_host_allowed = is_loop_host_allowed()
        except Exception:
            loop_host_allowed = False
    return not bool(loop_host_allowed)


def parse_status_brief(line: str) -> dict[str, Any]:
    """Parse `PHASE=… VERDICT=… slice=…` autobuilder brief line."""
    out: dict[str, Any] = {}
    text = (line or "").strip()
    if not text:
        return out
    for key in ("PHASE", "VERDICT"):
        match = re.search(rf"{key}=([^\s]+)", text)
        if match:
            out[key.lower()] = match.group(1)
    slice_match = re.search(r"slice=([^\s]+)", text)
    if slice_match:
        out["slice_id"] = slice_match.group(1)
    loop_match = re.search(r"stack_loop=([^\s]+)", text)
    if loop_match:
        out["stack_loop"] = loop_match.group(1)
    return out


def fetch_vm_autobuilder_status(
    *,
    ssh_host: str = VM_SSH_HOST,
    vm_repo: str = VM_REPO,
    timeout_sec: int = VM_FETCH_TIMEOUT_SEC,
) -> dict[str, Any]:
    """SSH to loop host and return autobuilder status JSON (empty on failure)."""
    cmd = (
        f"cd /d {vm_repo} && set PYTHONPATH={vm_repo} && "
        r"python scripts\ppe_autobuilder.py status --json"
    )
    try:
        proc = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", ssh_host, cmd],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        return {"ok": False, "error": err or f"ssh exit {proc.returncode}"}

    raw = (proc.stdout or "").strip()
    if not raw:
        return {"ok": False, "error": "empty vm status output"}

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        brief = parse_status_brief(raw.splitlines()[0] if raw else "")
        if brief.get("verdict"):
            return {"ok": True, "brief": brief, "source": "brief_fallback"}
        return {"ok": False, "error": f"json parse failed: {exc}"}

    if not isinstance(data, dict):
        return {"ok": False, "error": "vm status not a dict"}
    return {"ok": True, "status": data, "source": "json"}


def _vm_verdict_from_fetch(fetch: dict[str, Any]) -> str:
    if not fetch.get("ok"):
        return ""
    status = fetch.get("status")
    if isinstance(status, dict):
        return str(status.get("verdict") or "").strip().upper()
    brief = fetch.get("brief")
    if isinstance(brief, dict):
        return str(brief.get("verdict") or "").strip().upper()
    return ""


def should_trust_vm_over_local(
    *,
    local_verdict: str,
    vm_verdict: str,
    preflight_warnings: list[str] | None = None,
) -> bool:
    local = str(local_verdict or "").strip().upper()
    vm = str(vm_verdict or "").strip().upper()
    if not vm or local == vm:
        return False
    if vm not in _AHEAD_VERDICTS:
        return False
    if local in ("ERROR", "FIX_PLAN", "STALE_STATE"):
        return False
    if vm == "IDE_BUILD" and local in ("RUN_LOCAL", "SUPPLY_LOW", "RUN_AUTO"):
        return True
    if vm == "RUN_LOCAL" and local in ("SUPPLY_LOW", "RUN_AUTO"):
        return True
    if vm == "RUN_AUTO" and local == "SUPPLY_LOW":
        return True
    if preflight_warnings and vm in _AHEAD_VERDICTS:
        return True
    return False


def _vm_payload_fields(fetch: dict[str, Any]) -> dict[str, Any]:
    status = fetch.get("status")
    if isinstance(status, dict):
        build = status.get("build") if isinstance(status.get("build"), dict) else {}
        operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
        return {
            "verdict": str(status.get("verdict") or "").upper(),
            "phase": status.get("phase"),
            "blocker": status.get("blocker"),
            "slice_id": build.get("slice_id"),
            "plan_path": build.get("plan_path") or operator.get("phase_plan_path"),
            "chapter_name": operator.get("chapter_name"),
            "brief": None,
        }
    brief = fetch.get("brief") if isinstance(fetch.get("brief"), dict) else {}
    return {
        "verdict": str(brief.get("verdict") or "").upper(),
        "phase": brief.get("phase"),
        "blocker": None,
        "slice_id": brief.get("slice_id"),
        "plan_path": None,
        "chapter_name": None,
        "brief": brief,
    }


def apply_vm_authoritative(
    status: dict[str, Any],
    *,
    loop_host_allowed: bool,
    repo: Path | None = None,
) -> dict[str, Any]:
    """When desktop local status lags VM, overlay VM verdict for agent routing."""
    if not vm_bridge_enabled(loop_host_allowed=loop_host_allowed):
        return status

    fetch = fetch_vm_autobuilder_status()
    vm_fields = _vm_payload_fields(fetch) if fetch.get("ok") else {}
    vm_verdict = vm_fields.get("verdict") or _vm_verdict_from_fetch(fetch)
    local_verdict = str(status.get("verdict") or "").upper()
    warnings = status.get("preflight_warnings") or []

    status["vm_status_fetch"] = {
        "ok": bool(fetch.get("ok")),
        "source": fetch.get("source"),
        "error": fetch.get("error"),
    }

    if not should_trust_vm_over_local(
        local_verdict=local_verdict,
        vm_verdict=vm_verdict,
        preflight_warnings=warnings if isinstance(warnings, list) else [],
    ):
        return status

    out = dict(status)
    out["local_verdict"] = local_verdict
    out["verdict"] = vm_verdict
    out["vm_authoritative"] = True
    out["vm_status"] = vm_fields

    if vm_fields.get("blocker"):
        out["blocker"] = vm_fields["blocker"]
    if vm_fields.get("chapter_name"):
        out["chapter_name"] = vm_fields["chapter_name"]
    if vm_fields.get("plan_path"):
        out["phase_plan_path"] = vm_fields["plan_path"]

    try:
        from scripts.ppe_chapter_mode import resolve_chapter_mode, resolve_operator_commands

        root = (repo or Path.cwd()).resolve()
        chapter_mode = resolve_chapter_mode(
            root,
            verdict=vm_verdict,
            plan_path=str(vm_fields.get("plan_path") or out.get("phase_plan_path") or "") or None,
            guard_reason=(out.get("guard") or {}).get("reason"),
            chapter_name=str(vm_fields.get("chapter_name") or out.get("chapter_name") or "") or None,
        )
        commands, avoid = resolve_operator_commands(
            verdict=vm_verdict,
            chapter_mode=chapter_mode,
            loop_host_allowed=loop_host_allowed,
        )
        out["chapter_mode"] = chapter_mode
        out["commands"] = commands
        out["avoid"] = avoid
    except Exception:
        pass

    return out
