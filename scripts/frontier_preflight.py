"""
Machine-generated repo-state summary for BUILD preflight (Frontier Steward).

Stdlib only. Run from anywhere inside the repo (uses git to find root):

  python scripts/frontier_preflight.py
  python scripts/frontier_preflight.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


KNOWN_PLANES = frozenset({"CONTROL-PLANE", "PRODUCT-PLANE", "EVIDENCE-PLANE"})


def _run_git(repo: Path, args: list[str]) -> tuple[str, int]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    out = (proc.stdout or "").strip()
    return out, int(proc.returncode)


def _repo_root(start: Path) -> Path | None:
    out, code = _run_git(start, ["rev-parse", "--show-toplevel"])
    if code != 0 or not out:
        return None
    return Path(out)


def _classify_path(rel: str) -> str:
    p = rel.replace("\\", "/").lstrip("./")
    if p.startswith("docs/SOP/"):
        return "CONTROL-PLANE"
    if p.startswith("src/"):
        return "PRODUCT-PLANE"
    if p.startswith("tests/") or p.startswith("scripts/"):
        return "EVIDENCE-PLANE"
    return "SUSPICIOUS / UNKNOWN"


def _all_under_src_or_tests(rel_paths: list[str]) -> bool:
    """True iff every path is confined to product tree or companion unit-test tree."""
    for rel in rel_paths:
        p = rel.replace("\\", "/").lstrip("./")
        if p == "src" or p.startswith("src/"):
            continue
        if p == "tests" or p.startswith("tests/"):
            continue
        return False
    return bool(rel_paths)


def _parse_branch_line(line: str) -> tuple[str, str | None, int | None, int | None]:
    """
    Parse `git status --porcelain=v1 -b` first line.
    Returns: (branch_display, upstream_or_none, ahead, behind)
    """
    if not line.startswith("## "):
        return ("(unparsed)", None, None, None)
    rest = line[3:].strip()
    m = re.match(
        r"^(?P<br>[^.]+?)(?:\.\.\.(?P<up>[^\s\[]+))?"
        r"(?:\s*\[(?P<ab>[^\]]+)\])?\s*$",
        rest,
    )
    if not m:
        return (rest, None, None, None)
    br = m.group("br")
    up = m.group("up")
    ab = m.group("ab")
    ahead, behind = None, None
    if ab:
        ma = re.search(r"ahead\s+(\d+)", ab)
        mb = re.search(r"behind\s+(\d+)", ab)
        if ma:
            ahead = int(ma.group(1))
        if mb:
            behind = int(mb.group(1))
    return (br, up, ahead, behind)


def _parse_porcelain_v1(raw: str) -> tuple[list[str], bool, str]:
    """
    Returns (paths relative to repo root, has_unmerged, first_line_or_empty).
    `first_line_or_empty` is the optional `## ...` branch/upstream summary line.
    """
    lines = raw.splitlines()
    paths: list[str] = []
    seen: set[str] = set()
    unmerged = False
    branch_line = ""
    start = 0
    if lines and lines[0].startswith("## "):
        branch_line = lines[0]
        start = 1
    for line in lines[start:]:
        if len(line) < 4:
            continue
        xy = line[:2]
        if "U" in xy or xy == "AA" or xy == "DD":
            unmerged = True
        rest = line[3:]
        if rest.startswith('"'):
            unmerged = True
            continue
        chunk = rest.strip()
        if " -> " in chunk:
            left, right = chunk.split(" -> ", 1)
            for p in (left.strip(), right.strip()):
                if p and p not in seen:
                    seen.add(p)
                    paths.append(p)
        elif chunk:
            if chunk not in seen:
                seen.add(chunk)
                paths.append(chunk)
    return (paths, unmerged, branch_line)


def _stash_count(repo: Path) -> int:
    out, code = _run_git(repo, ["stash", "list"])
    if code != 0:
        return -1
    if not out:
        return 0
    return len(out.splitlines())


def main() -> int:
    ap = argparse.ArgumentParser(description="Frontier BUILD preflight (repo-state truth).")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON on stdout.")
    args = ap.parse_args()

    start = Path.cwd()
    repo = _repo_root(start)
    if repo is None:
        repo = Path(__file__).resolve().parents[1]
        repo = _repo_root(repo)
    if repo is None:
        print("BUILD allowed: NO", file=sys.stderr)
        print("BLOCKER: not a git repository (could not resolve work tree).", file=sys.stderr)
        return 2

    branch_ref, br_code = _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    if br_code != 0:
        branch_ref = "(error)"

    raw_status, st_code = _run_git(repo, ["status", "--porcelain=v1", "-b"])
    if st_code != 0:
        payload = {
            "build_allowed": False,
            "blocker": "git status failed; repo state unreadable.",
            "branch": branch_ref,
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print("BUILD allowed: NO")
            print("BLOCKER: git status failed; repo state unreadable.")
        return 1

    dirty_paths, unmerged, branch_line = _parse_porcelain_v1(raw_status)
    lines = raw_status.splitlines()
    br_disp, upstream, ahead, behind = _parse_branch_line(branch_line)
    is_clean = not any(
        ln for ln in lines if not ln.startswith("## ")
    )

    classifications = {p: _classify_path(p) for p in dirty_paths}
    planes_hit = {classifications[p] for p in dirty_paths}
    core_planes = sorted(p for p in planes_hit if p in KNOWN_PLANES)
    planes_mixed = len(set(core_planes)) > 1
    # Companion tests under tests/ are EVIDENCE in classification but not ambiguous with src/.
    mixed_plane = planes_mixed and not _all_under_src_or_tests(dirty_paths)
    unknown_hits = [p for p, c in classifications.items() if c not in KNOWN_PLANES]

    untracked_names, u_code = _run_git(
        repo, ["ls-files", "-o", "--exclude-standard", "-z"]
    )
    untracked: list[str] = []
    if u_code == 0 and untracked_names:
        untracked = [p for p in untracked_names.split("\0") if p]

    untracked_sop = [
        p for p in untracked if p.replace("\\", "/").replace("//", "/").startswith("docs/SOP/")
    ]

    detached = branch_ref == "HEAD"
    on_main = branch_ref == "main"

    stash_n = _stash_count(repo)

    blocker: str | None = None
    if detached:
        blocker = "detached HEAD; ambiguous branch context."
    elif on_main:
        blocker = "on `main`; execution work must use a short-lived branch or worktree."
    elif unmerged:
        blocker = "unmerged / conflicted index paths present."
    elif untracked_sop:
        blocker = f"untracked canonical docs under docs/SOP/ ({len(untracked_sop)} file(s))."
    elif mixed_plane:
        blocker = f"mixed-plane dirty state across: {', '.join(sorted(set(core_planes)))}."
    elif unknown_hits:
        blocker = "dirty paths include SUSPICIOUS / UNKNOWN locations (ambiguous plane)."
    elif st_code != 0 or br_code != 0:
        blocker = "git metadata incomplete or unreadable."

    build_allowed = blocker is None

    upstream_report = "no-upstream"
    if upstream:
        aa = ahead if ahead is not None else 0
        bb = behind if behind is not None else 0
        upstream_report = f"{upstream} (ahead {aa}, behind {bb})"

    by_plane: dict[str, list[str]] = {
        "CONTROL-PLANE": [],
        "PRODUCT-PLANE": [],
        "EVIDENCE-PLANE": [],
        "SUSPICIOUS / UNKNOWN": [],
    }
    for p in sorted(dirty_paths):
        by_plane[classifications[p]].append(p)

    report = {
        "repo_root": str(repo),
        "branch": branch_ref,
        "branch_status_line": br_disp if branch_line else branch_ref,
        "working_tree": "clean" if is_clean else "dirty",
        "upstream": upstream_report,
        "ahead": ahead,
        "behind": behind,
        "upstream_ref": upstream,
        "modified_untracked_paths": dirty_paths,
        "files_by_plane": by_plane,
        "untracked_canonical_docs_SOP": bool(untracked_sop),
        "untracked_canonical_docs_paths": untracked_sop,
        "mixed_plane_dirty": mixed_plane,
        "unknown_dirty_paths": unknown_hits,
        "stash_entries": stash_n,
        "build_allowed": build_allowed,
        "blocker": blocker,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0 if build_allowed else 1

    print("=== FRONTIER PREFLIGHT (machine-derived) ===")
    print(f"repo_root: {repo}")
    print(f"branch: {branch_ref}")
    print(f"working_tree: {'clean' if is_clean else 'dirty'}")
    print(f"upstream: {upstream_report}")
    print(f"stash_entries: {stash_n}")
    print(f"untracked_canonical_docs_under_docs/SOP: {'yes' if untracked_sop else 'no'}")
    if untracked_sop:
        for p in untracked_sop:
            print(f"  - {p}")
    print(f"mixed_plane_dirty: {'yes' if mixed_plane else 'no'}")
    print("changed_files_by_plane:")
    for plane in ("CONTROL-PLANE", "PRODUCT-PLANE", "EVIDENCE-PLANE", "SUSPICIOUS / UNKNOWN"):
        files = by_plane[plane]
        print(f"  {plane}: {len(files)}")
        for p in files:
            print(f"    - {p}")
    if not dirty_paths:
        print("  (no modified/untracked paths reported by git status)")
    print(f"BUILD allowed: {'YES' if build_allowed else 'NO'}")
    if blocker:
        print(f"BLOCKER: {blocker}")
    print("=== END PREFLIGHT ===")
    return 0 if build_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
