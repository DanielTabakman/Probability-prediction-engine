"""Git network mode for restricted environments (commit locally, defer push)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any


def local_git_only_enabled() -> bool:
    return os.environ.get("PPE_LOCAL_GIT_ONLY", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def git_network_mode() -> str:
    return "local_only" if local_git_only_enabled() else "normal"


def worker_git_instructions_block() -> str:
    if not local_git_only_enabled():
        return ""
    return "\n".join(
        [
            "",
            "GIT NETWORK MODE (PPE_LOCAL_GIT_ONLY):",
            "- Commit on the BUILD branch and perform LOCAL promotion (fast-forward/merge to baseline) per CODEX_AUTONOMY_V1.",
            "- Do NOT run git push or open a PR from this environment.",
            "- Remote push failure is expected and is NOT a stop condition when local promotion and tests are green.",
            "- In relay_result, set promotion.performed=true when local promotion succeeded; stop_condition=null.",
            "- Record deferred push in HANDBACK: operator will run git push from an unrestricted network later.",
            "",
        ]
    )


def try_git_push(
    repo_root: Path,
    *,
    remote: str = "origin",
    refspec: str = "HEAD",
    timeout_sec: int = 120,
) -> dict[str, Any]:
    """Attempt git push; respect PPE_LOCAL_GIT_ONLY (skip with ok=True)."""
    if local_git_only_enabled():
        return {
            "ok": True,
            "skipped": True,
            "reason": "PPE_LOCAL_GIT_ONLY set — push deferred",
        }
    cmd = ["git", "push", remote, refspec]
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"ok": False, "skipped": False, "reason": str(e), "stdout": "", "stderr": ""}
    ok = proc.returncode == 0
    return {
        "ok": ok,
        "skipped": False,
        "reason": (proc.stderr or proc.stdout or "").strip()[:500] if not ok else "",
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
        "exit_code": proc.returncode,
    }


def main() -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(description="PPE git push helper (honors PPE_LOCAL_GIT_ONLY)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--refspec", default="HEAD")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = try_git_push(args.repo_root.resolve(), remote=args.remote, refspec=args.refspec)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get("skipped"):
        print(f"git push: skipped ({result.get('reason')})")
    elif result["ok"]:
        print("git push: ok")
    else:
        print(f"git push: failed — {result.get('reason')}", file=__import__("sys").stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
