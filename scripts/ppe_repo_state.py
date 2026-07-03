"""Unified repo-state SSOT — plane classification, severity, recovery routing.

Writes artifacts/control_plane/REPO_STATE.json. Consumed by operator status,
coordination check, burst plan, and branch recovery.

Canon: docs/SOP/REPO_STATE_V1.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

REPO_STATE_REL = "artifacts/control_plane/REPO_STATE.json"

# Severity ladder (0 = cleanest)
SEVERITY_CLEAN = 0
SEVERITY_CAUTION = 1
SEVERITY_STEWARD = 2
SEVERITY_BLOCKED = 3

SEVERITY_LABELS = {
    SEVERITY_CLEAN: "CLEAN",
    SEVERITY_CAUTION: "CAUTION",
    SEVERITY_STEWARD: "STEWARD",
    SEVERITY_BLOCKED: "BLOCKED",
}

CORE_PLANES = frozenset({"CONTROL", "PRODUCT", "EVIDENCE", "CANON", "PLATFORM"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def current_branch(repo: Path) -> str:
    proc = _git(repo, "branch", "--show-current")
    return (proc.stdout or "").strip()


def dirty_paths(repo: Path) -> list[str]:
    from scripts.repo_layer_paths import git_dirty_paths, is_preflight_dirty_exempt

    return [p for p in git_dirty_paths(repo) if not is_preflight_dirty_exempt(p)]


def plane_for_path(path: str) -> str:
    """Single plane map for SSOT (delegation + frontier aligned)."""
    p = _norm(path)
    if not p:
        return "OTHER"
    if p.startswith("docs/SOP/"):
        return "CONTROL"
    if p.startswith("src/") or p.startswith("apps/"):
        return "PRODUCT"
    if p.startswith("tests/") or p.startswith("scripts/"):
        return "EVIDENCE"
    if p.startswith("docs/VISION/") or p.startswith("docs/RELEASES/"):
        return "CANON"
    if p.startswith(".github/") or p.startswith("docs/DEPLOY/"):
        return "PLATFORM"
    return "OTHER"


def _all_under_src_or_tests(paths: list[str]) -> bool:
    for rel in paths:
        p = _norm(rel)
        if p == "src" or p.startswith("src/"):
            continue
        if p == "tests" or p.startswith("tests/"):
            continue
        return False
    return bool(paths)


def is_mixed_plane(paths: list[str]) -> bool:
    if not paths:
        return False
    planes = {plane_for_path(p) for p in paths}
    core = planes & CORE_PLANES
    if len(core) < 2:
        return False
    product_evidence = core <= {"PRODUCT", "EVIDENCE"}
    if product_evidence and _all_under_src_or_tests(paths):
        return False
    return True


def paths_by_plane(paths: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {p: [] for p in sorted(CORE_PLANES | {"OTHER"})}
    for path in sorted(paths):
        out[plane_for_path(path)].append(path)
    return {k: v for k, v in out.items() if v}


def recovery_commands_for_paths(paths: list[str]) -> list[str]:
    """Ordered recovery commands to clear mixed or single-plane dirty state."""
    by_plane = paths_by_plane(paths)
    cmds: list[str] = []
    if by_plane.get("CONTROL"):
        cmds.append("python scripts/ppe_branch_recovery.py --plane control --ship")
    if by_plane.get("PRODUCT"):
        cmds.append("python scripts/ppe_branch_recovery.py --plane product --ship")
    if by_plane.get("EVIDENCE") and not by_plane.get("CONTROL") and not by_plane.get("PRODUCT"):
        cmds.append("python scripts/ppe_branch_recovery.py --plane control --ship")
    if by_plane.get("CANON") or by_plane.get("PLATFORM"):
        cmds.append("python scripts/ppe_branch_recovery.py --plane control --ship")
    if is_mixed_plane(paths) and len(cmds) > 1:
        return ["python scripts/ppe_branch_recovery.py --ship-all"]
    return cmds or ["python scripts/ppe_branch_recovery.py --plane control --plan-only"]


def assess_repo_state(
    repo: Path,
    *,
    verdict: str = "",
    branch_preflight: dict[str, Any] | None = None,
    delegation_tier: str | None = None,
    delegation_reasons: list[str] | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    paths = dirty_paths(repo)
    branch = current_branch(repo)
    on_main = branch in ("main", "master")
    by_plane = paths_by_plane(paths)
    planes_active = sorted(by_plane.keys())
    mixed = is_mixed_plane(paths)

    blockers: list[str] = []
    cautions: list[str] = []
    info: list[str] = []

    untracked_sop: list[str] = []
    try:
        proc = _git(repo, "ls-files", "-o", "--exclude-standard", "docs/SOP/")
        if proc.returncode == 0:
            untracked_sop = [p for p in (proc.stdout or "").splitlines() if p.strip()]
    except Exception:
        pass

    if branch == "HEAD":
        blockers.append("detached HEAD")
    if untracked_sop:
        blockers.append(f"untracked canonical docs under docs/SOP/ ({len(untracked_sop)})")

    tier = delegation_tier
    reasons = list(delegation_reasons or [])
    if tier is None:
        try:
            from scripts.ppe_delegation_envelope import classify_paths, current_branch as dg_branch

            if paths:
                dv = classify_paths(repo, paths, branch=dg_branch(repo))
                tier = str(dv.tier or "auto")
                reasons = list(dv.reasons or [])
            else:
                tier = "auto"
        except Exception:
            tier = "auto"

    if tier == "human_only":
        blockers.append(reasons[0] if reasons else "human_only delegation")

    bpf = branch_preflight or {}
    if bpf.get("blocks_relay"):
        for r in bpf.get("reasons") or []:
            blockers.append(str(r))

    if mixed:
        blockers.append(f"mixed-plane dirty state ({', '.join(planes_active)})")
    elif paths and on_main:
        cautions.append(f"dirty on main ({len(paths)} path(s) — recoverable)")
    elif paths and not on_main:
        cautions.append(f"dirty on branch {branch!r} ({len(paths)} path(s))")

    if tier == "steward_packet" and not mixed:
        detail = next((r for r in reasons if "mixed_plane" in r.lower()), reasons[0] if reasons else "")
        if detail:
            cautions.append(f"delegation steward_packet: {detail}")

    build_allowed = not blockers and not mixed and branch not in ("", "HEAD")
    if on_main and paths and not mixed:
        build_allowed = False

    severity = SEVERITY_CLEAN
    if blockers or tier == "human_only":
        severity = SEVERITY_BLOCKED
    elif mixed or tier == "steward_packet" or bpf.get("blocks_relay"):
        severity = SEVERITY_STEWARD
    elif paths or cautions:
        severity = SEVERITY_CAUTION

    relay_allowed = severity < SEVERITY_STEWARD and not bpf.get("blocks_relay")
    burst_allowed = severity < SEVERITY_STEWARD

    if severity >= SEVERITY_STEWARD:
        recommended_action = "recover"
        recommended_commands = recovery_commands_for_paths(paths)
    elif severity == SEVERITY_CAUTION and paths:
        recommended_action = "recover_or_ship"
        recommended_commands = recovery_commands_for_paths(paths) or [
            "python scripts/run_pushable_gate.py → commit → push → PR"
        ]
    else:
        recommended_action = "proceed"
        recommended_commands = []

    unlocks_after: list[str] = []
    if not burst_allowed:
        unlocks_after.append("burst")
    if not relay_allowed:
        unlocks_after.append("relay")
    if not build_allowed:
        unlocks_after.append("build")

    return {
        "as_of": _utc_now(),
        "branch": branch,
        "on_main": on_main,
        "working_tree": "clean" if not paths else "dirty",
        "dirty_count": len(paths),
        "dirty_paths": paths[:50],
        "paths_by_plane": by_plane,
        "planes_active": planes_active,
        "mixed_plane": mixed,
        "severity": severity,
        "severity_label": SEVERITY_LABELS[severity],
        "blockers": blockers,
        "cautions": cautions,
        "info": info,
        "delegation_tier": tier,
        "delegation_reasons": reasons[:8],
        "build_allowed": build_allowed,
        "burst_allowed": burst_allowed,
        "relay_allowed": relay_allowed,
        "recommended_action": recommended_action,
        "recommended_commands": recommended_commands,
        "unlocks_after_recovery": unlocks_after,
        "untracked_sop": untracked_sop[:10],
    }


def format_repo_state_lines(state: dict[str, Any]) -> list[str]:
    """Human/agent lines for OPERATOR_STATUS."""
    if not state:
        return []
    label = str(state.get("severity_label") or "CLEAN")
    lines = ["", f"**Repo state:** `{label}`"]
    for b in state.get("blockers") or []:
        lines.append(f"  - **Blocker:** {b}")
    for c in state.get("cautions") or []:
        lines.append(f"  - Caution: {c}")
    for i in state.get("info") or []:
        lines.append(f"  - Info: {i}")
    cmds = state.get("recommended_commands") or []
    if cmds:
        lines.append(f"  → Next: `{cmds[0]}`")
    if label in ("STEWARD", "BLOCKED"):
        lines.append("  → See docs/SOP/RECOVERY_PROTOCOL.md")
    return lines


def split_preflight_warnings(warnings: list[str]) -> tuple[list[str], list[str]]:
    """Split layer-scope info from actionable preflight warnings."""
    info: list[str] = []
    actionable: list[str] = []
    for w in warnings:
        if str(w).startswith("repo layer scope:"):
            info.append(str(w))
        else:
            actionable.append(str(w))
    return actionable, info


def enrich_repo_state_info(state: dict[str, Any], preflight_warnings: list[str]) -> dict[str, Any]:
    """Merge preflight info lines into repo state."""
    _, info = split_preflight_warnings(preflight_warnings)
    if info:
        state = {**state, "info": list(state.get("info") or []) + info}
    actionable, _ = split_preflight_warnings(preflight_warnings)
    if actionable and state.get("severity", 0) < SEVERITY_CAUTION:
        state = {
            **state,
            "severity": SEVERITY_CAUTION,
            "severity_label": SEVERITY_LABELS[SEVERITY_CAUTION],
            "cautions": list(state.get("cautions") or []) + actionable,
        }
    return state


def write_repo_state(repo: Path, state: dict[str, Any]) -> Path:
    out = repo / REPO_STATE_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return out


def load_repo_state(repo: Path) -> dict[str, Any] | None:
    p = repo / REPO_STATE_REL
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def assess_and_write(
    repo: Path,
    *,
    verdict: str = "",
    branch_preflight: dict[str, Any] | None = None,
    preflight_warnings: list[str] | None = None,
) -> dict[str, Any]:
    state = assess_repo_state(repo, verdict=verdict, branch_preflight=branch_preflight)
    if preflight_warnings:
        state = enrich_repo_state_info(state, preflight_warnings)
    write_repo_state(repo, state)
    return state


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Assess unified repo state (SSOT).")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help=f"Write {REPO_STATE_REL}")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    state = assess_repo_state(repo)
    if args.write:
        write_repo_state(repo, state)
    if args.json:
        print(json.dumps(state, indent=2))
    elif not args.write:
        print(
            f"ppe_repo_state: {state['severity_label']} "
            f"mixed_plane={state['mixed_plane']} dirty={state['dirty_count']}"
        )
        for cmd in state.get("recommended_commands") or []:
            print(f"  → {cmd}")
    return 0 if state["severity"] < SEVERITY_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())
