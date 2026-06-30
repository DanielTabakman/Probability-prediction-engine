"""Smart delegation envelope — classify change authority for agents vs operator.

Canon: docs/SOP/DELEGATION_ENVELOPE_V1.json · docs/SOP/DELEGATION_ENVELOPE_V1.md
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

ENVELOPE_REL = "docs/SOP/DELEGATION_ENVELOPE_V1.json"
TIER_RANK = {"auto": 0, "auto_notify": 1, "steward_packet": 2, "human_only": 3}


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip().lstrip("./")


def load_envelope(repo: Path) -> dict[str, Any]:
    p = repo.resolve() / ENVELOPE_REL
    if not p.is_file():
        return {"version": 1, "pathRules": [], "escalators": [], "tierRank": TIER_RANK}
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _match_prefix(path: str, prefix: str) -> bool:
    p = _norm(path)
    pref = _norm(prefix)
    if pref.endswith("/"):
        return p.startswith(pref) or p == pref.rstrip("/")
    return p == pref or p.startswith(pref + "/")


def _match_rule(path: str, rule: dict[str, Any]) -> bool:
    p = _norm(path)
    for pref in rule.get("prefixes") or []:
        if _match_prefix(p, str(pref)):
            return True
    for exact in rule.get("exact") or []:
        if p == _norm(str(exact)):
            return True
    glob_pat = rule.get("glob")
    if glob_pat and fnmatch.fnmatch(p, str(glob_pat)):
        return True
    suffix = rule.get("suffix")
    if suffix and p.endswith(_norm(str(suffix))):
        return True
    return False


def _plane_for_path(path: str) -> str:
    p = _norm(path)
    if p.startswith("docs/SOP/"):
        return "CONTROL"
    if p.startswith("docs/VISION/") or p.startswith("docs/RELEASES/"):
        return "CANON"
    if p.startswith("src/") or p.startswith("apps/"):
        return "PRODUCT"
    if p.startswith("tests/") or p.startswith("scripts/"):
        return "EVIDENCE"
    if p.startswith(".github/") or p.startswith("docs/DEPLOY/"):
        return "PLATFORM"
    return "OTHER"


@dataclass
class DelegationVerdict:
    tier: str
    reasons: list[str] = field(default_factory=list)
    path_tiers: dict[str, str] = field(default_factory=dict)
    planes: set[str] = field(default_factory=set)

    @property
    def rank(self) -> int:
        return TIER_RANK.get(self.tier, 99)

    def can_auto_ship(self) -> bool:
        return self.tier in ("auto", "auto_notify")

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier,
            "can_auto_ship": self.can_auto_ship(),
            "reasons": self.reasons,
            "path_tiers": self.path_tiers,
            "planes": sorted(self.planes),
        }


def _max_tier(a: str, b: str) -> str:
    return a if TIER_RANK.get(a, 0) >= TIER_RANK.get(b, 0) else b


def classify_paths(
    repo: Path,
    paths: list[str],
    *,
    pass_type: str = "",
    branch: str = "",
    git_force_push: bool = False,
) -> DelegationVerdict:
    env = load_envelope(repo)
    rules = [r for r in (env.get("pathRules") or []) if isinstance(r, dict)]
    rank_map = env.get("tierRank") or TIER_RANK

    worst = "auto"
    reasons: list[str] = []
    path_tiers: dict[str, str] = {}
    planes: set[str] = set()

    for raw in paths:
        path = _norm(raw)
        if not path:
            continue
        planes.add(_plane_for_path(path))
        tier = "auto"
        matched_reason = "default product/control delegation"
        for rule in rules:
            if _match_rule(path, rule):
                rt = str(rule.get("tier") or "auto")
                if rank_map.get(rt, 0) >= rank_map.get(tier, 0):
                    tier = rt
                    matched_reason = str(rule.get("reason") or rule.get("id") or rt)
        path_tiers[path] = tier
        worst = _max_tier(worst, tier)
        if tier != "auto":
            reasons.append(f"{path}: {matched_reason}")

    for esc in env.get("escalators") or []:
        if not isinstance(esc, dict):
            continue
        eid = str(esc.get("id") or "")
        bump = str(esc.get("bumpTo") or "steward_packet")
        unless = str(esc.get("unlessPassType") or "").strip().upper()
        if unless and pass_type.upper() == unless:
            continue

        if eid == "mixed_plane" and len(planes) >= int(esc.get("planesGte") or 2):
            worst = _max_tier(worst, bump)
            reasons.append(f"escalator mixed_plane: {esc.get('reason', '')}")
        elif eid == "large_diff" and len(paths) >= int(esc.get("fileCountGte") or 25):
            worst = _max_tier(worst, bump)
            reasons.append(f"escalator large_diff: {esc.get('reason', '')}")
        elif eid == "force_push" and git_force_push:
            worst = _max_tier(worst, bump)
            reasons.append(f"escalator force_push: {esc.get('reason', '')}")
        elif eid == "main_direct" and branch in ("main", "master"):
            worst = _max_tier(worst, bump)
            reasons.append(f"escalator main_direct: {esc.get('reason', '')}")

    # Dedupe reasons preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            uniq.append(r)

    return DelegationVerdict(tier=worst, reasons=uniq, path_tiers=path_tiers, planes=planes)


def git_changed_paths(repo: Path, *, staged_only: bool = False) -> list[str]:
    cmd = ["git", "diff", "--name-only"]
    if staged_only:
        cmd.append("--cached")
    else:
        cmd.extend(["HEAD", "--"])
    out = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, check=False)
    paths = [_norm(l) for l in (out.stdout or "").splitlines() if l.strip()]
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    paths.extend(_norm(l) for l in (untracked.stdout or "").splitlines() if l.strip())
    return sorted(set(paths))


def current_branch(repo: Path) -> str:
    out = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    return (out.stdout or "").strip()


def gate_check(repo: Path, paths: list[str], *, pass_type: str = "") -> int:
    """Return 0 if ship allowed; 1 if human_only blocks."""
    if os.environ.get("PPE_DELEGATION_OVERRIDE", "").strip().lower() in ("1", "true", "yes"):
        print("ppe_delegation_envelope: override active — skip block")
        return 0
    verdict = classify_paths(
        repo,
        paths,
        pass_type=pass_type,
        branch=current_branch(repo),
    )
    print(f"ppe_delegation_envelope: tier={verdict.tier} can_auto_ship={verdict.can_auto_ship()}")
    for r in verdict.reasons[:8]:
        print(f"  - {r}")
    if len(verdict.reasons) > 8:
        print(f"  - ... {len(verdict.reasons) - 8} more")
    if verdict.tier == "human_only":
        print(
            "ppe_delegation_envelope: BLOCK — human_only paths or escalator. "
            "Operator must explicitly authorize, or RECOVERY pass with PPE_DELEGATION_OVERRIDE=1.",
            file=sys.stderr,
        )
        return 1
    if verdict.tier == "steward_packet":
        print(
            "ppe_delegation_envelope: WARN — steward_packet; prefer decision packet before merge.",
            file=sys.stderr,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Smart delegation envelope classifier")
    ap.add_argument("--repo-root", type=Path, default=_REPO)
    ap.add_argument("--pass-type", default="", help="BUILD | RECOVERY | CLOSEOUT")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gate-check", action="store_true", help="Exit 1 on human_only (for run_pushable_gate)")
    ap.add_argument("paths", nargs="*", help="Paths to classify (default: git changed)")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    paths = [_norm(p) for p in args.paths if p.strip()] or git_changed_paths(repo)

    verdict = classify_paths(
        repo,
        paths,
        pass_type=args.pass_type,
        branch=current_branch(repo),
    )
    if args.json:
        print(json.dumps(verdict.to_dict(), indent=2))
        return 0
    if args.gate_check:
        return gate_check(repo, paths, pass_type=args.pass_type)
    print(f"tier: {verdict.tier}")
    print(f"can_auto_ship: {verdict.can_auto_ship()}")
    print(f"planes: {', '.join(sorted(verdict.planes)) or '(none)'}")
    for r in verdict.reasons:
        print(f"  - {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
