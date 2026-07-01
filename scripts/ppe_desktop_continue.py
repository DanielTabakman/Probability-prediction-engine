"""Canonical DESKTOP_CONTINUE — desktop pull + VM finish handoff (SSH)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


def run_desktop_continue(repo: Path, *, finish_timeout: int = 300) -> dict[str, Any]:
    repo = repo.resolve()
    from scripts.ppe_operator_branch_preflight import prepare_desktop_relay_pull
    from scripts.ppe_operator_git_sync import pull_main
    from scripts.ppe_operator_vm_ssh import ssh_vm, vm_finish_command, vm_status_brief_command

    desktop_prep = prepare_desktop_relay_pull(repo)
    pull = pull_main(repo)
    if not pull.get("ok", True) and not pull.get("skipped") and desktop_prep.get("ok"):
        pull = desktop_prep
    pull_ok = pull.get("ok", True) or pull.get("skipped")

    finish = ssh_vm(vm_finish_command(pull_main=True), timeout=finish_timeout)
    status = ssh_vm(vm_status_brief_command(), timeout=120)

    ok = pull_ok and bool(finish.get("ok"))
    return {
        "action": "desktop_continue",
        "ok": ok,
        "desktop_prep": desktop_prep,
        "git_pull": pull,
        "vm_finish": finish,
        "vm_status": status,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="DESKTOP_CONTINUE — pull desktop + VM finish handoff")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    print("[DESKTOP_CONTINUE] step 1/3 — git pull...")
    result = run_desktop_continue(repo)
    pull = result.get("git_pull") if isinstance(result.get("git_pull"), dict) else {}
    if pull.get("skipped"):
        print(f"  pull skipped: {pull.get('reason', 'unknown')}")
    elif pull.get("ok"):
        stdout = str(pull.get("stdout") or "").strip()
        print(f"  {stdout}" if stdout else "  ok")
    else:
        print(f"  pull failed: {pull.get('error', 'unknown')}", file=sys.stderr)

    print()
    print("[DESKTOP_CONTINUE] step 2/3 — VM finish handoff...")
    finish = result.get("vm_finish") if isinstance(result.get("vm_finish"), dict) else {}
    if finish.get("stdout"):
        print(finish["stdout"])
    if finish.get("stderr"):
        print(finish["stderr"], file=sys.stderr)
    if not finish.get("ok"):
        print(f"  VM finish exit={finish.get('exit_code')}", file=sys.stderr)

    print()
    print("[DESKTOP_CONTINUE] step 3/3 — VM status:")
    status = result.get("vm_status") if isinstance(result.get("vm_status"), dict) else {}
    print(status.get("stdout") or status.get("stderr") or "(no output)")

    if args.json:
        import json

        print(json.dumps(result, indent=2))

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
