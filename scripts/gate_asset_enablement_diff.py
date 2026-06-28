#!/usr/bin/env python3
"""CI gate: config/assets.yaml diffs that newly set enabled: true require witness proof.

Pass when:
  - No new enablements in the diff, or
  - A witness artifact under artifacts/enablement/ covers the batch, or
  - pre-enable witness passes for the batch (mocked in CI).

See docs/SOP/ASSET_ENABLEMENT_RUNBOOK_V1.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import yaml  # noqa: E402

from src.data.assets_registry import get_asset  # noqa: E402

ASSETS_REL = "config/assets.yaml"
ARTIFACT_PREFIX = "artifacts/enablement/"


def _git_show(repo: Path, ref: str, rel: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{rel}"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def _load_yaml(text: str | None) -> dict[str, Any]:
    if not text:
        return {}
    data = yaml.safe_load(text)
    return data if isinstance(data, dict) else {}


def _enabled_map(data: dict[str, Any]) -> dict[str, bool]:
    assets = data.get("assets")
    if not isinstance(assets, dict):
        return {}
    out: dict[str, bool] = {}
    for aid, row in assets.items():
        if isinstance(row, dict):
            out[str(aid).upper()] = row.get("enabled") is True
    return out


def newly_enabled_asset_ids(base: dict[str, bool], head: dict[str, bool]) -> list[str]:
    return sorted(aid for aid, enabled in head.items() if enabled and not base.get(aid))


def _catalog_group(aid: str) -> str | None:
    try:
        entry = get_asset(aid)
    except KeyError:
        return None
    catalog = entry.get("catalog")
    if isinstance(catalog, dict):
        group = str(catalog.get("group") or "").strip()
        return group or None
    return None


def _groups_for_assets(asset_ids: list[str]) -> list[str]:
    groups: set[str] = set()
    for aid in asset_ids:
        group = _catalog_group(aid)
        if group:
            groups.add(group)
    return sorted(groups)


def _artifact_covers_assets(repo: Path, artifact_rel: str, asset_ids: list[str]) -> bool:
    path = repo / artifact_rel.replace("\\", "/")
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if not data.get("witness_ok"):
        return False
    covered = {str(a).upper() for a in (data.get("asset_ids") or data.get("enabled") or [])}
    applied = {str(a).upper() for a in (data.get("applied") or [])}
    if applied:
        covered |= applied
    return set(asset_ids).issubset(covered)


def _witness_artifact_ok(repo: Path, changed_files: list[str], asset_ids: list[str]) -> bool:
    for rel in changed_files:
        norm = rel.replace("\\", "/")
        if norm.startswith(ARTIFACT_PREFIX) and norm.endswith(".json"):
            if _artifact_covers_assets(repo, norm, asset_ids):
                return True
    return False


def _witness_group_passes(group: str) -> tuple[bool, str]:
    from scripts import witness_asset_catalog as witness_mod

    ids = witness_mod.list_asset_ids_for_catalog_group(group, enabled_only=False)
    report = witness_mod.run_witness(ids, live=False)
    ok = bool(report.get("ok"))
    detail = str(report.get("catalog_detail") or ("ok" if ok else "witness failed"))
    return ok, detail


def _witness_pre_enable_passes(asset_ids: list[str]) -> tuple[bool, str]:
    from scripts import witness_asset_catalog as witness_mod

    report = witness_mod.run_witness(asset_ids, live=False, pre_enable=True)
    ok = bool(report.get("ok"))
    detail = str(report.get("catalog_detail") or ("ok" if ok else "pre-enable witness failed"))
    return ok, detail


def evaluate_enablement_diff(
    repo: Path,
    *,
    base_ref: str,
    head_ref: str = "HEAD",
    changed_files: list[str] | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    base_text = _git_show(repo, base_ref, ASSETS_REL)
    head_text = _git_show(repo, head_ref, ASSETS_REL)
    base_map = _enabled_map(_load_yaml(base_text))
    head_map = _enabled_map(_load_yaml(head_text))
    new_ids = newly_enabled_asset_ids(base_map, head_map)

    result: dict[str, Any] = {
        "ok": True,
        "newly_enabled": new_ids,
        "reason": "no new enablements",
        "base_ref": base_ref,
        "head_ref": head_ref,
    }
    if not new_ids:
        return result

    files = changed_files or []
    if _witness_artifact_ok(repo, files, new_ids):
        result["reason"] = "witness artifact covers batch"
        return result

    groups = _groups_for_assets(new_ids)
    if not groups:
        result["ok"] = False
        result["reason"] = f"new enablements {new_ids} have no catalog.group — add witness artifact"
        return result

    ok, detail = _witness_pre_enable_passes(new_ids)
    if ok:
        result["reason"] = f"pre-enable witness ok for {new_ids}"
        return result

    failed: list[str] = []
    for group in groups:
        g_ok, g_detail = _witness_group_passes(group)
        if not g_ok:
            failed.append(f"{group}: {g_detail}")
    if failed:
        result["ok"] = False
        result["reason"] = (
            f"assets.yaml newly enables {new_ids}; pre-enable witness failed ({detail}); "
            f"group witness failed: {'; '.join(failed)}. "
            f"Run enable_asset_batch --dry-run then --apply, or add "
            f"{ARTIFACT_PREFIX}<batch>.json with witness_ok."
        )
        return result

    result["reason"] = f"group witness ok for {groups}"
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gate new enabled: true diffs in config/assets.yaml")
    ap.add_argument("--repo-root", type=Path, default=_REPO_ROOT)
    ap.add_argument("--base-ref", default="origin/main")
    ap.add_argument("--head-ref", default="HEAD")
    ap.add_argument(
        "--changed-file",
        action="append",
        default=[],
        help="Changed file path (repeatable); when omitted, gate runs if assets.yaml differs",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    changed = [str(p).replace("\\", "/") for p in args.changed_file]

    if changed and ASSETS_REL not in changed:
        out = {"ok": True, "skipped": True, "reason": f"{ASSETS_REL} not in changed files"}
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print("gate_asset_enablement_diff: skip (assets.yaml unchanged)")
        return 0

    result = evaluate_enablement_diff(
        repo,
        base_ref=args.base_ref,
        head_ref=args.head_ref,
        changed_files=changed or None,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        print(f"gate_asset_enablement_diff: OK — {result['reason']}")
    else:
        print(f"gate_asset_enablement_diff: FAIL — {result['reason']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
