"""
Start an isolated BUILD pass: new branch + git worktree from a baseline ref.

Stdlib only. Intended as a small trial shell (Frontier Steward).

  python scripts/frontier_start_pass.py --plane EVIDENCE-PLANE --step BUILD \\
    --slice my-slice --baseline recovery/frontier-steward-v2_1-baseline
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import secrets
import shlex
import subprocess
import sys
from pathlib import Path


KNOWN_PLANES = frozenset({"CONTROL-PLANE", "PRODUCT-PLANE", "EVIDENCE-PLANE"})


def _run_git(repo: Path, args: list[str]) -> tuple[str, str, int]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    return out, err, int(proc.returncode)


def _repo_root(start: Path) -> Path | None:
    out, _, code = _run_git(start, ["rev-parse", "--show-toplevel"])
    if code != 0 or not out:
        return None
    return Path(out)


def _slug_segment(s: str, max_len: int = 40) -> str:
    s2 = s.strip().lower().replace(" ", "-")
    s2 = re.sub(r"[^a-z0-9._-]+", "-", s2)
    s2 = re.sub(r"-{2,}", "-", s2).strip("-._")
    if not s2:
        s2 = "slice"
    return s2[:max_len].rstrip("-._")


def _safe_dir_stem(name: str, max_len: int = 48) -> str:
    t = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip())
    t = re.sub(r"-{2,}", "-", t).strip("-._")
    if not t:
        t = "repo"
    return t[:max_len].rstrip("-._")


def _today_tag() -> str:
    return _dt.date.today().strftime("%Y%m%d")


def _branch_name(plane: str, step: str, slice_label: str) -> str:
    p = _slug_segment(plane, 24)
    st = _slug_segment(step, 12)
    sl = _slug_segment(slice_label, 32)
    rid = secrets.token_hex(2)
    return f"fs-pass/{p}/{st}/{sl}-{_today_tag()}-{rid}"


def _default_worktree_path(repo: Path, branch_leaf: str) -> Path:
    # branch_leaf: last segment of branch for a shorter directory name hint
    leaf = branch_leaf.split("/")[-1] if "/" in branch_leaf else branch_leaf
    stem = _safe_dir_stem(repo.name)
    return repo.parent / f"{stem}.frontier-pass.{_slug_segment(leaf, 56)}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Create a short-lived execution branch + worktree from a baseline."
    )
    ap.add_argument(
        "--plane",
        required=True,
        help="Plane label (e.g. EVIDENCE-PLANE). Used in branch/path naming.",
    )
    ap.add_argument(
        "--step",
        default="BUILD",
        help="Execution step type (default: BUILD).",
    )
    ap.add_argument(
        "--slice",
        required=True,
        metavar="LABEL",
        help="Short slice label / name (slugified for branch and directory).",
    )
    ap.add_argument(
        "--baseline",
        default="recovery/frontier-steward-v2_1-baseline",
        help="Baseline ref to branch from (default: recovery/frontier-steward-v2_1-baseline).",
    )
    ap.add_argument(
        "--worktree-path",
        default="",
        help="Explicit worktree directory (default: sibling of repo root).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned git commands and exit without changing state.",
    )
    ap.add_argument(
        "--no-preflight",
        action="store_true",
        help="Do not run scripts/frontier_preflight.py in the new worktree.",
    )
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    repo = _repo_root(Path.cwd())
    if repo is None:
        repo = _repo_root(here.parent)
    if repo is None:
        print("ERROR: not a git repository (could not resolve repo root).", file=sys.stderr)
        return 2

    plane = args.plane.strip()
    step = args.step.strip()
    sl = args.slice.strip()
    baseline = args.baseline.strip()
    if not plane or not step or not sl or not baseline:
        print("ERROR: --plane, --step, --slice, and --baseline must be non-empty.", file=sys.stderr)
        return 2

    if plane not in KNOWN_PLANES:
        print(
            f"NOTE: plane {plane!r} is not in {sorted(KNOWN_PLANES)}; naming will still proceed.",
            file=sys.stderr,
        )

    branch = _branch_name(plane, step, sl)
    wt_path = Path(args.worktree_path) if args.worktree_path else _default_worktree_path(repo, branch)

    verify_out, verify_err, vcode = _run_git(repo, ["rev-parse", "--verify", f"{baseline}^{{commit}}"])
    if vcode != 0:
        print(f"ERROR: baseline not a valid commit-ish: {baseline}", file=sys.stderr)
        if verify_err:
            print(verify_err, file=sys.stderr)
        return 3

    cmds = [
        ["git", "worktree", "add", "-b", str(branch), str(wt_path), baseline],
    ]

    if args.dry_run:
        print("=== FRONTIER START PASS (dry-run) ===")
        print(f"repo_root: {repo}")
        print(f"baseline_commit: {verify_out}")
        print(f"planned_branch: {branch}")
        print(f"planned_worktree: {wt_path}")
        print("commands:")
        for c in cmds:
            print(" ", subprocess.list2cmdline(c))
        if not args.no_preflight:
            print(f"  cd {shlex.quote(str(wt_path))}")
            print(f"  {sys.executable} scripts/frontier_preflight.py")
        print("=== END (no changes) ===")
        return 0

    if wt_path.exists():
        print(f"ERROR: worktree path already exists: {wt_path}", file=sys.stderr)
        return 4

    out, err, code = _run_git(repo, ["worktree", "add", "-b", branch, str(wt_path), baseline])
    if code != 0:
        print("ERROR: git worktree add failed.", file=sys.stderr)
        if err:
            print(err, file=sys.stderr)
        if out:
            print(out, file=sys.stderr)
        return 5

    wt = wt_path.resolve()
    anchor = repo.resolve()
    print("=== FRONTIER START PASS (created) ===", flush=True)
    print(f"execution_branch: {branch}", flush=True)
    print(f"execution_path:   {wt}", flush=True)
    print(f"baseline_used:    {baseline} ({verify_out})", flush=True)
    print(f"repo_anchor:      {anchor}", flush=True)
    print(flush=True)
    print("--- enter / use this worktree ---", flush=True)
    print(f"cd {shlex.quote(str(wt))}", flush=True)
    print(flush=True)
    print("--- preflight (also run anytime) ---", flush=True)
    print(f"cd {shlex.quote(str(wt))}", flush=True)
    print(f"{sys.executable} scripts/frontier_preflight.py", flush=True)
    print(flush=True)
    print("--- cleanup (after slice closeout) ---", flush=True)
    print(f"git -C {shlex.quote(str(anchor))} worktree remove {shlex.quote(str(wt))}", flush=True)
    print(
        f"# if remove is refused (dirty tree): git -C {shlex.quote(str(anchor))} "
        f"worktree remove --force {shlex.quote(str(wt))}",
        flush=True,
    )
    print(f"git -C {shlex.quote(str(anchor))} branch -D {shlex.quote(branch)}", flush=True)
    print("=== END ===", flush=True)
    print(flush=True)

    preflight_rc = 0
    if not args.no_preflight:
        pf = wt_path / "scripts" / "frontier_preflight.py"
        if not pf.is_file():
            print(f"WARNING: preflight script missing at {pf}", file=sys.stderr)
        else:
            print("--- preflight (live run) ---", flush=True)
            proc = subprocess.run(
                [sys.executable, str(pf)],
                cwd=wt_path,
                text=True,
            )
            preflight_rc = int(proc.returncode)

    return preflight_rc if preflight_rc != 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
