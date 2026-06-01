"""
Write a stable, human-readable completion report for orchestrator/relay wrapper runs.

Outputs:
  - artifacts/orchestrator/LAST_RUN_REPORT.json
  - artifacts/orchestrator/LAST_RUN_REPORT.md

This is intentionally best-effort: it scans the orchestrator worktree tree for the newest relay_result.json.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from scripts.ui_smoke_diagnose import diagnose_stop_for_review, format_diagnosis


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _find_newest_relay_result(repo_root: Path, worktree_hint: Optional[Path]) -> Optional[Path]:
    wt_root = repo_root / "_worktrees" / "acp_orchestrator"
    if not wt_root.is_dir():
        return None

    candidates: list[Path] = []
    if worktree_hint and worktree_hint.is_dir():
        candidates.extend(worktree_hint.glob("artifacts/relay/runs/*/relay_result.json"))
        candidates.extend(worktree_hint.glob("artifacts\\relay\\runs\\*\\relay_result.json"))

    # Global scan fallback (bounded-ish): only under acp_orchestrator worktrees.
    candidates.extend(wt_root.glob("*/artifacts/relay/runs/*/relay_result.json"))
    candidates.extend(wt_root.glob("*\\artifacts\\relay\\runs\\*\\relay_result.json"))

    existing = [p for p in candidates if p.is_file()]
    if not existing:
        return None
    return max(existing, key=lambda p: p.stat().st_mtime)


def _worktree_from_build_branch(repo_root: Path, build_branch: str) -> Optional[Path]:
    # Accept either:
    # - full branch like "build/auto/<leaf>"
    # - or just "<leaf>" (some callers may pass only the worktree folder name)
    leaf = build_branch.split("/")[-1].split("\\")[-1].strip()
    if not leaf:
        return None
    p = repo_root / "_worktrees" / "acp_orchestrator" / leaf
    return p if p.is_dir() else None


def _infer_attention(*, exit_code: int, relay: Optional[dict[str, Any]]) -> tuple[bool, str, str]:
    """
    Returns: (awaiting_user, status_bucket, next_action)
    """
    if exit_code != 0:
        return True, "error_or_stopped", "Investigate wrapper/orchestrator failure (non-zero exit). Open LAST_RUN_REPORT.md and the terminal output."

    if not relay:
        return True, "unknown", "Relay result not found on disk yet (or path scan failed). Check newest worktree under _worktrees/acp_orchestrator and artifacts/relay/runs/."

    stop_raw = relay.get("stop_condition")
    stop_code = ""
    if isinstance(stop_raw, dict):
        stop_code = str(stop_raw.get("code") or stop_raw.get("id") or "")
    else:
        stop_code = str(stop_raw or "").strip()
    slice_id = str(relay.get("slice_id") or "").upper()
    if stop_code == "SCOPE_AMBIGUITY" and "PRODUCT" in slice_id:
        build_branch = str(relay.get("build_branch") or relay.get("buildBranch") or "")
        branch_note = f" Commit on `{build_branch}`." if build_branch else ""
        return (
            True,
            "product_ide_build_required",
            "Product slice under deterministic relay: BUILD in Cursor IDE using docs/SOP/BUILD_PACKET_TEMPLATE.md "
            f"(sprint spec + AGENT_CONTINUITY_BRIEF).{branch_note} "
            "Then `mark_ide_product_ready.cmd <sliceId>` and `run_ppe_local.cmd` from repo root.",
        )

    decision = str(relay.get("stop_condition") or "").strip()
    # relay_result uses nested decision sometimes? Usually top-level has safe_to_continue etc.
    safe_to_continue = relay.get("safe_to_continue")
    ready_for_control_closeout = relay.get("ready_for_control_closeout")

    promotion = relay.get("promotion") if isinstance(relay.get("promotion"), dict) else {}
    performed = bool(promotion.get("performed")) if promotion else False

    # Heuristic: STOP_FOR_REVIEW often corresponds to exit_code 20 from orchestrator, but wrapper passes orchestrator exit code.
    # We use relay notes + promotion fields when present.
    if ready_for_control_closeout is False and performed is False:
        return (
            True,
            "stop_for_review_or_procedural",
            "Relay indicates steward follow-up (often baseline promotion / closeout). If baseline is checked out elsewhere, fast-forward baseline from the baseline worktree, then update MVP1_FRONTIER pointers.",
        )

    if safe_to_continue is True and ready_for_control_closeout is True:
        return (
            False,
            "continue",
            "Relay CONTINUE: post_relay_continue runs apply_control_closeout_v1 when phase plan has closeout; "
            "see docs/SOP/AGENT_CONTINUITY_BRIEF.md.",
        )

    return True, "review", "Relay payload is ambiguous; read LAST_RUN_REPORT.json and relay_result.json for details."


def _context_band_hint(repo_root: Path, sprint_spec_rel: str | None) -> str | None:
    if not sprint_spec_rel:
        return None
    p = repo_root / sprint_spec_rel.replace("\\", "/")
    if not p.is_file():
        return None
    line_count = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
    if line_count > 400:
        return "ESCALATE (sprint spec line count > 400 — prefer links over inline paste)"
    if line_count > 200:
        return "WATCH (sprint spec line count > 200)"
    return "NORMAL"


def _build_context_ritual(repo_root: Path) -> dict[str, Any]:
    return {
        "open_new_cursor_thread": True,
        "load_only": ["docs/SOP/AGENT_CONTINUITY_BRIEF.md"],
        "rules_doc": "docs/CONTEXT_RULES.md",
        "build_packet_template": "docs/SOP/BUILD_PACKET_TEMPLATE.md",
        "do_not_paste": [
            "orchestrator stdout",
            "full pytest log",
            "full git diff",
            "HANDOFF gate inline",
        ],
        "summary": (
            "After this run: open a new Cursor thread; @ AGENT_CONTINUITY_BRIEF.md only; "
            "read LAST_RUN_REPORT for steward actions. See docs/CONTEXT_RULES.md."
        ),
    }


def _enrich_from_steward_summary(repo_root: Path, report: dict[str, Any]) -> None:
    path = repo_root / "artifacts" / "orchestrator" / "steward_phase_summary.json"
    if not path.is_file():
        return
    try:
        summary = _read_json(path)
    except Exception:
        return
    stopped = summary.get("stopped") if isinstance(summary.get("stopped"), dict) else {}
    slice_id = stopped.get("sliceId")
    results = summary.get("results") if isinstance(summary.get("results"), list) else []
    last = results[-1] if results else {}
    run = last.get("run") if isinstance(last.get("run"), dict) else {}
    detail = str(run.get("detail") or "")
    if detail:
        report["orchestrator_detail"] = detail.replace("\r\n", "\n").strip()
    if slice_id:
        report["stopped_slice_id"] = slice_id
    status = str(run.get("status") or "")
    if status == "STOP_FOR_REVIEW" and "rule 6" in detail.lower():
        report["status_bucket"] = "stop_for_review_smoke_env"
        report["next_action"] = (
            "UI smoke failed with environment-sensitive classification (relay rule 6). "
            "Read smoke diagnosis below; fix harness/wrapper scenario alignment or retry on a stable network."
        )


def _enrich_smoke_diagnosis(repo_root: Path, report: dict[str, Any]) -> None:
    relay = report.get("relay_result") if isinstance(report.get("relay_result"), dict) else None
    exit_code = int(report.get("wrapper_exit_code") or 0)
    diagnosis = diagnose_stop_for_review(repo_root=repo_root, exit_code=exit_code, relay=relay)
    if diagnosis is None:
        return
    report["smoke_diagnosis"] = diagnosis.as_dict()
    if report.get("awaiting_user"):
        report["next_action"] = diagnosis.suggested_fix
    report["status_bucket"] = report.get("status_bucket") or "stop_for_review_smoke_env"


def _enrich_from_manifest(repo_root: Path, report: dict[str, Any]) -> None:
    manifest_path = repo_root / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    if not manifest_path.is_file():
        return
    try:
        manifest = _read_json(manifest_path)
    except Exception:
        return
    report["manifest_path"] = "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    report["manifest_status"] = manifest.get("status")
    sprint = str(manifest.get("sprintSpecPath") or report.get("sprint_spec") or "").strip()
    if sprint:
        report["context_band_hint"] = _context_band_hint(repo_root, sprint)
    report["context_ritual"] = _build_context_ritual(repo_root)


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# PPE last run report ({report.get('ts_utc')})")
    lines.append("")
    lines.append(f"- **kind**: `{report.get('kind')}`")
    if report.get("slice_id"):
        lines.append(f"- **slice_id**: `{report.get('slice_id')}`")
    if report.get("plan_path"):
        lines.append(f"- **plan_path**: `{report.get('plan_path')}`")
    lines.append(f"- **wrapper_exit_code**: `{report.get('wrapper_exit_code')}`")
    lines.append(f"- **status_bucket**: `{report.get('status_bucket')}`")
    lines.append(f"- **awaiting_user**: `{report.get('awaiting_user')}`")
    lines.append("")
    lines.append("## Next action")
    lines.append("")
    lines.append(str(report.get("next_action") or "").strip())
    lines.append("")
    lines.append("## Pointers")
    lines.append("")
    lines.append(f"- **worktree_path**: `{report.get('worktree_path')}`")
    lines.append(f"- **relay_result_path**: `{report.get('relay_result_path')}`")
    lines.append(f"- **steward_summary_path**: `{report.get('steward_summary_path')}`")
    if report.get("manifest_path"):
        lines.append(f"- **manifest_path**: `{report.get('manifest_path')}`")
        lines.append(f"- **manifest_status**: `{report.get('manifest_status')}`")
    if report.get("context_band_hint"):
        lines.append(f"- **context_band_hint**: `{report.get('context_band_hint')}`")
    if report.get("orchestrator_detail"):
        lines.append(f"- **orchestrator_detail**: `{report.get('orchestrator_detail')}`")
    smoke = report.get("smoke_diagnosis")
    if isinstance(smoke, dict) and smoke.get("summary"):
        lines.append("")
        lines.append("## Smoke diagnosis")
        lines.append("")
        lines.append(f"- **category**: `{smoke.get('category')}`")
        lines.append(f"- **summary**: {smoke.get('summary')}")
        lines.append(f"- **likely_cause**: {smoke.get('likely_cause')}")
        lines.append(f"- **suggested_fix**: {smoke.get('suggested_fix')}")
        if smoke.get("auto_retry_command"):
            lines.append(f"- **retry**: `{smoke.get('auto_retry_command')}`")
    ritual = report.get("context_ritual")
    if isinstance(ritual, dict):
        lines.append("")
        lines.append("## Cursor context ritual")
        lines.append("")
        lines.append(str(ritual.get("summary") or "").strip())
        lines.append("")
        lines.append(f"- Rules: `{ritual.get('rules_doc')}`")
        lines.append(f"- BUILD packets: `{ritual.get('build_packet_template')}`")
        load_only = ritual.get("load_only") or []
        if load_only:
            lines.append(f"- Load only: `{load_only[0]}`")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--kind", required=True, choices=["slice", "phase", "phase_raw"])
    ap.add_argument("--exit-code", type=int, required=True)
    ap.add_argument("--slice-id", default="")
    ap.add_argument("--plan-path", default="")
    ap.add_argument("--baseline-branch", default="")
    ap.add_argument("--build-branch", default="")
    ap.add_argument("--sprint-spec", default="")
    ap.add_argument("--declared-plane", default="")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_dir = repo_root / "artifacts" / "orchestrator"
    out_dir.mkdir(parents=True, exist_ok=True)

    wt_hint = _worktree_from_build_branch(repo_root, args.build_branch) if args.build_branch else None
    relay_path = _find_newest_relay_result(repo_root, wt_hint)
    relay: Optional[dict[str, Any]] = None
    if relay_path and relay_path.is_file():
        try:
            relay = _read_json(relay_path)  # type: ignore[assignment]
        except Exception:
            relay = None

    awaiting_user, status_bucket, next_action = _infer_attention(exit_code=args.exit_code, relay=relay)

    steward_summary = repo_root / "artifacts" / "orchestrator" / "steward_phase_summary.json"

    report: dict[str, Any] = {
        "ts_utc": _utc_now_iso(),
        "kind": args.kind,
        "wrapper_exit_code": args.exit_code,
        "slice_id": args.slice_id or None,
        "plan_path": args.plan_path or None,
        "baseline_branch": args.baseline_branch or None,
        "build_branch": args.build_branch or None,
        "sprint_spec": args.sprint_spec or None,
        "declared_plane": args.declared_plane or None,
        "worktree_path": str(wt_hint) if wt_hint else None,
        "relay_result_path": str(relay_path) if relay_path else None,
        "steward_summary_path": str(steward_summary) if steward_summary.is_file() else None,
        "relay_result": relay,
        "status_bucket": status_bucket,
        "awaiting_user": awaiting_user,
        "next_action": next_action,
    }
    _enrich_from_manifest(repo_root, report)
    _enrich_from_steward_summary(repo_root, report)
    _enrich_smoke_diagnosis(repo_root, report)

    (out_dir / "LAST_RUN_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out_dir / "LAST_RUN_REPORT.md").write_text(_render_md(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
