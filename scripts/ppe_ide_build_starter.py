"""Generate minimal IDE BUILD starter (smallest LOAD-ALWAYS bundle)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from scripts.ppe_context_bands import classify_line_count, score_text
from scripts.ppe_manifest import load_phase_plan
from scripts.repo_layer_paths import find_slice_in_plan, resolve_slice_layer_scope

STARTER_DIR = "artifacts/orchestrator"
CONTINUITY_BRIEF = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
PRESETS_REL = "docs/SOP/REPO_LAYER_PATH_PREFIXES.json"

# Token budget (see docs/SOP/PPE_TOKEN_ECONOMY_MONITOR_V1.md)
STARTER_LINE_TARGET = 65
STARTER_LINE_ESCALATE = 80


def _git_head(repo: Path) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip() or None


def starter_path(slice_id: str) -> str:
    safe = slice_id.replace("/", "_").replace("\\", "_")
    return f"{STARTER_DIR}/IDE_BUILD_STARTER_{safe}.md"


def format_build_closeout_section(*, slice_id: str, phase_plan: str) -> str:
    norm_plan = phase_plan.replace("\\", "/").strip()
    return "\n".join(
        [
            "## When done",
            "",
            f"1. `python scripts/run_pushable_gate.py` → commit on `{norm_plan}` build branch",
            f"2. `mark_ide_product_ready.cmd {slice_id} {norm_plan}` → `run_ppe_local.cmd`",
            "",
            "New thread only · no pasted logs · execute autonomously.",
        ]
    )


def format_ide_build_resume(slice_id: str, phase_plan: str) -> str:
    from scripts.ppe_operator_hint import PPE_GO_HINT

    rel = starter_path(slice_id)
    return (
        f"1. **You:** `{PPE_GO_HINT}`\n"
        f"2. **Manual:** `@` `{rel}` → commit → `mark_ide_product_ready.cmd {slice_id}` → `run_ppe_local.cmd`.\n"
        f"3. Regenerate: `generate_ide_build_starter.cmd {slice_id} {phase_plan}`"
    )


def _compact_focus(repo: Path, phase_plan: str) -> str:
    try:
        from scripts.ppe_focus_gate import evaluate_focus_gate

        focus = evaluate_focus_gate(repo, phase_plan)
        urgent = " urgent-ok" if focus.urgent_bypass else ""
        return f"**Focus:** {focus.tier}{urgent} — no asset/execution/platform drift."
    except ImportError:
        return "**Focus:** stay inside touchSet / layer preset."


def _compact_acceptance(sl: dict, sprint_path: str) -> str:
    raw = sl.get("acceptance")
    if isinstance(raw, list) and raw:
        lines = ["**Acceptance:**"]
        for item in raw[:6]:
            if not isinstance(item, dict):
                continue
            aid = str(item.get("id") or "").strip()
            check = str(item.get("check") or "").strip()
            if aid and check:
                lines.append(f"- `{aid}` — {check}")
            elif check:
                lines.append(f"- {check}")
        if len(raw) > 6:
            lines.append(f"- _(+{len(raw) - 6} more in phase plan)_")
        return "\n".join(lines)
    if sprint_path:
        return f"**Acceptance:** `{sprint_path}` (slice map + acceptance sections)."
    return "**Acceptance:** see phase plan sprint spec."


def _compact_scope(scope) -> str:
    touch = scope.touch_set or ()
    if touch:
        listed = ", ".join(f"`{p}`" for p in touch[:8])
        if len(touch) > 8:
            listed += f" (+{len(touch) - 8} more in plan)"
        scope_line = f"touchSet: {listed}"
    else:
        scope_line = f"preset `{scope.layer_preset}` — paths in `{PRESETS_REL}`"
    forbid = scope.forbidden_paths[:2]
    forbid_tail = ""
    if len(scope.forbidden_paths) > 2:
        forbid_tail = f" (+{len(scope.forbidden_paths) - 2} more)"
    forbid_line = ", ".join(f"`{p}`" for p in forbid) + forbid_tail if forbid else "see preset"
    return f"**Scope:** {scope_line} · **Forbidden:** {forbid_line}"


def _compact_loads(*, touch: tuple[str, ...], sprint_path: str, phase_plan: str) -> str:
    paths: list[str] = []
    for p in touch[:5]:
        if p not in paths:
            paths.append(p)
    for extra in (sprint_path, phase_plan, CONTINUITY_BRIEF):
        if extra and extra not in paths:
            paths.append(extra)
    joined = " · ".join(f"`{p}`" for p in paths[:7])
    return f"**Load:** {joined}"


def starter_line_band(line_count: int) -> str:
    if line_count > STARTER_LINE_ESCALATE:
        return "ESCALATE"
    if line_count > STARTER_LINE_TARGET:
        return "WATCH"
    return "NORMAL"


def _closeout_only_banner(repo: Path, *, slice_id: str, phase_plan: str) -> str | None:
    try:
        from scripts.ppe_chapter_mode import (
            is_closeout_only_chapter,
            plan_chapter_id,
            slice_product_on_main,
        )
        from scripts.ppe_slice_worker_mode import infer_slice_kind
    except ImportError:
        return None

    norm_plan = phase_plan.replace("\\", "/").strip()
    plan = load_phase_plan(repo, norm_plan)
    sl = find_slice_in_plan(plan, slice_id)
    kind = infer_slice_kind(slice_id, sl)
    if kind != "product":
        return None
    on_main = slice_product_on_main(repo, slice_id=slice_id, phase_plan=norm_plan)
    closeout = is_closeout_only_chapter(
        repo,
        plan_path=norm_plan,
        chapter_name=plan_chapter_id(norm_plan),
    )
    if not on_main and not closeout:
        return None
    return (
        "> **CLOSEOUT_ONLY** — product touchSet already on `main`. "
        "**Do NOT re-implement this slice.** Finish marker/closeout via operator thread only."
    )


def build_starter_md(repo: Path, *, slice_id: str, phase_plan: str) -> str:
    norm_plan = phase_plan.replace("\\", "/").strip()
    plan = load_phase_plan(repo, norm_plan)
    sl = find_slice_in_plan(plan, slice_id)
    if sl is None:
        raise SystemExit(f"slice_id not in plan: {slice_id}")

    closeout_banner = _closeout_only_banner(repo, slice_id=slice_id, phase_plan=norm_plan)

    declared_plane = str(sl.get("declaredPlane") or "EVIDENCE-PLANE")
    scope = resolve_slice_layer_scope(
        repo,
        slice_obj=sl,
        slice_id=slice_id,
        declared_plane=declared_plane,
    )
    build_branch = str(sl.get("buildBranch") or f"build/auto/{slice_id}").strip()
    sprint_path = str(sl.get("sprintSpecPath") or plan.get("sprintSpecPath") or "").strip()
    head = _git_head(repo) or "unknown"
    touch = tuple(scope.touch_set or ())

    parts = [
        "IDE BUILD thread. THREAD_ROLE: ide_build.",
        "Load only this starter — do not read OPERATOR_STATUS.",
        "",
        f"# IDE BUILD — `{slice_id}`",
        "",
    ]
    if closeout_banner:
        parts.extend([closeout_banner, ""])
    parts.extend(
        [
            f"`{head[:12]}` · `{declared_plane}` · `{scope.layer_preset}` · branch `{build_branch}`",
            "",
            _compact_focus(repo, norm_plan),
            _compact_scope(scope),
            _compact_acceptance(sl, sprint_path),
            _compact_loads(touch=touch, sprint_path=sprint_path, phase_plan=norm_plan),
            "",
            "_New Agent thread · this file only · no orchestrator/pytest/diff paste._",
            "",
            format_build_closeout_section(slice_id=slice_id, phase_plan=norm_plan),
            "",
        ]
    )
    return "\n".join(parts)


def write_starter(repo: Path, *, slice_id: str, phase_plan: str) -> Path:
    md = build_starter_md(repo, slice_id=slice_id, phase_plan=phase_plan)
    scored = score_text(md)
    line_count = int(scored["line_count"])
    band = starter_line_band(line_count)
    if band == "ESCALATE":
        print(
            f"ppe_ide_build_starter: WARNING starter {line_count} lines (ESCALATE >{STARTER_LINE_ESCALATE})",
            file=sys.stderr,
        )
    elif band == "WATCH":
        print(
            f"ppe_ide_build_starter: note starter {line_count} lines (WATCH >{STARTER_LINE_TARGET})",
            file=sys.stderr,
        )
    out = repo / starter_path(slice_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    return out


def prune_starters_for_plan(repo: Path, phase_plan: str) -> list[str]:
    norm_plan = phase_plan.replace("\\", "/").strip()
    if not norm_plan:
        return []
    try:
        plan = load_phase_plan(repo, norm_plan)
    except (FileNotFoundError, OSError):
        return []
    removed: list[str] = []
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        sid = str(sl.get("sliceId") or "").strip()
        if not sid:
            continue
        path = repo / starter_path(sid)
        if path.is_file():
            path.unlink()
            removed.append(sid)
    return removed


def prune_starters_for_completed_chapters(repo: Path) -> list[str]:
    from scripts.ppe_queue_health import chapter_marked_complete_in_repo

    sop = repo / "docs" / "SOP" / "PHASE_PLANS"
    if not sop.is_dir():
        return []
    removed: list[str] = []
    for plan_file in sorted(sop.glob("*_relay.json")):
        rel = str(plan_file.relative_to(repo)).replace("\\", "/")
        if not chapter_marked_complete_in_repo(repo, rel):
            continue
        for sid in prune_starters_for_plan(repo, rel):
            if sid not in removed:
                removed.append(sid)
    return removed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate minimal IDE BUILD starter.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--slice-id", required=True)
    ap.add_argument("--phase-plan", required=True)
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.stdout:
        print(build_starter_md(repo, slice_id=args.slice_id, phase_plan=args.phase_plan), end="")
        return 0

    out = write_starter(repo, slice_id=args.slice_id, phase_plan=args.phase_plan)
    lines = len(out.read_text(encoding="utf-8").splitlines())
    print(f"ppe_ide_build_starter: wrote {out} ({lines} lines, band={starter_line_band(lines)})")
    print(f"ppe_ide_build_starter: @ {out.relative_to(repo)} in a new Cursor thread")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
