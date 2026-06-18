"""VM loop-host bootstrap: config, git hygiene, slice progress sync, operator recovery."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

LOOP_HOST_EXAMPLE = "ppe_operator_loop_host.local.cmd.example"
LOOP_HOST_LOCAL = "ppe_operator_loop_host.local.cmd"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def ensure_loop_host_config(repo: Path) -> dict[str, Any]:
    dest = repo / LOOP_HOST_LOCAL
    src = repo / LOOP_HOST_EXAMPLE
    no_loop = repo / "ppe_operator_no_loop.local.cmd"
    if dest.is_file():
        result = {"action": "loop_host_config", "ok": True, "skipped": True, "path": str(dest)}
    elif not src.is_file():
        return {"action": "loop_host_config", "ok": False, "error": f"missing {LOOP_HOST_EXAMPLE}"}
    else:
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        result = {"action": "loop_host_config", "ok": True, "created": True, "path": str(dest)}
    if no_loop.is_file():
        backup = repo / "ppe_operator_no_loop.local.cmd.off-vm"
        if not backup.is_file():
            no_loop.rename(backup)
            result["no_loop_disabled"] = str(backup)
    return result


def detach_worktrees_holding_branch(repo: Path, branch: str = "main") -> list[dict[str, Any]]:
    """Detach HEAD on worktrees that hold a branch the operator checkout needs."""
    out: list[dict[str, Any]] = []
    proc = _git(repo, "worktree", "list", "--porcelain")
    if proc.returncode != 0:
        return out
    lines = (proc.stdout or "").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("worktree "):
            i += 1
            continue
        wt_path = line.split(" ", 1)[1].strip()
        wt_branch = ""
        j = i + 1
        while j < len(lines) and not lines[j].startswith("worktree "):
            if lines[j].startswith("branch "):
                wt_branch = lines[j].replace("branch refs/heads/", "").strip()
            j += 1
        i = j
        if wt_branch != branch:
            continue
        if Path(wt_path).resolve() == repo.resolve():
            continue
        co = _git(Path(wt_path), "checkout", "--detach")
        out.append(
            {
                "worktree": wt_path,
                "branch": branch,
                "detached": co.returncode == 0,
                "error": None if co.returncode == 0 else (co.stderr or co.stdout or "").strip(),
            }
        )
    return out


def ensure_on_main(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_operator_git_sync import ensure_main_on_loop_host, pull_main

        checkout = ensure_main_on_loop_host(repo)
        if checkout.get("checked_out"):
            return {"action": "ensure_main", **checkout}
        pull = pull_main(repo)
        return {"action": "ensure_main", "checkout": checkout, "pull": pull}
    except ImportError as exc:
        return {"action": "ensure_main", "ok": False, "error": str(exc)}


def _touchset_satisfied(repo: Path, slice_obj: dict[str, Any]) -> bool:
    raw = slice_obj.get("touchSet") or []
    if not isinstance(raw, list):
        return False
    paths = [str(p).strip() for p in raw if str(p).strip()]
    if not paths:
        return False
    return all((repo / p).is_file() for p in paths)


# Slice-specific compose markers — shared touchSet paths (e.g. docker-compose.yml) are not
# sufficient alone; prior chapters may have already landed the generic files.
_PLATFORM_COMPOSE_MARKERS: dict[str, tuple[str, ...]] = {
    "MSOS-UserStateV1-Platform-Slice003": (
        "PPE_SNAPSHOT_DB_PATH=/ppe-snapshots",
        "ppe_snapshots:/ppe-snapshots:ro",
    ),
}


def _platform_touchset_satisfied(repo: Path, slice_id: str, slice_obj: dict[str, Any]) -> bool:
    if not _touchset_satisfied(repo, slice_obj):
        return False
    markers = _PLATFORM_COMPOSE_MARKERS.get(slice_id)
    if not markers:
        return True
    compose = repo / "docker-compose.yml"
    if not compose.is_file():
        return False
    body = compose.read_text(encoding="utf-8", errors="replace")
    return all(marker in body for marker in markers)


def _is_closeout_slice(slice_obj: dict[str, Any]) -> bool:
    return isinstance(slice_obj.get("closeout"), dict)


def _evidence_has_pending_slices(body: str) -> bool:
    import re

    return bool(re.search(r"\|\s*PENDING\s*\|", body, re.I))


def _witness_touchset_only_evidence(slice_obj: dict[str, Any]) -> bool:
    raw = slice_obj.get("touchSet") or []
    if not isinstance(raw, list):
        return False
    paths = [str(p).strip() for p in raw if str(p).strip()]
    return len(paths) == 1 and paths[0].endswith("_EVIDENCE_STATUS.md")


def sync_slice_progress(repo: Path, plan_path: str) -> dict[str, Any]:
    """Mark relay slices complete when their touchSet (or product merge) is already on main."""
    from scripts.ppe_ide_product_ready import _product_touchset_on_main
    from scripts.ppe_manifest import load_phase_plan
    from scripts.ppe_phase_plan_window import (
        completed_slice_ids,
        load_progress,
        mark_slice_complete,
    )
    from scripts.ppe_slice_worker_mode import infer_slice_kind

    norm = plan_path.replace("\\", "/").strip()
    plan = load_phase_plan(repo, plan_path)
    progress = load_progress(repo)
    progress_plan = str(progress.get("planPath") or "").replace("\\", "/").strip()
    if progress_plan and progress_plan != norm:
        from scripts.ppe_phase_plan_window import clear_progress

        clear_progress(repo, progress_plan)

    marked: list[str] = []
    completed_before = completed_slice_ids(repo, norm)
    slices = [sl for sl in (plan.get("slices") or []) if isinstance(sl, dict)]
    product_on_main = False
    for sl in slices:
        sid = str(sl.get("sliceId") or "").strip()
        if not sid:
            continue
        if infer_slice_kind(sid, sl) == "product" and _product_touchset_on_main(
            repo, slice_id=sid, plan_path=norm
        ):
            product_on_main = True
            break

    for sl in slices:
        sid = str(sl.get("sliceId") or "").strip()
        if not sid or sid in completed_before:
            continue
        if _is_closeout_slice(sl):
            continue
        kind = infer_slice_kind(sid, sl)
        if kind == "product":
            if _product_touchset_on_main(repo, slice_id=sid, plan_path=norm):
                mark_slice_complete(repo, norm, sid)
                marked.append(sid)
            continue
        if _witness_touchset_only_evidence(sl):
            raw = sl.get("touchSet") or []
            evidence_path = repo / str(raw[0])
            if evidence_path.is_file():
                body = evidence_path.read_text(encoding="utf-8", errors="replace")
                if not _evidence_has_pending_slices(body):
                    mark_slice_complete(repo, norm, sid)
                    marked.append(sid)
            continue
        if "PLATFORM" in sid.upper():
            if _platform_touchset_satisfied(repo, sid, sl):
                mark_slice_complete(repo, norm, sid)
                marked.append(sid)
            continue
        if _touchset_satisfied(repo, sl):
            mark_slice_complete(repo, norm, sid)
            marked.append(sid)
            continue
        if kind != "product" and not (sl.get("touchSet") or []):
            selection = str(plan.get("selectionRecord") or "").strip()
            if product_on_main and selection and (repo / selection).is_file():
                mark_slice_complete(repo, norm, sid)
                marked.append(sid)

    return {
        "action": "sync_slice_progress",
        "plan_path": norm,
        "marked": marked,
        "completed": sorted(completed_slice_ids(repo, norm)),
    }


def heal_stale_relay_state(repo: Path) -> dict[str, Any]:
    """Abort relay runs stuck staged without relay_result.json (anchor repo)."""
    changes: list[str] = []
    relay_state_path = repo / "artifacts" / "relay" / "state" / "run_state.json"
    if not relay_state_path.is_file():
        return {"action": "heal_relay_state", "changes": changes}
    try:
        state = json.loads(relay_state_path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return {"action": "heal_relay_state", "changes": changes}
    if not isinstance(state, dict):
        return {"action": "heal_relay_state", "changes": changes}
    status = str(state.get("status") or "")
    run_id = str(state.get("run_id") or "").strip()
    if status not in ("staged_for_worker", "retry_waiting") or not run_id:
        return {"action": "heal_relay_state", "changes": changes}
    result_path = repo / "artifacts" / "relay" / "runs" / run_id / "relay_result.json"
    if result_path.is_file():
        return {"action": "heal_relay_state", "changes": changes}
    relay_script = repo / "scripts" / "relay_runtime_v0.py"
    if relay_script.is_file():
        for cmd in ("abort", "reset"):
            subprocess.run(
                [sys.executable, str(relay_script), "--repo-root", str(repo), cmd],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
    changes.append(f"relay reset (stale {status} run_id={run_id})")
    return {"action": "heal_relay_state", "changes": changes}


def loop_host_git_hygiene(repo: Path) -> dict[str, Any]:
    """Reset transient operator paths that block git pull on the loop host."""
    changes: list[str] = []
    for rel in (".cursor/IDE_BUILD_TRIGGER.json",):
        path = repo / rel
        proc = _git(repo, "status", "--porcelain", rel)
        if path.is_file() and (proc.stdout or "").strip():
            _git(repo, "checkout", "--", rel)
            changes.append(f"reset {rel}")
    return {"action": "git_hygiene", "changes": changes}


def heal_operator_artifacts(repo: Path) -> dict[str, Any]:
    """Clear stale locks / ACTIVE_RUN that block a fresh relay pass."""
    actions: list[str] = []
    for rel in (
        "artifacts/orchestrator/ACTIVE_RUN.json",
        "artifacts/orchestrator/REMOTE_BUILD_LOCK.json",
    ):
        p = repo / rel
        if p.is_file():
            p.unlink()
            actions.append(f"removed {rel}")
    manifest_path = repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    if manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, OSError):
            data = {}
        if str(data.get("status") or "").upper() == "RUNNING":
            data["status"] = "READY"
            manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            actions.append("manifest RUNNING -> READY")
    return {"action": "heal_artifacts", "changes": actions}


def run_queue_repair(repo: Path) -> dict[str, Any]:
    from scripts.ppe_queue_health import repair_backlog, repair_queue, repair_roadmap

    q_fixes, q_remaining = repair_queue(repo, apply=True)
    r_fixes, r_remaining = repair_roadmap(repo, apply=True)
    b_fixes, b_remaining = repair_backlog(repo, apply=True)
    return {
        "action": "queue_repair",
        "queue_fixes": len(q_fixes),
        "roadmap_fixes": len(r_fixes),
        "backlog_fixes": len(b_fixes),
        "queue_remaining": len(q_remaining),
        "roadmap_remaining": len(r_remaining),
        "backlog_remaining": len(b_remaining),
    }


def advance_operator(repo: Path, *, run_local: bool, ensure_stack: bool) -> dict[str, Any]:
    from scripts.ppe_autobuilder import (
        action_advance,
        action_ensure,
        action_run_local,
        collect_autobuilder_status,
    )

    status = collect_autobuilder_status(repo)
    out: dict[str, Any] = {"verdict_before": status.get("verdict"), "phase_before": status.get("phase")}
    if run_local and str(status.get("verdict") or "") == "RUN_LOCAL":
        out["run_local"] = action_run_local(repo)
    elif ensure_stack and str(status.get("phase") or "") == "STACK_DOWN":
        out["ensure"] = action_ensure(repo)
    else:
        out["advance"] = action_advance(repo)
    after = collect_autobuilder_status(repo)
    out["verdict_after"] = after.get("verdict")
    out["phase_after"] = after.get("phase")
    return out


def bootstrap(
    repo: Path,
    *,
    sync_progress: bool = True,
    heal: bool = True,
    queue_repair: bool = True,
    run_local: bool = False,
    ensure_stack: bool = False,
    detach_main_worktrees: bool = True,
    ensure_main: bool = True,
) -> dict[str, Any]:
    repo = repo.resolve()
    report: dict[str, Any] = {"repo": str(repo), "steps": []}

    report["steps"].append(ensure_loop_host_config(repo))
    if detach_main_worktrees:
        detached = detach_worktrees_holding_branch(repo, "main")
        if detached:
            report["steps"].append({"action": "detach_main_worktrees", "detached": detached})
    if ensure_main:
        report["steps"].append(ensure_on_main(repo))

    try:
        from scripts.ppe_manifest import load_manifest

        manifest = load_manifest(repo)
        plan_path = str(manifest.get("phasePlanPath") or "").strip()
    except FileNotFoundError:
        plan_path = ""

    if heal:
        report["steps"].append(loop_host_git_hygiene(repo))
        report["steps"].append(heal_stale_relay_state(repo))
        report["steps"].append(heal_operator_artifacts(repo))
    if sync_progress and plan_path:
        report["steps"].append(sync_slice_progress(repo, plan_path))
    if queue_repair:
        report["steps"].append(run_queue_repair(repo))
    if run_local or ensure_stack:
        report["steps"].append(
            advance_operator(repo, run_local=run_local, ensure_stack=ensure_stack)
        )

    from scripts.ppe_autobuilder import collect_autobuilder_status, write_status_artifact

    final = collect_autobuilder_status(repo)
    write_status_artifact(repo, final)
    report["final"] = {
        "phase": final.get("phase"),
        "verdict": final.get("verdict"),
        "recommended_action": final.get("recommended_action"),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="VM loop-host bootstrap and recovery")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--run-local", action="store_true", help="Spawn run_ppe_local when verdict is RUN_LOCAL")
    ap.add_argument("--ensure-stack", action="store_true", help="Start headless stack when STACK_DOWN")
    ap.add_argument("--no-sync", action="store_true")
    ap.add_argument("--no-heal", action="store_true")
    ap.add_argument("--no-queue-repair", action="store_true")
    ap.add_argument("--no-detach-worktrees", action="store_true")
    ap.add_argument("--no-ensure-main", action="store_true")
    args = ap.parse_args(argv)

    report = bootstrap(
        args.repo_root.resolve(),
        sync_progress=not args.no_sync,
        heal=not args.no_heal,
        queue_repair=not args.no_queue_repair,
        run_local=args.run_local,
        ensure_stack=args.ensure_stack,
        detach_main_worktrees=not args.no_detach_worktrees,
        ensure_main=not args.no_ensure_main,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        final = report.get("final") or {}
        print(
            f"ppe_vm_bootstrap: phase={final.get('phase')} verdict={final.get('verdict')} "
            f"next={final.get('recommended_action')}"
        )
        for step in report.get("steps") or []:
            action = step.get("action")
            if action == "sync_slice_progress" and step.get("marked"):
                print(f"  sync: marked {', '.join(step['marked'])}")
            if action == "heal_artifacts" and step.get("changes"):
                for ch in step["changes"]:
                    print(f"  heal: {ch}")
            if action in ("heal_relay_state", "git_hygiene") and step.get("changes"):
                for ch in step["changes"]:
                    print(f"  {action}: {ch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
