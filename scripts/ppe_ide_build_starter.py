"""Generate minimal IDE BUILD starter (smallest LOAD-ALWAYS bundle)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_context_bands import classify_line_count, score_text
from scripts.ppe_manifest import load_phase_plan
from scripts.repo_layer_paths import find_slice_in_plan, resolve_slice_layer_scope

STARTER_DIR = "artifacts/orchestrator"
CONTINUITY_BRIEF = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
PRESETS_REL = "docs/SOP/REPO_LAYER_PATH_PREFIXES.json"

# Token budget (see docs/SOP/PPE_TOKEN_ECONOMY_MONITOR_V1.md)
STARTER_LINE_TARGET = 65
STARTER_LINE_ESCALATE = 80
RESOLVE_FP_RE = re.compile(r"<!--\s*starter-resolve-fp:\s*([a-f0-9]{8,64})\s*-->")


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
    from scripts.ppe_operator_hint import WHAT_NEXT_HINT

    rel = starter_path(slice_id)
    return (
        f"1. **You:** `{WHAT_NEXT_HINT}`\n"
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


def _compact_doc_resolve(repo: Path, phase_plan: str) -> str:
    try:
        from scripts.ppe_chapter_mode import plan_chapter_id
        from scripts.sop_discovery_core import chapter_doc_bundle

        norm = phase_plan.replace("\\", "/").strip()
        cid = plan_chapter_id(norm)
        bundle = chapter_doc_bundle(repo, chapter_id=cid, plan_path=norm)
        build = bundle.get("load_for_build") or []
        skip = (bundle.get("do_not_load") or [])[:2]
        lines = [f"**Doc resolve:** `python scripts/resolve_sop.py --chapter {cid} --json`"]
        if build:
            lines.append("**load_for_build:** " + " · ".join(f"`{p}`" for p in build[:3]))
        if skip:
            lines.append("**skip:** " + " · ".join(f"`{p}`" for p in skip))
        return "\n".join(lines)
    except Exception:
        return ""


def doc_resolve_fingerprint_payload(repo: Path, phase_plan: str) -> dict[str, Any] | None:
    """Stable payload for starter doc-resolve freshness (mirrors resolve_sop --chapter)."""
    try:
        from scripts.ppe_chapter_mode import plan_chapter_id
        from scripts.sop_discovery_core import chapter_doc_bundle

        norm = phase_plan.replace("\\", "/").strip()
        cid = plan_chapter_id(norm)
        bundle = chapter_doc_bundle(repo, chapter_id=cid, plan_path=norm)
        build = [_norm_path(p) for p in (bundle.get("load_for_build") or []) if str(p).strip()]
        skip = [_norm_path(p) for p in (bundle.get("do_not_load") or [])[:2] if str(p).strip()]
        return {"chapter_id": cid, "load_for_build": build, "skip": skip}
    except Exception:
        return None


def _norm_path(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def doc_resolve_fingerprint(repo: Path, phase_plan: str) -> str | None:
    payload = doc_resolve_fingerprint_payload(repo, phase_plan)
    if not payload:
        return None
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def format_resolve_fingerprint_line(fingerprint: str) -> str:
    return f"<!-- starter-resolve-fp: {fingerprint} -->"


def parse_starter_resolve_fingerprint(text: str) -> str | None:
    match = RESOLVE_FP_RE.search(text or "")
    return match.group(1) if match else None


def extract_doc_resolve_block(text: str) -> str:
    lines: list[str] = []
    in_block = False
    for line in (text or "").splitlines():
        if line.startswith("**Doc resolve:**"):
            in_block = True
        elif in_block and line.startswith("**") and not line.startswith("**load") and not line.startswith("**skip"):
            break
        if in_block:
            lines.append(line.rstrip())
    return "\n".join(lines).strip()


def starter_doc_resolve_stale(
    repo: Path,
    *,
    slice_id: str,
    phase_plan: str,
    starter_text: str | None = None,
) -> tuple[bool, str]:
    """Return (stale, reason) for a starter's embedded doc-resolve bundle."""
    expected_fp = doc_resolve_fingerprint(repo, phase_plan)
    if not expected_fp:
        return False, "no doc-resolve payload"
    rel = starter_path(slice_id)
    text = starter_text
    if text is None:
        path = repo / rel
        if not path.is_file():
            return False, "missing starter"
        text = path.read_text(encoding="utf-8")
    embedded_fp = parse_starter_resolve_fingerprint(text)
    if embedded_fp:
        if embedded_fp != expected_fp:
            return True, "fingerprint mismatch"
        return False, "fresh"
    expected_block = _compact_doc_resolve(repo, phase_plan)
    if not expected_block:
        return False, "no doc-resolve block"
    actual_block = extract_doc_resolve_block(text)
    if not actual_block:
        return True, "missing doc-resolve block"
    if actual_block != expected_block:
        return True, "doc-resolve block drift"
    return False, "legacy block matches"


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
        ]
    )
    doc_resolve = _compact_doc_resolve(repo, norm_plan)
    if doc_resolve:
        parts.insert(-2, doc_resolve)
        fp = doc_resolve_fingerprint(repo, norm_plan)
        if fp:
            parts.insert(-2, format_resolve_fingerprint_line(fp))
        parts.insert(-2, "")
    parts.extend(
        [
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


def regenerate_starters_for_plan(repo: Path, phase_plan: str) -> list[str]:
    """Write IDE BUILD starters for pending product slices when a plan is READY."""
    from scripts.ppe_ide_product_ready import completed_product_slice_ids
    from scripts.ppe_slice_worker_mode import infer_slice_kind

    norm = phase_plan.replace("\\", "/").strip()
    if not norm:
        return []
    try:
        from scripts.ppe_queue_health import chapter_marked_complete_in_repo

        if chapter_marked_complete_in_repo(repo, norm):
            return []
    except ImportError:
        pass
    try:
        plan = load_phase_plan(repo, norm)
    except (FileNotFoundError, OSError):
        return []

    completed = completed_product_slice_ids(repo, plan_path=norm)
    written: list[str] = []
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        sid = str(sl.get("sliceId") or "").strip()
        if not sid or infer_slice_kind(sid, sl) != "product":
            continue
        if sid in completed:
            continue
        try:
            write_starter(repo, slice_id=sid, phase_plan=norm)
            written.append(sid)
        except Exception as exc:
            print(
                f"ppe_ide_build_starter: regenerate skip {sid}: {exc}",
                file=sys.stderr,
            )
    return written


def plan_regen_ready_starters(repo: Path) -> dict[str, Any]:
    """Plans IDE BUILD starter regen for READY queue rows (missing or stale doc-resolve)."""
    from scripts.ppe_ide_product_ready import next_pending_product_slice
    from scripts.ppe_queue import load_queue

    repo = repo.resolve()
    pending: list[dict[str, Any]] = []
    try:
        queue = load_queue(repo)
    except (FileNotFoundError, OSError):
        return {"pending_count": 0, "pending": [], "stale_count": 0, "missing_count": 0}
    for item in queue.get("items") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").upper() != "READY":
            continue
        plan = str(item.get("planPath") or "").replace("\\", "/").strip()
        if not plan:
            continue
        try:
            slice_id = next_pending_product_slice(repo, plan_path=plan)
        except (FileNotFoundError, OSError, ValueError):
            continue
        if not slice_id:
            continue
        rel = starter_path(slice_id)
        path = repo / rel
        if not path.is_file():
            pending.append({"plan_path": plan, "slice_id": slice_id, "reason": "missing starter"})
            continue
        stale, reason = starter_doc_resolve_stale(repo, slice_id=slice_id, phase_plan=plan)
        if stale:
            pending.append(
                {
                    "plan_path": plan,
                    "slice_id": slice_id,
                    "reason": "stale doc-resolve",
                    "stale_detail": reason,
                }
            )
    missing = sum(1 for row in pending if row.get("reason") == "missing starter")
    stale = sum(1 for row in pending if row.get("reason") == "stale doc-resolve")
    return {
        "pending_count": len(pending),
        "pending": pending,
        "missing_count": missing,
        "stale_count": stale,
    }


def plan_stale_ready_starters(repo: Path) -> dict[str, Any]:
    """READY queue starters with outdated doc-resolve bundles."""
    plan = plan_regen_ready_starters(repo)
    stale_rows = [row for row in plan.get("pending") or [] if row.get("reason") == "stale doc-resolve"]
    return {
        "pending_count": len(stale_rows),
        "pending": stale_rows,
    }


def regenerate_starters_for_ready_queue(repo: Path) -> dict[str, list[str]]:
    """Regenerate product-slice starters for READY queue plans that need them."""
    plan = plan_regen_ready_starters(repo)
    out: dict[str, list[str]] = {}
    for row in plan.get("pending") or []:
        if not isinstance(row, dict):
            continue
        plan_path = str(row.get("plan_path") or "").strip()
        slice_id = str(row.get("slice_id") or "").strip()
        if not plan_path or not slice_id:
            continue
        try:
            write_starter(repo, slice_id=slice_id, phase_plan=plan_path)
            out.setdefault(plan_path, []).append(slice_id)
        except Exception as exc:
            print(
                f"ppe_ide_build_starter: regen skip {slice_id}: {exc}",
                file=sys.stderr,
            )
    return out


def warn_if_stale_ready_starters(repo: Path, *, max_lines: int = 5) -> list[dict[str, Any]]:
    """Print non-blocking warnings for stale READY starters; return pending rows."""
    repo = repo.resolve()
    plan = plan_stale_ready_starters(repo)
    rows = plan.get("pending") or []
    if not rows:
        return []
    print(
        "WARN: stale IDE BUILD starters for READY queue (doc-resolve drift):",
        file=sys.stderr,
    )
    for row in rows[:max_lines]:
        sid = str(row.get("slice_id") or "")
        plan_path = str(row.get("plan_path") or "")
        print(
            f"  [{sid}] {plan_path} — {row.get('stale_detail') or 'stale doc-resolve'}",
            file=sys.stderr,
        )
        print(
            f"         → generate_ide_build_starter.cmd {sid} {plan_path}",
            file=sys.stderr,
        )
    extra = len(rows) - min(max_lines, len(rows))
    if extra > 0:
        print(
            f"  ... {extra} more — `sop_discovery_maintenance.cmd --regen-ready-starters --apply`",
            file=sys.stderr,
        )
    return rows


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
