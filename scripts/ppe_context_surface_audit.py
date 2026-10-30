"""Deterministic ChatGPT/GitHub/Codex context accounting.

Character counts are repository measurements. Estimated tokens use chars / 4 and
are explicitly approximate; they are not billing or hidden-context measurements.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_STARTER_REL = "docs/SOP/CHATGPT_PROJECT_STARTER.md"
CONTROL_PLANE_REL = "docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md"
ROUTING_REL = "docs/SOP/AGENT_ROUTING_V1.md"
CONTINUITY_REL = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
CHAPTER_INDEX_REL = "docs/SOP/CHAPTER_DOC_INDEX.json"
PHASE_BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"
ACTIVE_DIRECTION_REL = "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json"

OUT_JSON_REL = "artifacts/control_plane/CONTEXT_SURFACE_AUDIT_LATEST.json"
OUT_MD_REL = "artifacts/control_plane/CONTEXT_SURFACE_AUDIT_LATEST.md"

PROJECT_INSTRUCTION_CHAR_TARGET = 1_500
ROLE_CONTRACT_CHAR_TARGET = 800
STARTUP_BUNDLE_CHAR_TARGET = 2_500
CONTINUITY_CHAR_TARGET = 4_000

ROLE_HEADINGS = {
    "founder_setup": "### 1. Founder setup and collaboration",
    "charter": "### 2. Charter or product topic",
    "codex_build": "### 3. Codex implementation",
    "review": "### 4. Review and reconciliation",
}


@dataclass(frozen=True)
class ContextMeasure:
    id: str
    source: str
    chars: int
    est_tokens: int
    exists: bool = True
    note: str = ""


@dataclass(frozen=True)
class StartupBundle:
    id: str
    components: list[str]
    chars: int
    est_tokens: int
    variable_context_excluded: str


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _estimated_tokens(chars: int) -> int:
    return (max(chars, 0) + 3) // 4


def _read(repo: Path, rel: str) -> str:
    path = repo / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _measure(repo: Path, measure_id: str, rel: str, *, note: str = "") -> ContextMeasure:
    text = _read(repo, rel)
    exists = (repo / rel).is_file()
    return ContextMeasure(
        id=measure_id,
        source=rel,
        chars=len(text),
        est_tokens=_estimated_tokens(len(text)),
        exists=exists,
        note=note,
    )


def _first_fenced_text(text: str) -> str:
    match = re.search(r"```(?:text)?\s*\n(.*?)\n```", text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _fenced_after_heading(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    return _first_fenced_text(text[start:])


def measure_project_instructions(repo: Path) -> ContextMeasure:
    text = _first_fenced_text(_read(repo, PROJECT_STARTER_REL))
    return ContextMeasure(
        id="chatgpt_project_instructions",
        source=PROJECT_STARTER_REL,
        chars=len(text),
        est_tokens=_estimated_tokens(len(text)),
        exists=bool(text),
        note="Fenced Project-instruction text only; Markdown wrapper excluded.",
    )


def measure_role_contracts(repo: Path) -> dict[str, ContextMeasure]:
    control_plane = _read(repo, CONTROL_PLANE_REL)
    rows: dict[str, ContextMeasure] = {}
    for role_id, heading in ROLE_HEADINGS.items():
        text = _fenced_after_heading(control_plane, heading)
        rows[role_id] = ContextMeasure(
            id=f"role_contract_{role_id}",
            source=f"{CONTROL_PLANE_REL}#{heading.removeprefix('### ').strip()}",
            chars=len(text),
            est_tokens=_estimated_tokens(len(text)),
            exists=bool(text),
            note="Role starter block only; full control-plane canon excluded from fixed startup.",
        )
    return rows


def build_startup_bundles(
    project: ContextMeasure,
    roles: dict[str, ContextMeasure],
) -> dict[str, StartupBundle]:
    variable = {
        "founder_setup": "one relevant charter or operating issue",
        "charter": "one relevant program/charter or GitHub issue",
        "codex_build": "linked GitHub issue/task packet",
        "review": "target PR plus its charter/task packet",
    }
    bundles: dict[str, StartupBundle] = {}
    for role_id, role in roles.items():
        chars = project.chars + (1 if project.chars and role.chars else 0) + role.chars
        bundles[role_id] = StartupBundle(
            id=role_id,
            components=[project.id, role.id],
            chars=chars,
            est_tokens=_estimated_tokens(chars),
            variable_context_excluded=variable[role_id],
        )
    return bundles


def current_git_head(repo: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    head = proc.stdout.strip()
    return head if proc.returncode == 0 and re.fullmatch(r"[0-9a-fA-F]{40}", head) else None


def audit_continuity(repo: Path, *, head: str | None = None) -> dict[str, Any]:
    text = _read(repo, CONTINUITY_REL)
    if not text:
        return {
            "path": CONTINUITY_REL,
            "exists": False,
            "chars": 0,
            "est_tokens": 0,
            "embedded_head": None,
            "current_head": head,
            "freshness": "missing",
            "complete": False,
            "safe_to_load_first": False,
            "reasons": ["generated continuity brief is missing"],
            "safe_behavior": "Use GitHub main and current status/direction; regenerate through apply_control_closeout_v1.",
        }

    embedded_match = re.search(r"\*\*HEAD:\*\*\s*`([0-9a-fA-F]{7,40})`", text)
    embedded_head = embedded_match.group(1) if embedded_match else None
    current = head if head is not None else current_git_head(repo)

    blank_markers: list[str] = []
    marker_patterns = {
        "active_relay": r"\*\*Active relay:\*\*\s*``",
        "sprint": r"\*\*Sprint:\*\*\s*\[``\]\(\)",
        "plan": r"\*\*Plan:\*\*\s*\[``\]\(\)",
    }
    for name, pattern in marker_patterns.items():
        if re.search(pattern, text):
            blank_markers.append(name)

    machine_paths = sorted(set(re.findall(r"[A-Za-z]:[\\/][^\n`]+", text)))
    reasons: list[str] = []
    if not embedded_head:
        reasons.append("embedded HEAD is missing")
    if blank_markers:
        reasons.append(f"blank generated fields: {', '.join(blank_markers)}")
    if machine_paths:
        reasons.append("machine-specific absolute path present")

    if not current or not embedded_head:
        freshness = "unverifiable"
    elif current.lower().startswith(embedded_head.lower()) or embedded_head.lower().startswith(current.lower()):
        freshness = "fresh"
    else:
        freshness = "stale"
        reasons.append(f"embedded HEAD {embedded_head} differs from current HEAD {current}")

    complete = not blank_markers and embedded_head is not None
    safe = freshness == "fresh" and complete and not machine_paths
    return {
        "path": CONTINUITY_REL,
        "exists": True,
        "chars": len(text),
        "est_tokens": _estimated_tokens(len(text)),
        "embedded_head": embedded_head,
        "current_head": current,
        "freshness": freshness,
        "complete": complete,
        "blank_fields": blank_markers,
        "machine_specific_paths": machine_paths,
        "safe_to_load_first": safe,
        "reasons": reasons,
        "safe_behavior": (
            "Load only when fresh and complete. Otherwise use GitHub main plus current "
            "OPERATOR_STATUS/ACTIVE_PRODUCT_DIRECTION and regenerate through apply_control_closeout_v1."
        ),
    }


def build_context_surface_audit(repo: Path, *, head: str | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    project = measure_project_instructions(repo)
    roles = measure_role_contracts(repo)
    bundles = build_startup_bundles(project, roles)
    continuity = audit_continuity(repo, head=head)
    context_files = [
        _measure(repo, "control_plane_canon", CONTROL_PLANE_REL, note="On demand when coordination matters."),
        _measure(repo, "agent_routing_canon", ROUTING_REL, note="Role/topic routing reference."),
        _measure(repo, "generated_continuity", CONTINUITY_REL, note="Freshness-gated; not default startup."),
        _measure(repo, "chapter_doc_index", CHAPTER_INDEX_REL, note="On demand for chapter lookup."),
        _measure(repo, "phase_chapter_backlog", PHASE_BACKLOG_REL, note="On demand for explicit selection/closeout work."),
        _measure(repo, "active_product_direction", ACTIVE_DIRECTION_REL, note="Operator status context; not generic charter startup."),
    ]

    recommendations: list[str] = []
    verdict = "OK"
    if project.chars > PROJECT_INSTRUCTION_CHAR_TARGET:
        verdict = "WATCH"
        recommendations.append("Trim ChatGPT Project instructions below the recurring character target.")
    if any(row.chars > ROLE_CONTRACT_CHAR_TARGET for row in roles.values()):
        verdict = "WATCH"
        recommendations.append("Keep each role starter contract compact; move detailed policy to on-demand canon.")
    if any(row.chars > STARTUP_BUNDLE_CHAR_TARGET for row in bundles.values()):
        verdict = "WATCH"
        recommendations.append("Fixed startup bundle exceeds target; remove repeated status/index material.")
    if continuity.get("chars", 0) > CONTINUITY_CHAR_TARGET:
        verdict = "WATCH"
        recommendations.append("Generated continuity brief exceeds target; reduce repeated history and machine-local detail.")
    if not continuity.get("safe_to_load_first"):
        verdict = "WATCH"
        recommendations.append("Do not load generated continuity first until it is fresh, complete, and portable.")
    if not recommendations:
        recommendations.append("Keep Project instructions + one role contract fixed; load one relevant program/issue on demand.")

    return {
        "version": 1,
        "generated_at_utc": _utc_now(),
        "verdict": verdict,
        "estimation": "Estimated tokens are ceil(chars / 4); approximation only, not billing or hidden context.",
        "thresholds": {
            "project_instruction_char_target": PROJECT_INSTRUCTION_CHAR_TARGET,
            "role_contract_char_target": ROLE_CONTRACT_CHAR_TARGET,
            "startup_bundle_char_target": STARTUP_BUNDLE_CHAR_TARGET,
            "continuity_char_target": CONTINUITY_CHAR_TARGET,
        },
        "project_instructions": asdict(project),
        "role_contracts": {key: asdict(value) for key, value in roles.items()},
        "startup_bundles": {key: asdict(value) for key, value in bundles.items()},
        "context_files": [asdict(row) for row in context_files],
        "continuity": continuity,
        "recommendations": recommendations,
        "unmeasurable": [
            "proprietary hidden system or Project context",
            "actual ChatGPT/Codex subscription or API billing",
            "operator-local files or generated artifacts absent from this checkout",
            "variable issue, PR, program, logs, and conversation content",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Cross-surface context audit (latest)",
        "",
        f"**Generated:** {report['generated_at_utc']} · **Verdict:** `{report['verdict']}`",
        "",
        "> Character counts are deterministic repository measurements. Token estimates are chars / 4 approximations, not billing.",
        "",
        "## Fixed startup bundles",
        "",
        "| Role | Chars | Est. tokens | Variable context excluded |",
        "|---|---:|---:|---|",
    ]
    for role_id, row in report["startup_bundles"].items():
        lines.append(
            f"| `{role_id}` | {row['chars']} | ~{row['est_tokens']} | {row['variable_context_excluded']} |"
        )

    project = report["project_instructions"]
    lines.extend(
        [
            "",
            "## Project instructions and role contracts",
            "",
            f"- Project instructions: {project['chars']} chars (~{project['est_tokens']} tokens).",
        ]
    )
    for role_id, row in report["role_contracts"].items():
        lines.append(f"- `{role_id}` contract: {row['chars']} chars (~{row['est_tokens']} tokens).")

    lines.extend(["", "## Repository context surfaces", ""])
    for row in report["context_files"]:
        state = "present" if row["exists"] else "missing"
        lines.append(
            f"- `{row['source']}` — {row['chars']} chars (~{row['est_tokens']} tokens), {state}. {row['note']}"
        )

    continuity = report["continuity"]
    lines.extend(
        [
            "",
            "## Generated continuity safety",
            "",
            f"- Freshness: `{continuity['freshness']}`; complete: `{continuity['complete']}`; safe to load first: `{continuity['safe_to_load_first']}`.",
        ]
    )
    for reason in continuity.get("reasons") or []:
        lines.append(f"- {reason}")
    lines.append(f"- Safe behavior: {continuity['safe_behavior']}")

    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.extend(["", "## Unmeasurable", ""])
    lines.extend(f"- {item}" for item in report["unmeasurable"])
    return "\n".join(lines).rstrip() + "\n"


def write_artifacts(repo: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    json_path = repo / OUT_JSON_REL
    md_path = repo / OUT_MD_REL
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit ChatGPT/GitHub/Codex fixed context surfaces")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--fail-on-watch", action="store_true")
    parser.add_argument("--prune-stale", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-history", action="store_true", help=argparse.SUPPRESS)
    args, _unknown = parser.parse_known_args(argv)

    repo = args.repo_root.resolve()
    report = build_context_surface_audit(repo)
    if args.stdout:
        print(render_markdown(report), end="")
    else:
        json_path, md_path = write_artifacts(repo, report)
        print(f"ppe_context_surface_audit: verdict={report['verdict']}")
        print(f"ppe_context_surface_audit: wrote {json_path.relative_to(repo)}")
        print(f"ppe_context_surface_audit: wrote {md_path.relative_to(repo)}")
    if args.fail_on_watch and report["verdict"] in {"WATCH", "ESCALATE"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
