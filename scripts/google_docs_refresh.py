"""google_docs_refresh_v1 — control-plane Google Docs maintenance at cycle boundaries.

Canonical human command: refresh Google Docs.
Protocol: docs/SOP/GOOGLE_DOCS_REFRESH_V1.md (repo) and PPE Master (Google).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

REPORT_JSON_REL = "artifacts/control_plane/google_docs_refresh_report.json"
REPORT_MD_REL = "artifacts/control_plane/google_docs_refresh_report.md"
MSOS_REPORT_REL = "artifacts/control_plane/msos_sync_report.json"
CANON_REL = "docs/VISION/PPE_MASTER_MVP1.md"
BRIEF_REL = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
CONTINUITY_JSON_REL = "artifacts/control_plane/continuity_brief.json"
WITNESS_REL = "docs/SOP/VALIDATION_DEPLOY_WITNESS.md"

NAMING_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("MSOS live mirror", "low", "Prefer display title: PPE / MSOS Repo Truth — Live Mirror"),
    ("Google MSOS doc", "low", "Prefer: PPE / MSOS Repo Truth — Live Mirror (Google Doc)"),
    ("MSOS Google Doc", "low", "Prefer: PPE / MSOS Repo Truth — Live Mirror"),
    (
        "MSOS Repo Truth",
        "medium",
        "Use full title PPE / MSOS Repo Truth — Live Mirror unless referring to env MSOS_REPO_TRUTH_*",
    ),
)

SCAN_SUFFIXES = {".md", ".py", ".cmd", ".ps1", ".jsonc"}
SCAN_ROOTS = ("docs", "scripts", ".cursor/rules")
SKIP_DIR_NAMES = {"__pycache__", ".pytest_cache", "artifacts", "node_modules"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return None


def _git_state(repo: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"branch": None, "head": None, "working_tree_clean": None, "upstream": None, "ahead": None, "behind": None}

    def run(*args: str) -> str | None:
        try:
            p = subprocess.run(
                ["git", *args],
                cwd=repo,
                capture_output=True,
                text=True,
                check=True,
            )
            return p.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    out["branch"] = run("branch", "--show-current")
    out["head"] = run("rev-parse", "HEAD")
    status = run("status", "--porcelain")
    out["working_tree_clean"] = status == "" if status is not None else None
    out["upstream"] = run("rev-parse", "--abbrev-ref", "@{u}")
    counts = run("rev-list", "--left-right", "--count", "HEAD...@{u}")
    if counts:
        parts = counts.split()
        if len(parts) == 2:
            out["behind"], out["ahead"] = int(parts[0]), int(parts[1])
    return out


def _scan_naming_drift(repo: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for root_name in SCAN_ROOTS:
        root = repo / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.suffix not in SCAN_SUFFIXES and path.name not in ("mcp.json",):
                continue
            if "MSOS_REPO_TRUTH" in path.name:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = path.relative_to(repo).as_posix()
            for needle, severity, note in NAMING_CHECKS:
                if needle not in text:
                    continue
                if needle == "MSOS Repo Truth":
                    for line in text.splitlines():
                        if "MSOS Repo Truth" not in line:
                            continue
                        if "Live Mirror" in line or "MSOS_REPO_TRUTH" in line:
                            continue
                        findings.append(
                            {
                                "path": rel,
                                "pattern": needle,
                                "severity": severity,
                                "note": note,
                            }
                        )
                    continue
                findings.append(
                    {
                        "path": rel,
                        "pattern": needle,
                        "severity": severity,
                        "note": note,
                    }
                )
    # De-dupe by path+pattern
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, str]] = []
    for f in findings:
        key = (f["path"], f["pattern"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return sorted(unique, key=lambda x: (x["severity"], x["path"]))


def _master_import_gap(repo: Path) -> bool:
    canon = repo / CANON_REL
    if not canon.is_file():
        return True
    return "GOOGLE_DOCS_REFRESH" not in canon.read_text(encoding="utf-8", errors="replace")


def _continuity_staleness(repo: Path) -> list[str]:
    warnings: list[str] = []
    brief = repo / BRIEF_REL
    cont = _read_json(repo / CONTINUITY_JSON_REL)
    if not brief.is_file() or not cont:
        return warnings
    brief_text = brief.read_text(encoding="utf-8", errors="replace")
    m_brief = re.search(r"\|\s*Chapter\s*\|\s*([^|]+)\|", brief_text, re.I)
    closeout = cont.get("closeout") or {}
    title = (closeout.get("chapter_title") or "").strip()
    if m_brief and title:
        brief_ch = m_brief.group(1).strip()
        if title not in brief_ch and brief_ch not in title:
            warnings.append(f"continuity_brief.json chapter {title!r} vs brief {brief_ch!r}")
    gen = cont.get("generated_at")
    if gen and "2026-05-20" in gen and "onboarding" in brief_text.lower():
        warnings.append(f"continuity_brief.json generated_at {gen} may be stale vs onboarding closeout")
    return warnings


def _witness(repo: Path, *, skip_http: bool) -> dict[str, Any]:
    witness: dict[str, Any] = {"repo_doc": WITNESS_REL, "http": {}}
    wpath = repo / WITNESS_REL
    if wpath.is_file():
        text = wpath.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"\*\*Git SHA on VPS\*\*\s*\|\s*\*\*`([^`]+)`", text)
        if m:
            witness["vps_sha_doc"] = m.group(1)
    if skip_http:
        witness["http_skipped"] = True
        return witness
    for url in ("https://marketstructureos.com", "https://app.marketstructureos.com"):
        try:
            req = Request(url, headers={"User-Agent": "ppe-google-docs-refresh/1"})
            with urlopen(req, timeout=20) as resp:
                witness["http"][url] = {"status": resp.status, "ok": 200 <= resp.status < 400}
        except URLError as e:
            witness["http"][url] = {"ok": False, "error": str(e)}
    return witness


def _run_control_validation(repo: Path) -> dict[str, Any]:
    """Lightweight validation for control-plane refresh (no full product pytest)."""
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(repo)}
    results: dict[str, Any] = {"py_compile": [], "pytest": None}
    for rel in (
        "scripts/google_docs_refresh.py",
        "scripts/sync_msos_repo_truth.py",
        "scripts/msos/build_snapshot.py",
    ):
        path = repo / rel
        if not path.is_file():
            continue
        proc = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            cwd=repo,
            capture_output=True,
            text=True,
            env=env,
        )
        results["py_compile"].append({"path": rel, "ok": proc.returncode == 0})
    pytest_targets = [
        repo / "tests/test_google_docs_refresh.py",
        repo / "tests/test_msos_snapshot.py",
        repo / "tests/test_sync_msos_repo_truth.py",
    ]
    existing = [str(p.relative_to(repo)).replace("\\", "/") for p in pytest_targets if p.is_file()]
    if existing:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", *existing],
            cwd=repo,
            capture_output=True,
            text=True,
            env=env,
        )
        results["pytest"] = {
            "paths": existing,
            "ok": proc.returncode == 0,
            "summary": (proc.stdout or "").splitlines()[-1] if proc.stdout else proc.stderr,
        }
    return results


def _freshness_verdict(
    git: dict[str, Any],
    prev_msos: dict[str, Any] | None,
    msos: dict[str, Any] | None,
    staleness: list[str],
    drift: list[dict[str, str]],
) -> str:
    if git.get("working_tree_clean") is False:
        return "STALE_LOCAL_TREE"
    if staleness:
        return "STALE_CONTINUITY_ARTIFACTS"
    head = git.get("head")
    if prev_msos and msos and head:
        prev_head = prev_msos.get("head_sha")
        if prev_head and prev_head != head and not msos.get("skipped"):
            return "FRESH_MIRROR_UPDATED"
        if prev_head == head and msos and msos.get("skipped"):
            return "MIRROR_UNCHANGED_SKIP"
    if msos and msos.get("passed") and not msos.get("skipped"):
        return "FRESH"
    if msos and msos.get("skipped"):
        return "MIRROR_SKIP_OK"
    medium = [d for d in drift if d.get("severity") == "medium"]
    if medium:
        return "NAMING_DRIFT_REVIEW"
    return "ACCEPTABLE"


def _recommended_next_move(repo: Path) -> tuple[str, str]:
    brief = repo / BRIEF_REL
    if brief.is_file():
        text = brief.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"\|\s*Next SELECTION\s*\|\s*\[([^\]]+)\]", text, re.I)
        if m:
            return f"Steward SELECTION per {m.group(1).strip()}", "high"
        if "await steward" in text.lower() or "Active BUILD" in text:
            m2 = re.search(r"## Active BUILD\s*\n\n\*\*([^*]+)\*\*", text)
            if m2:
                return m2.group(1).strip(), "high"
    return "Read AGENT_CONTINUITY_BRIEF.md and MVP1_FRONTIER.md before next BUILD", "medium"


def _format_report_md(report: dict[str, Any]) -> str:
    lines = [
        "# GOOGLE_DOCS_REFRESH report",
        "",
        f"**Generated:** {report.get('generated_at')}",
        f"**Trigger:** {report.get('trigger')}",
        "",
        "## Summary",
        "",
        f"- **Branch / HEAD:** `{report.get('branch')}` / `{report.get('head')}`",
        f"- **Working tree:** {'clean' if report.get('working_tree_clean') else 'dirty'}",
        f"- **Freshness verdict:** {report.get('freshness_verdict')}",
        f"- **Live Mirror regenerated:** {report.get('live_mirror_regenerated')}",
        f"- **Master import gap (repo):** {'yes' if report.get('master_import_needed') else 'no'}",
        f"- **Recommended next move:** {report.get('recommended_next_move')} ({report.get('confidence')} confidence)",
        "",
        "## Delta since last refresh",
        "",
        report.get("delta_summary") or "_none_",
        "",
        "## Validation",
        "",
        f"```json\n{json.dumps(report.get('validation', {}), indent=2)}\n```",
        "",
        "## Website / deployment witness",
        "",
        f"```json\n{json.dumps(report.get('witness', {}), indent=2)}\n```",
        "",
        "## Naming / control-plane drift",
        "",
    ]
    drift = report.get("naming_drift") or []
    if not drift:
        lines.append("_No naming drift patterns flagged._")
    else:
        for item in drift[:25]:
            lines.append(f"- **{item['severity']}** `{item['path']}` — {item['pattern']}: {item['note']}")
        if len(drift) > 25:
            lines.append(f"- _…and {len(drift) - 25} more_")
    lines.extend(
        [
            "",
            "## Warnings",
            "",
        ]
    )
    for w in report.get("warnings") or []:
        lines.append(f"- {w}")
    if not report.get("warnings"):
        lines.append("_none_")
    lines.append("")
    return "\n".join(lines)


def run_google_docs_refresh(
    repo_root: Path,
    *,
    trigger: str,
    dry_run: bool = False,
    skip_witness_http: bool = False,
    skip_msos_push: bool = False,
    skip_validation: bool = False,
) -> tuple[dict[str, Any], int]:
    repo = repo_root.resolve()
    git = _git_state(repo)
    prev_refresh = _read_json(repo / REPORT_JSON_REL)
    prev_msos = _read_json(repo / MSOS_REPORT_REL)

    drift = _scan_naming_drift(repo)
    staleness = _continuity_staleness(repo)
    warnings: list[str] = list(staleness)
    if prev_msos:
        warnings.extend(prev_msos.get("section15a_drift_warnings") or [])

    msos_report: dict[str, Any] | None = None
    if not skip_msos_push:
        from scripts.sync_msos_repo_truth import run_sync

        code = run_sync(repo, dry_run=dry_run)
        msos_report = _read_json(repo / MSOS_REPORT_REL)
        if code == 2:
            warnings.append("MSOS markers missing in Google Doc (operator setup required)")
        elif code != 0:
            warnings.append(f"sync_msos_repo_truth_v1 exit {code}")

    validation: dict[str, Any] = {"skipped": skip_validation}
    if not skip_validation:
        validation = _run_control_validation(repo)

    witness = _witness(repo, skip_http=skip_witness_http)
    head = git.get("head")
    prev_head = (prev_refresh or {}).get("head") or (prev_msos or {}).get("head_sha")
    delta_parts: list[str] = []
    if prev_head and head and prev_head != head:
        delta_parts.append(f"HEAD {prev_head[:7]} → {head[:7]}")
    elif prev_head == head:
        delta_parts.append("HEAD unchanged")
    if prev_refresh:
        delta_parts.append(f"last refresh {prev_refresh.get('generated_at', 'unknown')}")
    delta_summary = "; ".join(delta_parts) if delta_parts else "first refresh or no prior report"

    live_mirror = "no"
    if msos_report:
        if msos_report.get("skipped") and msos_report.get("reason") == "dry_run":
            live_mirror = "dry-run only"
        elif msos_report.get("passed") and not msos_report.get("skipped"):
            live_mirror = f"yes ({msos_report.get('generated_at')})"
        elif msos_report.get("skipped"):
            live_mirror = f"skipped ({msos_report.get('reason')})"

    next_move, confidence = _recommended_next_move(repo)
    report: dict[str, Any] = {
        "job": "google_docs_refresh_v1",
        "trigger": trigger,
        "generated_at": _iso_now(),
        "branch": git.get("branch"),
        "head": head,
        "working_tree_clean": git.get("working_tree_clean"),
        "upstream": git.get("upstream"),
        "ahead": git.get("ahead"),
        "behind": git.get("behind"),
        "freshness_verdict": _freshness_verdict(git, prev_msos, msos_report, staleness, drift),
        "delta_summary": delta_summary,
        "validation": validation,
        "witness": witness,
        "live_mirror_regenerated": live_mirror,
        "msos_sync": msos_report,
        "naming_drift": drift,
        "master_import_needed": _master_import_gap(repo),
        "recommended_next_move": next_move,
        "confidence": confidence,
        "warnings": warnings,
        "passed": True,
    }

    cp = repo / "artifacts" / "control_plane"
    cp.mkdir(parents=True, exist_ok=True)
    (cp / "google_docs_refresh_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    (cp / "google_docs_refresh_report.md").write_text(_format_report_md(report), encoding="utf-8")

    exit_code = 0
    if msos_report and msos_report.get("reason") and "markers missing" in str(msos_report.get("reason")):
        exit_code = 2
    return report, exit_code


def main(argv: list[str] | None = None) -> int:
    # Windows consoles often default to cp1252, which cannot print some unicode
    # characters used in reports (e.g., em-dash, arrows). Make printing best-effort
    # instead of crashing the whole refresh.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="GOOGLE_DOCS_REFRESH — control-plane Google Docs maintenance"
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--trigger",
        choices=("cycle-start", "cycle-end", "manual"),
        default="manual",
        help="cycle-start: before run_ppe/phase; cycle-end: after closeout; manual: operator/agent",
    )
    parser.add_argument("--dry-run", action="store_true", help="MSOS snapshot only, no Google push")
    parser.add_argument("--skip-witness-http", action="store_true")
    parser.add_argument("--skip-msos-push", action="store_true")
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args(argv)

    report, code = run_google_docs_refresh(
        args.repo_root,
        trigger=args.trigger,
        dry_run=args.dry_run,
        skip_witness_http=args.skip_witness_http,
        skip_msos_push=args.skip_msos_push,
        skip_validation=args.skip_validation,
    )
    print(_format_report_md(report))
    print(f"\ngoogle_docs_refresh: wrote {REPORT_JSON_REL}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
