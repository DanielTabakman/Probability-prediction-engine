"""Generate one-file IDE BUILD starter (LOAD-ALWAYS bundle)."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from scripts.ppe_build_packet import build_packet_text
from scripts.ppe_context_bands import advisory_actions, classify_line_count, score_text, worst_band
from scripts.ppe_manifest import load_phase_plan
from scripts.repo_layer_paths import find_slice_in_plan, resolve_slice_layer_scope

STARTER_DIR = "artifacts/orchestrator"
CONTINUITY_BRIEF = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
CONTINUITY_EXCERPT_LINES = 40
ACCEPTANCE_MAX_LINES = 80


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
    """Closeout steps agents must run after implementing a product slice."""
    norm_plan = phase_plan.replace("\\", "/").strip()
    return "\n".join(
        [
            "## When done (required)",
            "",
            "Execute in order — do not skip:",
            "",
            "1. `python scripts/run_pushable_gate.py`",
            "2. `git commit` on plan `buildBranch` (create branch if needed)",
            f"3. `mark_ide_product_ready.cmd {slice_id} {norm_plan}`",
            "4. `run_ppe_local.cmd`",
            "",
            "Execute autonomously; do not ask for confirmation.",
        ]
    )


def format_ide_build_resume(slice_id: str, phase_plan: str) -> str:
    from scripts.ppe_operator_hint import PPE_GO_HINT

    rel = starter_path(slice_id)
    return (
        f"1. **You:** `{PPE_GO_HINT}`\n"
        f"2. **Manual fallback:** `@` `{rel}` — then commit, `mark_ide_product_ready.cmd {slice_id}`, "
        f"`run_ppe_local.cmd`.\n"
        f"3. Starter: `python scripts/ppe_ide_build_starter.py --slice-id {slice_id} "
        f'--phase-plan {phase_plan}`'
    )


def _continuity_excerpt(repo: Path, max_lines: int = CONTINUITY_EXCERPT_LINES) -> str:
    p = repo / CONTINUITY_BRIEF
    if not p.is_file():
        return f"_({CONTINUITY_BRIEF} not found — regenerate via closeout.)_\n"
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    excerpt = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        excerpt += f"\n\n_(truncated — full file: `{CONTINUITY_BRIEF}`)_"
    return excerpt


def _slice_map_row(sprint_text: str, slice_id: str) -> str | None:
    in_table = False
    for line in sprint_text.splitlines():
        if line.strip().lower().startswith("## slice map"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if in_table and slice_id in line and "|" in line:
            return line.strip()
    return None


def _acceptance_excerpt(sprint_text: str, sprint_path: str, *, max_lines: int = ACCEPTANCE_MAX_LINES) -> str:
    parts: list[str] = []
    for line in sprint_text.splitlines():
        if line.strip().lower().startswith("## slice map"):
            break
        parts.append(line)
    body = "\n".join(parts).strip()
    if not body:
        return f"_No acceptance sections before Slice map — read `{sprint_path}`._"
    lines = body.splitlines()
    if len(lines) > max_lines:
        truncated = "\n".join(lines[:max_lines])
        return f"{truncated}\n\n_(truncated — full spec: `{sprint_path}`)_"
    return body


def _context_ritual_bullets() -> str:
    return "\n".join(
        [
            "- Open a **new** Cursor Agent thread for this BUILD (not the steward thread).",
            "- Do **not** paste orchestrator stdout, full pytest logs, or full `git diff`.",
            "- Include **AGENT CONTINUITY** block in your return (see BUILD packet template).",
            "- Relay BUILD uses a fresh ACP worker; this IDE thread is separate.",
            "- After chapter closeout: new thread with `AGENT_CONTINUITY_BRIEF.md` only.",
        ]
    )


def build_starter_md(repo: Path, *, slice_id: str, phase_plan: str) -> str:
    norm_plan = phase_plan.replace("\\", "/").strip()
    plan = load_phase_plan(repo, norm_plan)
    sl = find_slice_in_plan(plan, slice_id)
    if sl is None:
        raise SystemExit(f"slice_id not in plan: {slice_id}")

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

    sprint_text = ""
    sprint_lines: int | None = None
    if sprint_path:
        sp = repo / sprint_path.replace("\\", "/")
        if sp.is_file():
            sprint_text = sp.read_text(encoding="utf-8", errors="replace")
            sprint_lines = len(sprint_text.splitlines())

    slice_row = _slice_map_row(sprint_text, slice_id) if sprint_text else None
    if not slice_row:
        slice_row = f"| {slice_id} | {declared_plane} | {scope.layer_preset or '?'} | (see phase plan) |"

    acceptance = (
        _acceptance_excerpt(sprint_text, sprint_path)
        if sprint_text and sprint_path
        else f"_Read sprint spec at `{sprint_path}`._"
    )
    packet = build_packet_text(repo, slice_id=slice_id, phase_plan=norm_plan)

    try:
        from scripts.ppe_focus_gate import evaluate_focus_gate, format_ide_focus_block

        focus = evaluate_focus_gate(repo, norm_plan)
        focus_section = format_ide_focus_block(
            tier=focus.tier,
            urgent_bypass=focus.urgent_bypass,
        )
    except ImportError:
        focus_section = ""

    starter_body_parts = [
        f"# IDE BUILD starter — `{slice_id}`",
        "",
        f"**As-of HEAD:** `{head}` · **Plane:** `{declared_plane}` · "
        f"**Layer preset:** `{scope.layer_preset}` · **Build branch:** `{build_branch}`",
        "",
    ]
    if focus_section:
        starter_body_parts.extend([focus_section, ""])
    starter_body_parts.extend([
        "## Continuity excerpt",
        "",
        _continuity_excerpt(repo),
        "",
        "## Slice intent",
        "",
        slice_row,
        "",
        "## Acceptance excerpt",
        "",
        acceptance,
        "",
        "## Slim BUILD packet",
        "",
        "```text",
        packet.rstrip(),
        "```",
        "",
        "## Context ritual",
        "",
        _context_ritual_bullets(),
        "",
        format_build_closeout_section(slice_id=slice_id, phase_plan=norm_plan),
        "",
    ])

    full_md = "\n".join(starter_body_parts)
    starter_scored = score_text(full_md)
    sprint_band = "NORMAL"
    if sprint_lines is not None:
        sprint_band = classify_line_count(sprint_lines)

    overall = worst_band(starter_scored["band"], sprint_band)
    band_section = [
        "## Context band",
        "",
        f"- **Starter file:** `{starter_scored['band']}` ({starter_scored['line_count']} lines)",
    ]
    if sprint_lines is not None:
        band_section.append(f"- **Sprint spec:** `{sprint_band}` ({sprint_lines} lines — `{sprint_path}`)")
    band_section.append(f"- **Overall (advisory):** `{overall}`")
    actions = advisory_actions(overall)
    if actions:
        band_section.append("")
        band_section.append("**Advisory actions:**")
        for action in actions:
            band_section.append(f"- {action}")

    return full_md + "\n".join(band_section) + "\n"


def write_starter(repo: Path, *, slice_id: str, phase_plan: str) -> Path:
    md = build_starter_md(repo, slice_id=slice_id, phase_plan=phase_plan)
    rel = starter_path(slice_id)
    out = repo / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    try:
        from scripts.ppe_active_ide_slice import write_active_slice

        write_active_slice(
            repo,
            slice_id=slice_id,
            phase_plan_path=phase_plan,
            starter_path=rel,
        )
    except ImportError:
        pass
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate IDE BUILD starter markdown bundle.")
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
    print(f"ppe_ide_build_starter: wrote {out}")
    print(f"ppe_ide_build_starter: @ {out.relative_to(repo)} in a new Cursor thread")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
