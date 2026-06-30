"""Token economy audit and perpetual budget monitoring."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_context_bands import score_text
from scripts.ppe_ide_build_starter import STARTER_LINE_ESCALATE, STARTER_LINE_TARGET, starter_line_band

CONTROL_PLANE_DIR = "artifacts/control_plane"
TOKEN_AUDIT_JSON = f"{CONTROL_PLANE_DIR}/TOKEN_AUDIT_LATEST.json"
TOKEN_AUDIT_MD = f"{CONTROL_PLANE_DIR}/TOKEN_AUDIT_LATEST.md"
TOKEN_HISTORY_JSONL = f"{CONTROL_PLANE_DIR}/token_economy_history.jsonl"
STARTER_DIR = "artifacts/orchestrator"
RULES_DIR = ".cursor/rules"
BUILD_WORKER_EVENTS_REL = "artifacts/orchestrator/build_worker_events.jsonl"

# Per docs/SOP/PPE_TOKEN_ECONOMY_MONITOR_V1.md
ALWAYS_ON_CHAR_TARGET = 8_000
ALWAYS_ON_CHAR_ESCALATE = 12_000


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
            "over_escalate": self.lines > STARTER_LINE_ESCALATE,
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
    verdict: str = "OK"

    def to_dict(self) -> dict[str, Any]:
        always_on = [r for r in self.rules if r.always_apply]
        always_chars = sum(r.chars for r in always_on)
        starter_lines = [s.lines for s in self.starters]
        over_target = sum(1 for s in self.starters if s.lines > STARTER_LINE_TARGET)
        over_escalate = sum(1 for s in self.starters if s.lines > STARTER_LINE_ESCALATE)
        return {
            "generated_at_utc": self.generated_at_utc,
            "verdict": self.verdict,
            "always_on_rules": [r.to_dict() for r in always_on],
            "load_on_demand_rules": [r.to_dict() for r in self.rules if not r.always_apply],
            "always_on_total_chars": always_chars,
            "always_on_est_tokens_per_turn": always_chars // 4,
            "always_on_char_target": ALWAYS_ON_CHAR_TARGET,
            "always_on_char_escalate": ALWAYS_ON_CHAR_ESCALATE,
            "starters": [s.to_dict() for s in self.starters],
            "starter_line_target": STARTER_LINE_TARGET,
            "starter_line_escalate": STARTER_LINE_ESCALATE,
            "starter_over_target_count": over_target,
            "starter_over_escalate_count": over_escalate,
            "starter_line_median": _median(starter_lines),
            "starter_line_max": max(starter_lines) if starter_lines else 0,
            "stale_starter_ids": list(self.stale_starter_ids),
            "build_worker": dict(self.build_worker),
            "operator_config": dict(self.operator_config),
            "recommendations": list(self.recommendations),
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _median(values: list[int]) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) // 2


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
        line_count = len(text.splitlines())
        rows.append(
            StarterAuditRow(
                path=path.relative_to(repo).as_posix(),
                lines=line_count,
                band=starter_line_band(line_count),
                slice_id=path.stem.replace("IDE_BUILD_STARTER_", "", 1),
            )
        )
    return rows


def audit_stale_starters(repo: Path) -> list[str]:
    from scripts.ppe_ide_build_starter import prune_starters_for_completed_chapters

    return prune_starters_for_completed_chapters(repo)


def audit_build_worker(repo: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        from scripts.ppe_build_worker import (
            codex_authenticated,
            load_build_worker_pref,
            read_build_worker_events,
            resolve_build_worker,
        )

        resolved = resolve_build_worker(repo)
        out["resolved"] = {k: resolved.get(k) for k in (
            "worker", "pref", "mode", "reason",
            "cursor_cli_available", "codex_cli_available",
            "cursor_cli_exhausted", "codex_cli_exhausted",
        )}
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


def _in_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() in ("1", "true", "yes")


def _headless_fallback_actionable(report: TokenAuditReport) -> bool:
    """IDE fallback WATCH only when operator profile expects headless BUILD on this machine."""
    if _in_ci():
        return False
    cfg = report.operator_config
    worker = str(cfg.get("buildWorker") or "").strip().lower()
    if not cfg.get("autoRemoteBuild") and worker not in ("codex", "cursor", "auto"):
        return False
    bw = report.build_worker.get("resolved") or {}
    if bw.get("mode") != "manual":
        return False
    reason = str(bw.get("reason") or "")
    if reason in ("manual_handoff", "near_zero_api_profile", "desktop_handoff"):
        return False
    return worker in ("codex", "cursor", "auto") or bool(cfg.get("autoRemoteBuild"))


def build_recommendations(report: TokenAuditReport) -> list[str]:
    recs: list[str] = []
    data = report.to_dict()
    always_chars = int(data["always_on_total_chars"])
    if always_chars > ALWAYS_ON_CHAR_ESCALATE:
        recs.append("ESCALATE: always-on rules exceed hard ceiling — demote to load-on-demand immediately.")
    elif always_chars > ALWAYS_ON_CHAR_TARGET:
        recs.append("WATCH: always-on rules heavy — keep only ppe-operator-core + ppe-desktop-vm-layout.")
    if data["starter_over_escalate_count"]:
        recs.append(
            f"ESCALATE: {data['starter_over_escalate_count']} starter(s) >{STARTER_LINE_ESCALATE} lines — regenerate."
        )
    elif data["starter_over_target_count"]:
        recs.append(
            f"WATCH: {data['starter_over_target_count']} starter(s) >{STARTER_LINE_TARGET} lines — regenerate."
        )
    if report.stale_starter_ids:
        recs.append(f"Remove {len(report.stale_starter_ids)} stale starter(s): token_audit.cmd --prune-stale")
    bw = report.build_worker.get("resolved") or {}
    if _headless_fallback_actionable(report):
        reason = str(bw.get("reason") or "")
        recs.append(f"Headless BUILD → IDE fallback ({reason}). Run verify_codex.cmd.")
    if bw.get("codex_cli_exhausted"):
        recs.append("Codex CLI exhausted — clear_build_worker_quota.cmd if false positive.")
    cfg = report.operator_config
    if cfg.get("stewardCharter"):
        recs.append("stewardCharter=true burns API credits — disable on local profile.")
    if cfg.get("skipAcp") is False:
        recs.append("skipAcp=false — relay will use ACP/API credits.")
    if not recs:
        recs.append("OK — maintain: new thread per BUILD, Codex-first, token_audit weekly.")
    return recs


def compute_verdict(report: TokenAuditReport) -> str:
    data = report.to_dict()
    if int(data["always_on_total_chars"]) > ALWAYS_ON_CHAR_ESCALATE:
        return "ESCALATE"
    if data["starter_over_escalate_count"]:
        return "ESCALATE"
    if _headless_fallback_actionable(report):
        return "WATCH"
    if int(data["always_on_total_chars"]) > ALWAYS_ON_CHAR_TARGET:
        return "WATCH"
    if data["starter_over_target_count"] or report.stale_starter_ids:
        return "WATCH"
    return "OK"


def build_token_audit(repo: Path) -> TokenAuditReport:
    report = TokenAuditReport(
        generated_at_utc=_utc_now(),
        rules=audit_rules(repo),
        starters=audit_starters(repo),
        stale_starter_ids=audit_stale_starters(repo),
        build_worker=audit_build_worker(repo),
        operator_config=audit_operator_config(repo),
    )
    report.recommendations = build_recommendations(report)
    try:
        from scripts.ppe_token_reconcile import billing_recommendation
        billing_rec = billing_recommendation(repo)
        if billing_rec:
            report.recommendations.append(billing_rec)
    except ImportError:
        pass
    report.verdict = compute_verdict(report)
    return report


def append_history_snapshot(repo: Path, report: TokenAuditReport) -> Path:
    repo = repo.resolve()
    path = repo / TOKEN_HISTORY_JSONL
    path.parent.mkdir(parents=True, exist_ok=True)
    data = report.to_dict()
    row = {
        "ts": report.generated_at_utc,
        "verdict": report.verdict,
        "always_on_chars": data["always_on_total_chars"],
        "always_on_est_tokens": data["always_on_est_tokens_per_turn"],
        "starter_count": len(report.starters),
        "starter_max_lines": data["starter_line_max"],
        "starter_over_target": data["starter_over_target_count"],
        "build_worker_reason": (data.get("build_worker") or {}).get("resolved", {}).get("reason"),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    return path


def read_history(repo: Path, *, limit: int = 12) -> list[dict[str, Any]]:
    path = repo / TOKEN_HISTORY_JSONL
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def render_token_audit_markdown(report: TokenAuditReport) -> str:
    data = report.to_dict()
    lines = [
        "# Token economy audit (latest)",
        "",
        f"**Generated:** {report.generated_at_utc} · **Verdict:** `{report.verdict}`",
        "",
        "## Fixed overhead",
        "",
        f"- Always-on: {data['always_on_total_chars']} chars (~{data['always_on_est_tokens_per_turn']} tok/turn)",
        f"- Targets: ≤{ALWAYS_ON_CHAR_TARGET} chars normal · ≤{ALWAYS_ON_CHAR_ESCALATE} escalate",
        "",
    ]
    for row in data["always_on_rules"]:
        lines.append(f"- `{row['name']}` — ~{row['est_tokens']} tok")
    lines.extend(["", "## IDE starters", ""])
    if data["starters"]:
        lines.append(
            f"- {len(data['starters'])} on disk · median {data['starter_line_median']} · max {data['starter_line_max']}"
            f" (target ≤{STARTER_LINE_TARGET})"
        )
        for row in data["starters"]:
            flag = " **OVER**" if row["over_target"] else ""
            lines.append(f"- `{row['slice_id']}` — {row['lines']}L ({row['band']}){flag}")
    else:
        lines.append("- None on disk.")
    bw = (data.get("build_worker") or {}).get("resolved") or {}
    if bw:
        lines.extend([
            "", "## Build worker", "",
            f"- `{bw.get('worker')}` · `{bw.get('mode')}` · reason `{bw.get('reason')}`",
        ])
    lines.extend(["", "## Recommendations", ""])
    for rec in data["recommendations"]:
        lines.append(f"- {rec}")
    lines.extend([
        "",
        "Monitor canon: [`PPE_TOKEN_ECONOMY_MONITOR_V1.md`](../SOP/PPE_TOKEN_ECONOMY_MONITOR_V1.md)",
    ])
    return "\n".join(lines).rstrip() + "\n"


def render_token_audit_markdown_for_repo(repo: Path, report: TokenAuditReport) -> str:
    md = render_token_audit_markdown(report)
    # inject history section
    history = read_history(repo, limit=8)
    if not history:
        return md
    extra = ["", "## Trend (recent audits)", ""]
    for row in history[-5:]:
        extra.append(
            f"- `{row.get('ts', '?')[:10]}` — {row.get('verdict')} · "
            f"~{row.get('always_on_est_tokens')} tok/turn · max starter {row.get('starter_max_lines')}L"
        )
    return md.rstrip() + "\n" + "\n".join(extra) + "\n"


def write_token_audit_artifacts(repo: Path, report: TokenAuditReport) -> tuple[Path, Path]:
    repo = repo.resolve()
    out_dir = repo / CONTROL_PLANE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = repo / TOKEN_AUDIT_JSON
    md_path = repo / TOKEN_AUDIT_MD
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_token_audit_markdown_for_repo(repo, report), encoding="utf-8")
    return json_path, md_path


def scan_token_friction(repo: Path) -> list[dict[str, Any]]:
    report = build_token_audit(repo)
    data = report.to_dict()
    signals: list[dict[str, Any]] = []
    if int(data["always_on_total_chars"]) > ALWAYS_ON_CHAR_TARGET:
        sev = "escalate" if int(data["always_on_total_chars"]) > ALWAYS_ON_CHAR_ESCALATE else "watch"
        signals.append({"id": "always-on-rules-heavy", "severity": sev,
                        "detail": f"{data['always_on_est_tokens_per_turn']} est tok/turn"})
    if data["starter_over_escalate_count"]:
        signals.append({"id": "starters-over-escalate", "severity": "escalate",
                        "detail": f"{data['starter_over_escalate_count']} starter(s) >{STARTER_LINE_ESCALATE} lines"})
    elif data["starter_over_target_count"]:
        signals.append({"id": "starters-over-target", "severity": "watch",
                        "detail": f"{data['starter_over_target_count']} starter(s) >{STARTER_LINE_TARGET} lines"})
    if report.stale_starter_ids:
        signals.append({"id": "stale-ide-starters", "severity": "info",
                        "detail": f"{len(report.stale_starter_ids)} stale starter(s)"})
    if _headless_fallback_actionable(report):
        resolved = (data.get("build_worker") or {}).get("resolved") or {}
        signals.append({"id": "headless-build-fallback", "severity": "escalate",
                        "detail": f"IDE fallback: {resolved.get('reason')}"})
    return signals


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Token economy audit + monitor")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--prune-stale", action="store_true")
    ap.add_argument("--no-history", action="store_true", help="Skip appending history jsonl")
    ap.add_argument("--fail-on-watch", action="store_true", help="Exit 1 on WATCH or ESCALATE")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.prune_stale:
        from scripts.ppe_ide_build_starter import prune_starters_for_completed_chapters
        removed = prune_starters_for_completed_chapters(repo)
        print(f"ppe_token_audit: pruned {len(removed)} stale starter(s)" if removed else
              "ppe_token_audit: no stale starters")

    report = build_token_audit(repo)
    if args.stdout:
        print(render_token_audit_markdown_for_repo(repo, report), end="")
        return 0

    if not args.no_history:
        append_history_snapshot(repo, report)
    json_path, md_path = write_token_audit_artifacts(repo, report)
    print(f"ppe_token_audit: verdict={report.verdict} always-on ~{report.to_dict()['always_on_est_tokens_per_turn']} tok/turn")
    print(f"ppe_token_audit: wrote {json_path.relative_to(repo)}")
    print(f"ppe_token_audit: wrote {md_path.relative_to(repo)}")
    for rec in report.recommendations[:3]:
        print(f"ppe_token_audit: {rec}")
    if args.fail_on_watch and report.verdict in ("WATCH", "ESCALATE"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
