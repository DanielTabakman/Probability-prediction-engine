"""Headless auto-loop entry (no cmd.exe). Mirrors run_ppe_auto_loop.cmd for VM supervisors."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _hidden_flags() -> int:
    from scripts.ppe_remote_agent_spawn import _win32_hidden_flags

    return _win32_hidden_flags()


def _run_script(repo: Path, env: dict[str, str], script: str, *args: str) -> int:
    cmd = [sys.executable, str(repo / "scripts" / script), *args]
    kwargs: dict = {"cwd": repo, "env": env, "check": False}
    if sys.platform == "win32":
        kwargs["creationflags"] = _hidden_flags()
    return int(subprocess.run(cmd, **kwargs).returncode)


def _sleep(repo: Path, env: dict[str, str], seconds: int) -> int:
    cmd = [sys.executable, str(repo / "scripts" / "ppe_loop_sleep.py"), str(max(1, seconds))]
    kwargs: dict = {"cwd": repo, "env": env, "check": False}
    if sys.platform == "win32":
        kwargs["creationflags"] = _hidden_flags()
    return int(subprocess.run(cmd, **kwargs).returncode)


def _guard_sleep_seconds(repo: Path, env: dict[str, str]) -> int:
    cmd = [sys.executable, str(repo / "scripts" / "ppe_loop_guard_stop.py"), "--repo-root", str(repo)]
    kwargs: dict = {"cwd": repo, "env": env, "capture_output": True, "text": True, "check": False}
    if sys.platform == "win32":
        kwargs["creationflags"] = _hidden_flags()
    proc = subprocess.run(cmd, **kwargs)
    if proc.returncode != 0:
        return 120
    raw = (proc.stdout or "").strip()
    if raw == "-1":
        return -1
    try:
        return max(1, int(raw))
    except ValueError:
        return 120


def _run_auto(repo: Path, env: dict[str, str]) -> int:
    from scripts.ppe_operator_config import continuous_max

    max_ch = continuous_max(repo)
    rc = _run_script(repo, env, "ppe_auto_select.py", "--repo-root", str(repo), "--apply")
    if rc != 0:
        return rc
    return _run_script(
        repo,
        env,
        "ppe_run.py",
        "--repo-root",
        str(repo),
        "--continuous",
        "--continuous-max",
        str(max_ch),
    )


def _git_sync(repo: Path, env: dict[str, str]) -> int:
    for step in ("--pull", "--auto-publish", "--check-merge", "--retarget-stacked"):
        rc = _run_script(repo, env, "ppe_operator_git_sync.py", "--repo-root", str(repo), step)
        if rc != 0:
            return rc
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Headless auto-loop entry")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    env.setdefault("PPE_OPERATOR_PROFILE", "local")
    env.setdefault("PPE_SKIP_ACP", "1")
    env.setdefault("PPE_WORKER_MODE", "deterministic")
    env.setdefault("PPE_STACK_HEADLESS", "1")
    env["PPE_HEADLESS_SUPERVISED_LOOP"] = "1"

    if _run_script(repo, env, "ppe_operator_env.py") != 0:
        return 1
    if _run_script(repo, env, "ppe_loop_host_guard.py", "--require") != 0:
        return _run_script(repo, env, "ppe_loop_host_guard.py", "--require")

    from scripts.ppe_operator_config import idle_sleep_seconds

    idle_sleep = idle_sleep_seconds(repo)

    if _run_script(repo, env, "ppe_loop_singleton.py", "--repo-root", str(repo)) != 0:
        print("ppe_headless_auto_loop_entry: another loop instance is already running", file=sys.stderr)
        return 1

    if _run_script(repo, env, "run_codebase_health_gate.py", "--repo-root", str(repo), "--skip-relay") != 0:
        return 1

    preflight = _run_script(repo, env, "ppe_operator_status.py", "--repo-root", str(repo))
    while preflight == 7:
        rc = _guard_stop(repo, env, idle_sleep)
        if rc != 0:
            return rc
        preflight = _run_script(repo, env, "ppe_operator_status.py", "--repo-root", str(repo))
    if preflight != 0:
        return preflight

    rc = _git_sync(repo, env)
    if rc != 0:
        return rc

    while True:
        rc = _git_sync(repo, env)
        if rc != 0:
            return rc
        rc = _run_script(repo, env, "ppe_post_build_watcher.py", "--repo-root", str(repo))
        if rc != 0:
            return rc
        _run_script(repo, env, "ppe_autobuilder.py", "--repo-root", str(repo), "status", "--write", "--brief")
        status_rc = _run_script(
            repo,
            env,
            "ppe_operator_status.py",
            "--repo-root",
            str(repo),
            "--brief",
            "--no-write",
        )
        if status_rc == 7:
            guard_rc = _guard_stop(repo, env, idle_sleep)
            if guard_rc != 0:
                return guard_rc
            continue
        pass_rc = _run_script(repo, env, "ppe_operator_loop_pass.py", "--repo-root", str(repo))
        if pass_rc == 7:
            guard_rc = _guard_stop(repo, env, idle_sleep)
            if guard_rc != 0:
                return guard_rc
            continue
        if pass_rc == 8:
            if _sleep(repo, env, idle_sleep) != 0:
                return _sleep(repo, env, idle_sleep)
            continue
        if pass_rc != 0:
            return pass_rc

        auto_rc = _run_auto(repo, env)
        if auto_rc == 7:
            guard_rc = _guard_stop(repo, env, idle_sleep)
            if guard_rc != 0:
                return guard_rc
            continue
        if auto_rc != 0:
            return auto_rc
        if _sleep(repo, env, idle_sleep) != 0:
            return _sleep(repo, env, idle_sleep)


def _guard_stop(repo: Path, env: dict[str, str], default_sleep: int) -> int:
    _run_script(repo, env, "ppe_operator_status.py", "--repo-root", str(repo), "--notify")
    sleep_sec = _guard_sleep_seconds(repo, env)
    if sleep_sec == -1:
        return 7
    if _sleep(repo, env, sleep_sec if sleep_sec > 0 else default_sleep) != 0:
        return _sleep(repo, env, sleep_sec if sleep_sec > 0 else default_sleep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
