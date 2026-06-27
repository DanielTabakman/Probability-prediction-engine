"""Token economy audit — fixed overhead, starters, build-worker routing."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scripts.ppe_context_bands import score_text

CONTROL_PLANE_DIR = "artifacts/control_plane"
TOKEN_AUDIT_JSON = f"{CONTROL_PLANE_DIR}/TOKEN_AUDIT_LATEST.json"
TOKEN_AUDIT_MD = f"{CONTROL_PLANE_DIR}/TOKEN_AUDIT_LATEST.md"
STARTER_DIR = "artifacts/orchestrator"
RULES_DIR = ".cursor/rules"
BUILD_WORKER_EVENTS_REL = "artifacts/orchestrator/build_worker_events.jsonl"
STARTER_LINE_TARGET = 100
ALWAYS_ON_CHAR_TARGET = 10_000


@dataclass
class RuleAuditRow:
    name: str
    always_apply: bool
    lines: int
    chars: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "always_apply": self.always_apply,
            "lines": self.lines,
            "chars": self.chars,
            "est_tokens": self.chars // 4,
        }


@dataclass
class StarterAuditRow:
    path: str
    lines: int
    band: str
    slice_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "lines": self.lines,
            "band": self.band,
            "slice_id": self.slice_id,
            "over_target": self.lines > STARTER_LINE_TARGET,
        }


@dataclass
class TokenAuditReport:
    generated_at_utc: str
    rules: list[RuleAuditRow] = field(default_factory=list)
    starters: list[StarterAuditRow] = field(default_factory=list)
    stale_starter_ids: list[str] = field(default_factory=list)
    build_worker: dict[str, Any] = field(default_factory=dict)
    operator_config: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        always_on = [r for r in self.rules if r.always_apply]
        always_chars = sum(r.chars for r in always_on)
        starter_lines = [s.lines for s in self.starters]
        return {
            "generated_at_utc": self.generated_at_utc,
            "always_on_rules": [r.to_dict() for r in always_on],
            "load_on_demand_rules": [r.to_dict() for r in self.rules if not r.always_apply],
            "always_on_total_chars": always_chars,
            "always_on_est_tokens_per_turn": always_chars // 4,
            "always_on_char_target": ALWAYS_ON_CHAR_TARGET,
            "starters": [s.to_dict() for s in self.starters],
            "starter_line_target": STARTER_LINE_TARGET,
            "starter_line_median": _median(starter_lines),
            "starter_line_max": max(starter_lines) if starter_lines else 0,
            "stale_starter_ids": list(self.stale_starter_ids),
            "build_worker": dict(self.build_worker),
            "operator_config": dict(self.operator_config),
            "recommendations": list(self.recommendations),
        }


def _median(values: list[int]) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) // 2


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_rule(path: Path) -> RuleAuditRow:
    text = path.read_text(encoding="utf-8", errors="replace")
    always = bool(re.search(r"alwaysApply:\s*true", text))
    return RuleAuditRow(name=path.name, always_apply=always, lines=len(text.splitlines()), chars=len(text))


def audit_rules(repo: Path) -> list[RuleAuditRow]:
    rules_dir = repo / RULES_DIR
    if not rules_dir.is_dir():
        return []
    return [_parse_rule(p) for p in sorted(rules_dir.glob("*.mdc"))]


def audit_starters(repo: Path) -> list[StarterAuditRow]:
    starter_root = repo / STARTER_DIR
    if not starter_root.is_dir():
        return []
    rows: list[StarterAuditRow] = []
    for path in sorted(starter_root.glob("IDE_BUILD_STARTER_*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        scored = score_text(text)
        name = path.stem.replace("IDE_BUILD_STARTER_", "", 1)
        rows.append(
            StarterAuditRow(
                path=path.relative_to(repo).as_posix(),
                lines=int(scored["line_count"]),
                band=str(scored["band"]),
                slice_id=name,
            )
        )
    return rows


def audit_stale_starters(repo: Path) -> list[str]:
    try:
        from scripts.ppe_ide_build_starter import prune_starters_for_completed_chapters

        return prune_starters_for_completed_chapters(repo)
    except ImportError:
        return []


def audit_build_worker(repo: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        from scripts.ppe_build_worker import (
            codex_authenticated,
            codex_cli_exhausted,
            load_build_worker_pref,
            read_build_worker_events,
            resolve_build_worker,
        )

        resolved = resolve_build_worker(repo)
        out["resolved"] = {
            k: resolved.get(k)
            for k in (
                "worker",
                "pref",
                "mode",
                "reason",
                "cursor_cli_available",
                "codex_cli_available",
                "cursor_cli_exhausted",
                "codex_cli_exhausted",
            )
        }
        out["pref"] = load_build_worker_pref(repo)
        out["codex_authenticated"] = codex_authenticated()
        out["recent_events"] = read_build_worker_events(repo, limit=10)
    except ImportError as exc:
        out["error"] = str(exc)
    return out


def audit_operator_config(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        guards = cfg.get("guards") if isinstance(cfg.get("guards"), dict) else {}
        handoff = cfg.get("ideHandoff") if isinstance(cfg.get("ideHandoff"), dict) else {}
        return {
            "skipAcp": cfg.get("skipAcp"),
            "stewardCharter": cfg.get("stewardCharter"),
            "autoRemoteBuild": cfg.get("autoRemoteBuild"),
            "buildWorker": handoff.get("buildWorker"),
            "preferIdeOverCli": handoff.get("preferIdeOverCli"),
            "stopOnContextWatch": guards.get("stopOnContextWatch"),
            "stopOnContextEscalate": guards.get("stopOnContextEscalate"),
        }
    except ImportError:
        return {}


def build_recommendations(report: TokenAuditReport) -> list[str]:
    recs: list[str] = []
    always_on = [r for r in report.rules if r.always_apply]
    always_chars = sum(r.chars for r in always_on)
    if always_chars > ALWAYS_ON_CHAR_TARGET:
        recs.append(
            f"Always-on rules ~{always_chars // 4} tok/turn (target ≤{ALWAYS_ON_CHAR_TARGET // 4}) — "
            "demote load-on-demand rules; keep ppe-operator-core + ppe-desktop-vm-layout only."
        )
    over = [s for s in report.starters if s.lines > STARTER_LINE_TARGET]
    if over:
        recs.append(
            f"{len(over)} IDE starter(s) exceed {STARTER_LINE_TARGET} lines — regenerate after slim starter pass."
        )
    if report.stale_starter_ids:
        recs.append(
            f"Remove {len(report.stale_starter_ids)} stale starter(s) for completed chapters "
            "(run token_audit --prune-stale)."
        )
    bw = report.build_worker.get("resolved") or {}
    reason = str(bw.get("reason") or "")
    if reason in ("codex_unavailable", "no_headless_worker", "cursor_quota_exhausted"):
        recs.append(f"Headless BUILD falling back to IDE ({reason}) — run verify_codex.cmd / verify_build_worker.cmd.")
    if bw.get("codex_cli_exhausted"):
        recs.append("Codex CLI marked exhausted — clear_build_worker_quota.cmd if false positive.")
    if bw.get("cursor_cli_exhausted") and bw.get("mode") == "manual":
        recs.append("Cursor CLI exhausted — product BUILD will use IDE Agent (high token cost).")
    cfg = report.operator_config
    if cfg.get("stewardCharter"):
        recs.append("stewardCharter=true on local profile — disable to avoid API burn.")
    if cfg.get("skipAcp") is False:
        recs.append("skipAcp=false — ACP relay will consume API credits.")
    if not recs:
        recs.append("No critical token friction signals — keep one thread per slice and Codex-first BUILD.")
    return recs


def build_token_audit(repo: Path) -> TokenAuditReport:
    repo = repo.resolve()
    report = TokenAuditReport(
        generated_at_utc=_utc_now(),
        rules=audit_rules(repo),
        starters=audit_starters(repo),
        stale_starter_ids=audit_stale_starters(repo),
        build_worker=audit_build_worker(repo),
        operator_config=audit_operator_config(repo),
    )
    report.recommendations = build_recommendations(report)
    return report


def render_token_audit_markdown(report: TokenAuditReport) -> str:
    data = report.to_dict()
    lines = [
        "# Token economy audit (latest)",
        "",
        f"**Generated:** {report.generated_at_utc}",
        "",
        "## Fixed overhead (always-on rules)",
        "",
        f"- **Total:** {data['always_on_total_chars']} chars (~{data['always_on_est_tokens_per_turn']} tok/turn)",
        f"- **Target:** ≤{ALWAYS_ON_CHAR_TARGET} chars (~{ALWAYS_ON_CHAR_TARGET // 4} tok/turn)",
        "",
    ]
    for row in data["always_on_rules"]:
        lines.append(f"- `{row['name']}` — {row['lines']} lines, ~{row['est_tokens']} tok")
    lines.extend(["", "## IDE BUILD starters", ""])
    if data["starters"]:
        lines.append(
            f"- Count: {len(data['starters'])} · median {data['starter_line_median']} lines · "
            f"max {data['starter_line_max']} (target ≤{STARTER_LINE_TARGET})"
        )
        for row in data["starters"]:
            flag = " **OVER**" if row["over_target"] else ""
            lines.append(f"- `{row['slice_id']}` — {row['lines']} lines ({row['band']}){flag}")
    else:
        lines.append("- No IDE_BUILD_STARTER files on disk.")
    if data["stale_starter_ids"]:
        lines.extend(["", "## Stale starters (completed chapters)", ""])
        for sid in data["stale_starter_ids"]:
            lines.append(f"- `{sid}`")
    bw = data.get("build_worker") or {}
    resolved = bw.get("resolved") or {}
    if resolved:
        lines.extend(
            [
                "",
                "## Build worker routing",
                "",
                f"- Worker: `{resolved.get('worker')}` · mode: `{resolved.get('mode')}` · reason: `{resolved.get('reason')}`",
                f"- Codex auth: `{bw.get('codex_authenticated')}` · Codex exhausted: `{resolved.get('codex_cli_exhausted')}`",
                f"- Cursor exhausted: `{resolved.get('cursor_cli_exhausted')}`",
            ]
        )
    lines.extend(["", "## Recommendations", ""])
    for rec in data["recommendations"]:
        lines.append(f"- {rec}")
    lines.append("")
    lines.append("Canon: [`docs/SOP/PPE_TOKEN_ECONOMY_V1.md`](../SOP/PPE_TOKEN_ECONOMY_V1.md)")
    return "\n".join(lines).rstrip() + "\n"


def write_token_audit_artifacts(repo: Path, report: TokenAuditReport) -> tuple[Path, Path]:
    repo = repo.resolve()
    out_dir = repo / CONTROL_PLANE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = repo / TOKEN_AUDIT_JSON
    md_path = repo / TOKEN_AUDIT_MD
    payload = json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
    json_path.write_text(payload, encoding="utf-8")
    md_path.write_text(render_token_audit_markdown(report), encoding="utf-8")
    return json_path, md_path


def scan_token_friction(repo: Path) -> list[dict[str, Any]]:
    """Compact signals for workflow radar integration."""
    report = build_token_audit(repo)
    data = report.to_dict()
    signals: list[dict[str, Any]] = []
    if data["always_on_total_chars"] > ALWAYS_ON_CHAR_TARGET:
        signals.append(
            {
                "id": "always-on-rules-heavy",
                "severity": "watch",
                "detail": f"{data['always_on_est_tokens_per_turn']} est tok/turn from always-on rules",
            }
        )
    over = sum(1 for s in data["starters"] if s.get("over_target"))
    if over:
        signals.append(
            {
                "id": "starters-over-budget",
                "severity": "watch",
                "detail": f"{over} starter(s) exceed {STARTER_LINE_TARGET} lines",
            }
        )
    if report.stale_starter_ids:
        signals.append(
            {
                "id": "stale-ide-starters",
                "severity": "info",
                "detail": f"{len(report.stale_starter_ids)} stale starter file(s)",
            }
        )
    resolved = (data.get("build_worker") or {}).get("resolved") or {}
    if resolved.get("mode") == "manual" and resolved.get("reason") not in ("manual_handoff", "near_zero_api_profile"):
        signals.append(
            {
                "id": "headless-build-fallback",
                "severity": "escalate",
                "detail": f"IDE handoff fallback: {resolved.get('reason')}",
            }
        )
    if resolved.get("codex_cli_exhausted"):
        signals.append(
            {
                "id": "codex-cli-exhausted",
                "severity": "watch",
                "detail": "Codex CLI quota exhausted — Cursor IDE BUILD likely",
            }
        )
    return signals


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Token economy audit report")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--stdout", action="store_true", help="Print markdown to stdout only")
    ap.add_argument("--prune-stale", action="store_true", help="Remove starters for completed chapters")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.prune_stale:
        from scripts.ppe_ide_build_starter import prune_starters_for_completed_chapters

        removed = prune_starters_for_completed_chapters(repo)
        if removed:
            print(f"ppe_token_audit: pruned {len(removed)} stale starter(s)")
        else:
            print("ppe_token_audit: no stale starters to prune")

    report = build_token_audit(repo)
    if args.stdout:
        print(render_token_audit_markdown(report), end="")
        return 0

    json_path, md_path = write_token_audit_artifacts(repo, report)
    print(f"ppe_token_audit: always-on ~{report.to_dict()['always_on_est_tokens_per_turn']} tok/turn")
    print(f"ppe_token_audit: wrote {json_path.relative_to(repo)}")
    print(f"ppe_token_audit: wrote {md_path.relative_to(repo)}")
    for rec in report.recommendations[:3]:
        print(f"ppe_token_audit: {rec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
