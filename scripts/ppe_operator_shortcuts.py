"""Install operator Desktop shortcuts on the correct machine (VM vs daily PC)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_REL = "artifacts/orchestrator/OPERATOR_SHORTCUTS_STATE.json"

VM_SHORTCUTS: dict[str, str | None] = {
    "PPE Operator Folder": None,
    "DO THE THING": "DO_THE_THING.cmd",
    "VM STATUS": "VM_STATUS.cmd",
    "VM STOP": "VM_STOP.cmd",
    "VM START": "VM_START.cmd",
    "VM RESTART": "VM_RESTART.cmd",
    "VM AUTO": "VM_AUTO.cmd",
    "VM UPDATE": "VM_UPDATE.cmd",
}

BUTTON_NAME = "DO THE THING"

DESKTOP_SHORTCUTS: dict[str, str | None] = {
    "PPE Repo (Desktop)": None,
    "DO THE THING": "DO_THE_THING.cmd",
    "DESKTOP BUILD": "DESKTOP_BUILD.cmd",
    "DESKTOP CONTINUE": "DESKTOP_CONTINUE.cmd",
    "DESKTOP VM MAINTAIN": "DESKTOP_VM_MAINTAIN.cmd",
    "SETUP VM CODEX": "setup_vm_codex.cmd",
    "SETUP VM CODEX LOGIN": "setup_vm_codex_login.cmd",
    "DESKTOP ZERO CLICK START": "DESKTOP_ZERO_CLICK_START.cmd",
    "DESKTOP ZERO CLICK STOP": "DESKTOP_ZERO_CLICK_STOP.cmd",
    "DESKTOP STOP": "DESKTOP_STOP.cmd",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_path(repo: Path) -> Path:
    return (repo / STATE_REL).resolve()


def load_state(repo: Path) -> dict[str, Any]:
    path = state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(repo: Path, data: dict[str, Any]) -> None:
    path = state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = _utc_now()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def desktop_dir() -> Path:
    desk = os.environ.get("USERPROFILE", "")
    if desk:
        candidate = Path(desk) / "Desktop"
        if candidate.is_dir():
            return candidate
    return Path.home() / "Desktop"


def detect_role(repo: Path) -> str:
    """Return vm_loop_host | daily_driver | unknown."""
    repo = repo.resolve()
    loop_host = repo / "ppe_operator_loop_host.local.cmd"
    no_loop = repo / "ppe_operator_no_loop.local.cmd"

    if loop_host.is_file() and not no_loop.is_file():
        return "vm_loop_host"
    if no_loop.is_file():
        return "daily_driver"

    env_host = os.environ.get("PPE_LOOP_HOST", "").strip() == "1"
    env_forbidden = os.environ.get("PPE_STACK_FORBIDDEN", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if env_host and not env_forbidden:
        return "vm_loop_host"
    if env_forbidden:
        return "daily_driver"
    return "unknown"


def shortcuts_for_role(role: str) -> dict[str, str | None]:
    if role == "vm_loop_host":
        return VM_SHORTCUTS
    if role == "daily_driver":
        return DESKTOP_SHORTCUTS
    return {}


def _shortcut_path(desk: Path, name: str) -> Path:
    return desk / f"{name}.lnk"


def shortcuts_need_refresh(repo: Path, role: str, *, force: bool = False) -> bool:
    if force or role == "unknown":
        return role != "unknown"
    repo = repo.resolve()
    desk = desktop_dir()
    mapping = shortcuts_for_role(role)
    if not mapping:
        return False

    for name, script in mapping.items():
        lnk = _shortcut_path(desk, name)
        if not lnk.is_file():
            return True
        if script:
            script_path = repo / script
            if script_path.is_file() and script_path.stat().st_mtime > lnk.stat().st_mtime:
                return True

    state = load_state(repo)
    if str(state.get("repoRoot") or "") != str(repo):
        return True
    if str(state.get("role") or "") != role:
        return True
    return False


def _ps_escape(value: str) -> str:
    return value.replace("'", "''")


def install_shortcuts(repo: Path, role: str) -> dict[str, Any]:
    repo = repo.resolve()
    mapping = shortcuts_for_role(role)
    if not mapping:
        return {"ok": False, "reason": f"unknown role on this machine (role={role})"}

    folder_name = "PPE Operator Folder" if role == "vm_loop_host" else "PPE Repo (Desktop)"
    desk = desktop_dir()
    desk.mkdir(parents=True, exist_ok=True)

    def _mk_shortcut(name: str, target: Path) -> None:
        ps = (
            "$s = New-Object -ComObject WScript.Shell; "
            f"$l = $s.CreateShortcut('{_ps_escape(str(desk / (name + '.lnk')))}'); "
            f"$l.TargetPath = '{_ps_escape(str(target))}'; "
            f"$l.WorkingDirectory = '{_ps_escape(str(repo))}'; "
            "$l.Save()"
        )
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()
            raise RuntimeError(err or f"powershell exit {proc.returncode}")

    try:
        _mk_shortcut(folder_name, repo)
        for name, script in mapping.items():
            if script is None:
                continue
            script_path = repo / script
            if not script_path.is_file():
                raise FileNotFoundError(f"missing {script}")
            _mk_shortcut(name, script_path)
    except (OSError, RuntimeError) as exc:
        return {"ok": False, "reason": str(exc)}

    created = list(mapping.keys())
    save_state(
        repo,
        {
            "repoRoot": str(repo),
            "role": role,
            "desktop": str(desk),
            "shortcuts": created,
        },
    )
    return {"ok": True, "role": role, "desktop": str(desk), "shortcuts": created}


def ensure_shortcuts(repo: Path, *, force: bool = False, quiet: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    role = detect_role(repo)
    if role == "unknown":
        result = {"ok": False, "skipped": True, "reason": "unknown machine role (no loop-host / no-loop local cmd)"}
        if not quiet:
            print(f"ppe_operator_shortcuts: {result['reason']}", file=sys.stderr)
        return result

    if not force and not shortcuts_need_refresh(repo, role):
        result = {"ok": True, "skipped": True, "role": role, "reason": "shortcuts up to date"}
        if not quiet:
            print(f"ppe_operator_shortcuts: {role} shortcuts already current")
        return result

    result = install_shortcuts(repo, role)
    if not quiet:
        if result.get("ok"):
            names = ", ".join(result.get("shortcuts") or [])
            print(f"ppe_operator_shortcuts: installed {result.get('role')} shortcuts -> {result.get('desktop')}")
            print(f"  {names}")
        else:
            print(f"ppe_operator_shortcuts: failed — {result.get('reason')}", file=sys.stderr)
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Install PPE operator Desktop shortcuts when appropriate")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--apply", action="store_true", help="Install or refresh shortcuts when needed")
    ap.add_argument("--force", action="store_true", help="Recreate shortcuts even if current")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.apply or args.force:
        result = ensure_shortcuts(repo, force=args.force, quiet=args.quiet or args.json)
    else:
        role = detect_role(repo)
        result = {
            "role": role,
            "needs_refresh": shortcuts_need_refresh(repo, role, force=False),
            "desktop": str(desktop_dir()),
        }

    if args.json:
        print(json.dumps(result, indent=2))
    if result.get("ok") is False and not result.get("skipped"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
