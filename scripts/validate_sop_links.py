#!/usr/bin/env python3
"""Validate SOP discovery links — active chapters, program docs, topic routes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.sop_discovery_core import (  # noqa: E402
    CHAPTER_DOC_INDEX_REL,
    MODULE_PROGRAM_DOCS,
    TOPIC_ROUTES,
    build_chapter_doc_index,
    validate_archived_selection_refs,
    validate_program_doc_footers,
)


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def _missing(repo: Path, rel: str) -> bool:
    p = rel.strip()
    if not p:
        return True
    if p.startswith("artifacts/"):
        return False
    if p.startswith(".cursor/"):
        return not (repo / p).is_file()
    return not (repo / p).is_file()


def validate_active_chapters(repo: Path, index: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    active = index.get("active_chapters") or [
        row for row in (index.get("chapters") or []) if not row.get("archived")
    ]
    for row in active:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("chapter_id") or "?")
        for key in ("program_doc", "selection", "sprint", "evidence", "next_selection"):
            val = row.get(key)
            if isinstance(val, str) and val.strip() and _missing(repo, _norm(val)):
                errors.append(f"active chapter {cid}: missing {val}")
        for path in row.get("load_always") or []:
            if _missing(repo, _norm(str(path))):
                errors.append(f"active chapter {cid}: missing load_always {path}")
        for path in row.get("load_for_build") or []:
            if _missing(repo, _norm(str(path))):
                errors.append(f"active chapter {cid}: missing load_for_build {path}")
        for path in row.get("load_on_demand") or []:
            if _missing(repo, _norm(str(path))):
                errors.append(f"active chapter {cid}: missing load_on_demand {path}")
    return errors


def validate_program_docs(
    repo: Path,
    *,
    module_program_docs: dict[str, str] | None = None,
) -> list[str]:
    errors: list[str] = []
    docs = module_program_docs if module_program_docs is not None else MODULE_PROGRAM_DOCS
    for module_id, rel in docs.items():
        if _missing(repo, _norm(rel)):
            errors.append(f"module {module_id}: missing program doc {rel}")
    return errors


def validate_topic_routes(
    repo: Path,
    *,
    topic_routes: list[dict[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    routes = topic_routes if topic_routes is not None else TOPIC_ROUTES
    for route in routes:
        rid = str(route.get("id") or "?")
        sop = _norm(str(route.get("sop") or ""))
        if sop and _missing(repo, sop):
            errors.append(f"topic route {rid}: missing sop {sop}")
        for path in route.get("load_always") or []:
            rel = _norm(str(path))
            if rel.startswith("artifacts/"):
                continue
            if _missing(repo, rel):
                errors.append(f"topic route {rid}: missing load_always {rel}")
        for path in route.get("load_on_demand") or []:
            rel = _norm(str(path))
            if rel.startswith("artifacts/"):
                continue
            if rel.startswith("config/"):
                if not (repo / rel).is_file():
                    errors.append(f"topic route {rid}: missing load_on_demand {rel}")
                continue
            if _missing(repo, rel):
                errors.append(f"topic route {rid}: missing load_on_demand {rel}")
        rule = route.get("cursor_rule")
        if rule and _missing(repo, _norm(str(rule))):
            errors.append(f"topic route {rid}: missing cursor_rule {rule}")
    return errors


def validate_sop_links(
    repo: Path,
    *,
    index: dict[str, Any] | None = None,
    module_program_docs: dict[str, str] | None = None,
    topic_routes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    if index is None:
        index_path = repo / CHAPTER_DOC_INDEX_REL
        if index_path.is_file():
            try:
                index = json.loads(index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                index = build_chapter_doc_index(repo)
        else:
            index = build_chapter_doc_index(repo)

    errors: list[str] = []
    errors.extend(validate_active_chapters(repo, index))
    errors.extend(validate_program_docs(repo, module_program_docs=module_program_docs))
    errors.extend(validate_topic_routes(repo, topic_routes=topic_routes))
    errors.extend(validate_program_doc_footers(repo))
    errors.extend(validate_archived_selection_refs(repo, index=index))

    return {
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
        "active_chapter_count": index.get("active_chapter_count"),
        "archived_chapter_count": index.get("archived_chapter_count"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate SOP discovery doc links")
    ap.add_argument("--repo-root", type=Path, default=_REPO)
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    args = ap.parse_args(argv)

    report = validate_sop_links(args.repo_root.resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        if report["ok"]:
            print(
                "validate_sop_links: OK "
                f"({report.get('active_chapter_count')} active, "
                f"{report.get('archived_chapter_count')} archived)"
            )
        else:
            print(f"validate_sop_links: FAIL ({report['error_count']} errors)")
            for err in report["errors"][:20]:
                print(f"  - {err}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
