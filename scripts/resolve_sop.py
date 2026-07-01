#!/usr/bin/env python3
"""Resolve which SOP docs to load for a chapter, module, or topic."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.sop_discovery_core import (  # noqa: E402
    ROLE_ROUTES,
    list_topics,
    resolve_by_chapter,
    resolve_by_module,
    resolve_by_role,
    resolve_by_search,
    resolve_by_topic,
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Resolve SOP docs to load for agents/humans")
    ap.add_argument("--repo-root", type=Path, default=_REPO)
    ap.add_argument("--chapter", help="Relay chapter id (e.g. ppe_exposure_menu_v1)")
    ap.add_argument("--plan-path", help="Phase plan path (alternative to --chapter)")
    ap.add_argument("--module", help="Module id from PPE_MODULE_REGISTRY_V1.md")
    ap.add_argument("--topic", help="Free-text topic or operator phrase")
    ap.add_argument("--search", help="Search active chapters + program docs")
    ap.add_argument(
        "--role",
        choices=sorted(ROLE_ROUTES),
        help="Thread role load bundle (operator, charter, ide_build, explore, neutral)",
    )
    ap.add_argument("--list-topics", action="store_true", help="List topic route catalog")
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    return ap.parse_args(argv)


def _print_human(report: dict) -> None:
    ok = report.get("ok")
    label = "OK" if ok else "UNRESOLVED"
    print(f"resolve_sop: {label}")
    if report.get("chapter_id"):
        print(f"  chapter: {report['chapter_id']}")
    if report.get("module_id"):
        print(f"  module: {report['module_id']}")
    if report.get("topic"):
        print(f"  topic: {report['topic']}")
    if report.get("topic_route_id"):
        print(f"  route: {report['topic_route_id']}")
    if report.get("role"):
        print(f"  role: {report['role']}")
    if report.get("query"):
        print(f"  query: {report['query']}")
    if report.get("search_match_count") is not None:
        print(f"  matches: {report['search_match_count']}")
    if report.get("sop"):
        print(f"  sop: {report['sop']}")
    if report.get("next_action"):
        print(f"  next_action: {report['next_action']}")
    for key in ("load_always", "load_for_build", "load_on_demand"):
        paths = report.get(key) or []
        if paths:
            print(f"  {key}:")
            for p in paths:
                print(f"    - {p}")
    never = report.get("never_load") or report.get("do_not_load") or []
    if never:
        print("  never_load:")
        for p in never:
            print(f"    - {p}")
    results = report.get("results") or []
    if results:
        print("  results:")
        for row in results[:8]:
            label = row.get("chapter_id") or row.get("module_id") or row.get("topic_route_id")
            print(f"    - {label}: {row.get('resolve_cmd')}")
    steps = report.get("agent_steps") or []
    if steps:
        print("  agent_steps:")
        for step in steps:
            print(f"    - {step}")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    repo = args.repo_root.resolve()

    if args.list_topics:
        topics = list_topics()
        if args.json:
            print(json.dumps(topics, indent=2, sort_keys=True))
        else:
            print("resolve_sop: topic routes")
            for row in topics:
                print(f"  {row['id']}: {row['sop']}")
        return 0

    modes = sum(
        1
        for x in (args.chapter, args.plan_path, args.module, args.topic, args.role, args.search)
        if x
    )
    if modes != 1:
        print(
            "resolve_sop: pass exactly one of --chapter, --plan-path, --module, "
            "--topic, --role, --search",
            file=sys.stderr,
        )
        return 2

    if args.role:
        report = resolve_by_role(args.role)
    elif args.search:
        report = resolve_by_search(repo, args.search)
    elif args.chapter or args.plan_path:
        report = resolve_by_chapter(
            repo,
            chapter_id=args.chapter,
            plan_path=args.plan_path,
        )
    elif args.module:
        report = resolve_by_module(repo, args.module)
    else:
        report = resolve_by_topic(args.topic or "")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_human(report)

    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
