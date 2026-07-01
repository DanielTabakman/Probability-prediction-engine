"""Desktop → VM live status: check loop health; auto-ensure stack when down."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scripts.ppe_operator_vm_ssh import SSH_ARGS, VM_REPO, VM_SSH_HOST, ssh_vm

_PHASE_RE = re.compile(r"PHASE=(?P<phase>\S+).*stack_loop=(?P<loop>\S+)")


def _vm_cmd(inner: str) -> str:
    return f"cd /d {VM_REPO} && call call_ppe_operator_local.cmd && {inner}"


def _needs_ensure(stdout: str) -> bool:
    if "stack_loop=False" in stdout or "PHASE=STACK_DOWN" in stdout:
        return True
    m = _PHASE_RE.search(stdout or "")
    return bool(m and m.group("loop") == "False")


def fetch_vm_loop_status(*, ensure_if_down: bool = True, timeout: int = 120) -> dict:
    brief = ssh_vm(_vm_cmd("call check_vm_loop.cmd --no-pause"), timeout=timeout)
    stdout = str(brief.get("stdout") or "")
    ensured = False
    if ensure_if_down and brief.get("ok") and _needs_ensure(stdout):
        ensure = ssh_vm(_vm_cmd("run_ppe_headless_stack.cmd --ensure"), timeout=timeout)
        ensured = bool(ensure.get("ok"))
        brief = ssh_vm(_vm_cmd("call check_vm_loop.cmd --no-pause"), timeout=timeout)
        stdout = str(brief.get("stdout") or "")
    return {
        "ok": brief.get("ok"),
        "stdout": stdout,
        "stderr": brief.get("stderr"),
        "exit_code": brief.get("exit_code"),
        "auto_ensured_stack": ensured,
        "host": VM_SSH_HOST,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Desktop: SSH to VM for live loop status")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--no-ensure", action="store_true", help="Do not auto-start stack when down")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    _ = args.repo_root.resolve()

    report = fetch_vm_loop_status(ensure_if_down=not args.no_ensure)
    if args.json:
        import json

        print(json.dumps(report, indent=2))
    else:
        if report.get("auto_ensured_stack"):
            print("[DESKTOP_VM_STATUS] stack was down — ran run_ppe_headless_stack --ensure")
        out = (report.get("stdout") or "").strip()
        if out:
            print(out)
        elif report.get("stderr"):
            print(report["stderr"], file=sys.stderr)
        if not _PHASE_RE.search(out):
            print(
                "[DESKTOP_VM_STATUS] WARN: no PHASE= line — loop may be stopped. "
                f"SSH host={VM_SSH_HOST} args={' '.join(SSH_ARGS)}",
                file=sys.stderr,
            )
    ok = bool(report.get("ok")) and bool(_PHASE_RE.search(str(report.get("stdout") or "")))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
