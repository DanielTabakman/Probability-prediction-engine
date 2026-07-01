"""Desktop DESKTOP_CONTINUE — git pull, VM handoff, status (proper exit codes)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from scripts.ppe_operator_vm_ssh import (
    VM_REPO,
    fetch_vm_brief,
    ssh_vm,
    vm_finish_command,
    vm_status_brief_command,
)


def _git_pull(repo: Path) -> int:
    proc = subprocess.run(
        ["git", "pull", "origin", "main"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "git pull failed").strip()
        print(f"[DESKTOP_CONTINUE] git pull failed: {err}", file=sys.stderr)
    return proc.returncode


def run_desktop_continue(repo: Path) -> int:
    repo = repo.resolve()
    print("[DESKTOP_CONTINUE] step 1/3 — git pull...")
    pull_rc = _git_pull(repo)
    if pull_rc != 0:
        return pull_rc

    print()
    print("[DESKTOP_CONTINUE] step 2/3 — mark product ready + start relay on VM...")
    print("           (via SSH to ppe-vm)")
    print()

    handoff = ssh_vm(vm_finish_command(pull_main=True), timeout=120)
    handoff_rc = int(handoff.get("exit_code") or 1)
    if handoff.get("stdout"):
        print(handoff["stdout"])
    if handoff.get("stderr"):
        print(handoff["stderr"], file=sys.stderr)
    if handoff_rc != 0:
        print(
            f"[DESKTOP_CONTINUE] VM handoff failed (exit={handoff_rc})",
            file=sys.stderr,
        )

    print()
    print("[DESKTOP_CONTINUE] step 3/3 — VM status:")
    brief = fetch_vm_brief(repo, use_cache=False, timeout=90, write_cache=True)
    stdout = str(brief.get("stdout") or "").strip()
    if stdout:
        print(stdout)
    elif brief.get("error"):
        print(brief["error"], file=sys.stderr)

    print()
    print("=" * 60)
    if handoff_rc == 0:
        print(" Done. VM loop should advance past IDE_BUILD.")
    else:
        print(" Handoff failed — see stderr above. Status refreshed for triage.")
    print("=" * 60)
    print()

    return handoff_rc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Desktop continue after IDE BUILD merge")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    _ = VM_REPO  # canonical path documented in vm_ssh module
    return run_desktop_continue(args.repo_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
