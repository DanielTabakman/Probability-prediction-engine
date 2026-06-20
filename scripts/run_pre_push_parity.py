"""Local pre-push parity with GitHub CI (pytest job + optional docker_entrypoint).

Canonical before ``git push`` when you want CI-equivalent checks locally.
See docs/SOP/COMMIT_POLICY.md and docs/SOP/TESTING_TIERS_V1.md.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_IMAGE = "ppe-local:pre-push"
HEALTH_URL = "http://127.0.0.1:8501/_stcore/health"
IMPORT_CHECK = r"""
import importlib.util
import sys
from pathlib import Path

root = Path('/app')
viz = root / 'src' / 'viz'
app = viz / 'app.py'

sys.path = [str(viz)] + [
    p for p in sys.path
    if p and Path(p).resolve() != root.resolve()
]

spec = importlib.util.spec_from_file_location('ppe_docker_entry', app)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load app entry spec')

mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if Path(mod.ROOT).resolve() != root.resolve():
    raise AssertionError(f'ROOT={mod.ROOT!r} != {root!r}')
"""


def _run(cmd: list[str], *, cwd: Path) -> int:
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode


def _docker_available() -> bool:
    proc = subprocess.run(
        ["docker", "version"],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def run_pushable_gate(repo: Path) -> int:
    from scripts.run_pushable_gate import main as gate_main

    return gate_main(["--repo-root", str(repo), "--pre-push"])


def run_docker_entrypoint_smoke(repo: Path, *, image: str = DEFAULT_IMAGE) -> int:
    if not _docker_available():
        print("ERROR: docker is not available; install Docker or omit --docker", file=sys.stderr)
        return 1

    rc = _run(["docker", "build", "-t", image, "."], cwd=repo)
    if rc != 0:
        return rc

    rc = _run(
        ["docker", "run", "--rm", image, "python", "-c", IMPORT_CHECK.strip()],
        cwd=repo,
    )
    if rc != 0:
        return rc

    proc = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "-p",
            "8501:8501",
            image,
            "streamlit",
            "run",
            "src/viz/app.py",
            "--server.headless",
            "true",
            "--server.port",
            "8501",
            "--server.address",
            "0.0.0.0",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode

    container_id = proc.stdout.strip()
    if not container_id:
        print("ERROR: docker run did not return a container id", file=sys.stderr)
        return 1

    try:
        for attempt in range(1, 31):
            logs = subprocess.run(
                ["docker", "logs", container_id],
                capture_output=True,
                text=True,
            )
            combined = (logs.stdout or "") + (logs.stderr or "")
            if "ModuleNotFoundError" in combined:
                print("ModuleNotFoundError during Streamlit startup:", file=sys.stderr)
                print(combined, file=sys.stderr)
                return 1

            try:
                with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
                    if 200 <= resp.status < 300:
                        print(f"Streamlit healthy after {attempt} attempt(s)")
                        return 0
            except (urllib.error.URLError, TimeoutError):
                pass

            time.sleep(2)

        print("Streamlit did not become healthy within 60s:", file=sys.stderr)
        tail = subprocess.run(
            ["docker", "logs", container_id],
            capture_output=True,
            text=True,
        )
        print((tail.stdout or tail.stderr or "")[-4000:], file=sys.stderr)
        return 1
    finally:
        subprocess.run(["docker", "stop", container_id], capture_output=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run local checks that mirror CI before git push.",
    )
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument(
        "--docker",
        action="store_true",
        help="Also run CI docker_entrypoint smoke (build, import, Streamlit health)",
    )
    ap.add_argument(
        "--skip-gate",
        action="store_true",
        help="Skip run_pushable_gate --pre-push (docker-only)",
    )
    ap.add_argument(
        "--image",
        default=DEFAULT_IMAGE,
        help=f"Docker image tag for --docker (default: {DEFAULT_IMAGE})",
    )
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    if not args.skip_gate:
        rc = run_pushable_gate(repo)
        if rc != 0:
            return rc

    if args.docker:
        return run_docker_entrypoint_smoke(repo, image=args.image)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
