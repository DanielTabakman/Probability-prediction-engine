"""Loop-host / VM resource health (disk, RAM) — not covered by autobuilder verdict."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HEALTH_REL = "artifacts/control_plane/VM_HOST_HEALTH.json"
DISK_WARN_GB = 5.0
DISK_CRITICAL_GB = 2.0
RAM_WARN_PCT = 15.0
RAM_CRITICAL_PCT = 8.0


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def health_path(repo: Path) -> Path:
    return (repo / HEALTH_REL).resolve()


def check_local_disk_health() -> dict[str, Any]:
    usage = shutil.disk_usage(Path.cwd().anchor or "C:\\")
    free_gb = usage.free / (1024**3)
    total_gb = usage.total / (1024**3)
    used_pct = (usage.used / usage.total * 100.0) if usage.total else 0.0
    level = "ok"
    if free_gb < DISK_CRITICAL_GB:
        level = "critical"
    elif free_gb < DISK_WARN_GB:
        level = "warn"
    return {
        "free_gb": round(free_gb, 2),
        "total_gb": round(total_gb, 2),
        "used_pct": round(used_pct, 1),
        "level": level,
    }


def check_local_ram_health() -> dict[str, Any] | None:
    if sys.platform != "win32":
        return None
    try:
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "$os=Get-CimInstance Win32_OperatingSystem;"
                    "$free=[math]::Round($os.FreePhysicalMemory/1MB,2);"
                    "$total=[math]::Round($os.TotalVisibleMemorySize/1MB,2);"
                    "$pct=[math]::Round(100*$free/$total,1);"
                    "Write-Output \"$free|$total|$pct\""
                ),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    line = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout else ""
    parts = line.split("|")
    if len(parts) != 3:
        return None
    try:
        free_gb = float(parts[0])
        total_gb = float(parts[1])
        free_pct = float(parts[2])
    except ValueError:
        return None
    level = "ok"
    if free_pct < RAM_CRITICAL_PCT:
        level = "critical"
    elif free_pct < RAM_WARN_PCT:
        level = "warn"
    return {
        "free_gb": free_gb,
        "total_gb": total_gb,
        "free_pct": free_pct,
        "level": level,
    }


def check_vm_host_health_via_ssh(repo: Path) -> dict[str, Any]:
    """Desktop: probe VM disk/RAM via SSH (run local health script on loop host)."""
    try:
        from scripts.ppe_operator_vm_ssh import VM_REPO, VM_SSH_HOST, ssh_vm
    except ImportError:
        return {"ok": False, "error": "ppe_operator_vm_ssh unavailable"}
    cmd = f"cd /d {VM_REPO} && set PYTHONPATH=%CD% && python scripts\\check_vm_host_health.py"
    try:
        ssh = ssh_vm(cmd, timeout=30)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "ssh timed out", "host": VM_SSH_HOST}
    if not ssh.get("ok"):
        return {
            "ok": False,
            "error": (ssh.get("stderr") or ssh.get("stdout") or "ssh failed").strip()[:200],
            "host": VM_SSH_HOST,
        }
    text = (ssh.get("stdout") or "").strip()
    local_payload = None
    for line in reversed(text.splitlines()):
        candidate = line.strip()
        if not candidate.startswith("{"):
            continue
        try:
            local_payload = json.loads(candidate)
            break
        except json.JSONDecodeError:
            continue
    if not isinstance(local_payload, dict):
        return {"ok": False, "error": f"unexpected ssh output: {text[:120]}", "host": VM_SSH_HOST}
    disk = local_payload.get("disk") or {}
    ram = local_payload.get("ram") or {}
    if not disk and not ram:
        return {"ok": False, "error": "no disk/ram in VM health payload", "host": VM_SSH_HOST}
    disk_level = str(disk.get("level") or "ok")
    ram_level = str(ram.get("level") or "ok")
    return {
        "ok": True,
        "host": VM_SSH_HOST,
        "disk": {
            "free_gb": disk.get("free_gb"),
            "total_gb": disk.get("total_gb"),
            "level": disk_level,
        },
        "ram": {
            "free_gb": ram.get("free_gb"),
            "total_gb": ram.get("total_gb"),
            "free_pct": ram.get("free_pct"),
            "level": ram_level,
        },
    }


def collect_host_health(repo: Path, *, via_ssh: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    payload: dict[str, Any] = {"as_of": _utc_now(), "source": "local"}
    if via_ssh:
        payload["vm_ssh"] = check_vm_host_health_via_ssh(repo)
        payload["source"] = "ssh"
    else:
        payload["disk"] = check_local_disk_health()
        ram = check_local_ram_health()
        if ram:
            payload["ram"] = ram
    alerts: list[str] = []
    if via_ssh:
        vm = payload.get("vm_ssh") if isinstance(payload.get("vm_ssh"), dict) else {}
        if not vm.get("ok"):
            alerts.append(f"vm_ssh_unreachable: {vm.get('error', 'unknown')}")
        else:
            disk = vm.get("disk") or {}
            ram = vm.get("ram") or {}
            if disk.get("level") in ("warn", "critical"):
                alerts.append(f"vm_disk_{disk['level']}: {disk.get('free_gb')}GB free")
            if ram.get("level") in ("warn", "critical"):
                alerts.append(f"vm_ram_{ram['level']}: {ram.get('free_pct')}% free")
    else:
        disk = payload.get("disk") or {}
        if disk.get("level") in ("warn", "critical"):
            alerts.append(f"disk_{disk['level']}: {disk.get('free_gb')}GB free")
        ram = payload.get("ram") or {}
        if ram.get("level") in ("warn", "critical"):
            alerts.append(f"ram_{ram['level']}: {ram.get('free_pct')}% free")
    payload["alerts"] = alerts
    payload["healthy"] = not alerts
    return payload


def write_host_health(repo: Path, payload: dict[str, Any]) -> Path:
    path = health_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def load_host_health(repo: Path) -> dict[str, Any] | None:
    path = health_path(repo)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check loop-host / VM disk and RAM health")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--ssh", action="store_true", help="Probe VM via SSH (desktop)")
    ap.add_argument("--write", action="store_true", help="Write artifacts/control_plane/VM_HOST_HEALTH.json")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    os.environ.setdefault("PPE_REPO_ROOT", str(repo))
    payload = collect_host_health(repo, via_ssh=bool(args.ssh))
    if args.write:
        write_host_health(repo, payload)
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("healthy", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
