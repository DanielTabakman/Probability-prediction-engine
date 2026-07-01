"""Product vapor registry — documented/implied capability not yet real (outside active relay).

Auto-populates from module registry, chapter backlog, usage signals, and static rules.
Auto-depopulates when relay queue ships, modules go LIVE, or archive gates clear.

Source: docs/SOP/PRODUCT_VAPOR_REGISTRY.json (manual pins persist; items[] regenerated on sync)
Readable: docs/SOP/PRODUCT_VAPOR_REGISTRY.md
Dashboard: msos_module_map.html panel via ppe_operator_compass.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

REGISTRY_REL = "docs/SOP/PRODUCT_VAPOR_REGISTRY.json"
REGISTRY_MD_REL = "docs/SOP/PRODUCT_VAPOR_REGISTRY.md"
MODULE_REGISTRY_REL = "docs/SOP/PPE_MODULE_REGISTRY_V1.md"
BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"
QUEUE_REL = "docs/SOP/PHASE_QUEUE.json"

OPEN_STATUSES = frozenset({"open", "parked"})
CLOSED_STATUSES = frozenset({"shipped", "wont", "in_queue", "chartered"})

# Vision / engine gaps — not auto-detectable from queue or registry tables.
STATIC_VAPOR: list[dict[str, Any]] = [
    {
        "id": "mode:expression_search",
        "title": "Expression search (interaction mode 2)",
        "vaporType": "vision",
        "priority": "low",
        "why": "Dedicated payoff-structure mode; P6 sim exists but no mode surface.",
        "canonRef": "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md",
    },
    {
        "id": "mode:hedging",
        "title": "Hedging (interaction mode 3)",
        "vaporType": "vision",
        "priority": "low",
        "why": "Exposure-first reshape; no dedicated surface.",
        "canonRef": "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md",
    },
    {
        "id": "mode:scenario_planning",
        "title": "Scenario planning (interaction mode 4)",
        "vaporType": "vision",
        "priority": "low",
        "why": "Multi-world branching UI unvalidated by trader research.",
        "canonRef": "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md",
    },
    {
        "id": "mode:timing_planner",
        "title": "Timing planner (interaction mode 5)",
        "vaporType": "vision",
        "priority": "low",
        "why": "Expiry choice exists; no entry/roll timing surface.",
        "canonRef": "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md",
    },
    {
        "id": "mode:calibration_science",
        "title": "Learning / calibration science (interaction mode 7)",
        "vaporType": "vision",
        "priority": "medium",
        "why": "Post-mortem reviews shipped; systematic mispricing analytics not.",
        "canonRef": "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md",
    },
    {
        "id": "ux:msos_native_strategy_lab",
        "title": "MSOS-native Strategy Lab (migrate off embed)",
        "vaporType": "doc",
        "priority": "medium",
        "why": "Embed shell shipped for MCD; full native chart shell is a separate architecture chapter.",
        "canonRef": "docs/SOP/UX_EXECUTION_BACKLOG_V1.md",
    },
    {
        "id": "ux:richer_relationship_modes",
        "title": "Richer relationship modes (beyond disagreement)",
        "vaporType": "doc",
        "priority": "medium",
        "why": "Disagreement is primary grammar today; additional modes need steward SELECTION.",
        "canonRef": "docs/SOP/PPE_MODULE_REGISTRY_V1.md",
    },
    {
        "id": "ux:session_continuity",
        "title": "Session continuity (market moved since…)",
        "vaporType": "ui",
        "priority": "low",
        "why": "Return visits lack stale-state honesty on saved thesis/evaluation.",
        "canonRef": "docs/SOP/UX_EXECUTION_BACKLOG_V1.md",
    },
    {
        "id": "ux:homepage_zero_login_action",
        "title": "Public homepage zero-login first action",
        "vaporType": "ui",
        "priority": "low",
        "why": "Storyboard P2 partial — visitors may not do something meaningful before sign-in.",
        "canonRef": "docs/SOP/MSOS_WEBSITE_PROGRAM.md",
    },
    {
        "id": "engine:materiality_floors",
        "title": "Named materiality floors (M_floor, M_ratio)",
        "vaporType": "engine",
        "priority": "medium",
        "why": "PPE Master §6 gap — candidate UX can outrun math contract.",
        "canonRef": "docs/VISION/PPE_MASTER_MVP1.md",
    },
    {
        "id": "research:strategy_layer",
        "title": "Research pipeline strategy layer",
        "vaporType": "doc",
        "priority": "low",
        "why": "Collectors + tests exist; trade rules consume strategy_ready later.",
        "canonRef": "docs/SOP/RESEARCH_PIPELINE_V1.md",
    },
    {
        "id": "lens:prediction_markets",
        "title": "Prediction markets MSOS lens",
        "vaporType": "ui",
        "priority": "medium",
        "why": "Collector + scan exist ops-side; storyboard lens still Coming Soon.",
        "canonRef": "docs/VISION/MSOS/storyboard-v0.6/MANIFEST.md",
    },
    {
        "id": "panel:msos_class_summary",
        "title": "MSOS class-summary panel",
        "vaporType": "ui",
        "priority": "medium",
        "why": "Streamlit reviewed-class rollup exists; MSOS aggregate learning view does not.",
        "canonRef": "docs/SOP/TRADER_LEARNING_SPINE_PROGRAM_V1.md",
    },
    {
        "id": "commercial:stripe_self_serve",
        "title": "Stripe self-serve billing",
        "vaporType": "doc",
        "priority": "low",
        "why": "Chapter deferred until operator Stripe prerequisites complete.",
        "canonRef": "docs/SOP/HUMAN_STEWARD_BACKLOG.json",
        "depopulateWhen": "human_backlog:stripe_operator_prereq:done",
    },
]


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def registry_path(repo: Path) -> Path:
    return repo.resolve() / REGISTRY_REL


def load_registry(repo: Path) -> dict[str, Any]:
    p = registry_path(repo)
    if not p.is_file():
        return {"version": 1, "notes": "", "manual": [], "items": [], "last_sync_utc": None}
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save_registry(repo: Path, data: dict[str, Any]) -> Path:
    p = registry_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return p


def _chapter_id_from_plan(plan_path: str) -> str:
    name = Path(plan_path.replace("\\", "/")).stem
    if name.endswith("_relay"):
        return name[: -len("_relay")]
    return name


def _queue_chapter_states(repo: Path) -> dict[str, str]:
    path = repo / QUEUE_REL
    if not path.is_file():
        return {}
    try:
        queue = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}
    out: dict[str, str] = {}
    for item in queue.get("items") or []:
        if not isinstance(item, dict):
            continue
        plan = str(item.get("planPath") or "").strip()
        if not plan:
            continue
        cid = _chapter_id_from_plan(plan)
        st = str(item.get("status") or "").strip().upper()
        out[cid] = st
    return out


def _backlog_chapters(repo: Path) -> list[dict[str, Any]]:
    path = repo / BACKLOG_REL
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return []
    return [i for i in (data.get("items") or []) if isinstance(i, dict)]


def _parse_module_registry_modules(repo: Path) -> list[dict[str, str]]:
    path = repo / MODULE_REGISTRY_REL
    if not path.is_file():
        return []
    modules: list[dict[str, str]] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| # | Module ID"):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        if line.startswith("|---"):
            continue
        if line.strip().startswith("| *"):
            break
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 13:
            continue
        num = parts[1]
        if not num.isdigit():
            continue
        modules.append(
            {
                "module_id": parts[2].strip("`"),
                "display_name": parts[3],
                "tier": parts[9],
                "status": parts[11].replace("**", "").strip(),
                "advance": parts[12],
            }
        )
    return modules


def _parse_planned_module_classes(repo: Path) -> list[dict[str, str]]:
    path = repo / MODULE_REGISTRY_REL
    if not path.is_file():
        return []
    out: list[dict[str, str]] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if "| Class ID | Primary question |" in line:
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        if line.startswith("|---"):
            continue
        if "*reserved*" in line:
            break
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        class_id = parts[1].strip("`")
        if not class_id or class_id == "Class ID":
            continue
        examples = parts[3]
        if "planned" not in examples.lower() and "*(planned)*" not in examples:
            continue
        out.append({"class_id": class_id, "label": examples})
    return out


def _human_backlog_done_ids(repo: Path) -> set[str]:
    from scripts.ppe_human_backlog import load_backlog

    done: set[str] = set()
    for item in load_backlog(repo).get("items") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").strip().lower() in ("done", "cancelled"):
            done.add(str(item.get("id") or ""))
    return done


def _usage_vapor(repo: Path) -> list[dict[str, Any]]:
    try:
        from scripts.ppe_tracking_hub import collect_tracking_snapshot

        snap = collect_tracking_snapshot(repo, days=7)
    except Exception:
        snap = {}
    factory = snap.get("factory") or {}
    trader = snap.get("trader") or {}
    sessions = int(factory.get("validation_sessions") or 0)
    frozen = int(trader.get("frozen_total") or 0)
    reviewed = int(trader.get("completed_reviews") or 0)
    out: list[dict[str, Any]] = []
    if sessions < 1:
        out.append(
            {
                "id": "usage:validation_sessions",
                "title": "Trader validation sessions (milestone gate)",
                "vaporType": "usage",
                "priority": "high",
                "why": "Milestone needs ≥3 traders using MSOS in process; validation_sessions=0.",
                "canonRef": "docs/SOP/MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md",
                "source": "tracking_hub",
            }
        )
    if frozen < 1 and reviewed < 1:
        out.append(
            {
                "id": "usage:evidence_clock",
                "title": "Evidence clock (freeze → review loop)",
                "vaporType": "usage",
                "priority": "high",
                "why": "Product shipped but no production freezes/reviews on evidence clock yet.",
                "canonRef": "docs/VISION/PPE_MASTER_MVP1.md",
                "source": "tracking_hub",
            }
        )
    return out


def discover_vapor(repo: Path) -> list[dict[str, Any]]:
    """Auto-detect vapor candidates (not yet filtered for depopulate)."""
    repo = repo.resolve()
    discovered: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(item: dict[str, Any]) -> None:
        iid = str(item.get("id") or "")
        if not iid or iid in seen:
            return
        seen.add(iid)
        row = dict(item)
        row.setdefault("auto", True)
        row.setdefault("status", "open")
        row.setdefault("source", row.get("source") or "discover")
        discovered.append(row)

    for row in STATIC_VAPOR:
        add(dict(row))

    for mod in _parse_module_registry_modules(repo):
        mid = mod["module_id"]
        status = mod["status"].upper()
        if "PARTIAL" in status or "PLANNED" in status:
            add(
                {
                    "id": f"module:{mid}",
                    "title": f"{mod['display_name']} — partial module",
                    "vaporType": "engine",
                    "priority": "medium",
                    "why": f"Registry status: {mod['status']}. Next: {mod.get('advance') or '—'}",
                    "canonRef": "docs/SOP/PPE_MODULE_REGISTRY_V1.md",
                    "source": "module_registry",
                }
            )
        elif "LIVE" in status and mod.get("advance"):
            adv = str(mod["advance"])
            if adv and not adv.lower().startswith("—") and "T4" in adv:
                add(
                    {
                        "id": f"module:{mid}:advance",
                        "title": f"{mod['display_name']} — tier advance",
                        "vaporType": "doc",
                        "priority": "low",
                        "why": adv,
                        "canonRef": "docs/SOP/PPE_MODULE_REGISTRY_V1.md",
                        "source": "module_registry",
                    }
                )

    for cls in _parse_planned_module_classes(repo):
        cid = cls["class_id"]
        add(
            {
                "id": f"class:{cid.lower()}",
                "title": f"Module class — {cid}",
                "vaporType": "vision",
                "priority": "low",
                "why": f"Registry class planned: {cls['label']}",
                "canonRef": "docs/SOP/PPE_MODULE_REGISTRY_V1.md",
                "source": "module_registry",
            }
        )

    queue_states = _queue_chapter_states(repo)
    for chapter in _backlog_chapters(repo):
        cid = str(chapter.get("chapterId") or "").strip()
        if not cid:
            continue
        st = str(chapter.get("status") or "").strip().lower()
        qst = queue_states.get(cid, "")
        if st in ("done", "skipped"):
            continue
        if st not in ("deferred", "blocked", "chartered", "queued"):
            continue
        if st == "queued" and qst == "PLANNED":
            continue
        priority = str(chapter.get("priority") or "medium")
        add(
            {
                "id": f"chapter:{cid}",
                "title": cid.replace("_", " "),
                "vaporType": "doc",
                "priority": priority,
                "why": str(chapter.get("reason") or f"Backlog status: {st}"),
                "canonRef": str(chapter.get("canonRef") or chapter.get("selectionRecord") or BACKLOG_REL),
                "source": "chapter_backlog",
                "chapterId": cid,
            }
        )

    for item in _usage_vapor(repo):
        add(item)

    return discovered


def _should_depopulate(
    item: dict[str, Any],
    *,
    queue_states: dict[str, str],
    human_done: set[str],
) -> str | None:
    """Return closed status if item should leave open vapor list."""
    iid = str(item.get("id") or "")
    st = str(item.get("status") or "open").strip().lower()
    if st in ("wont", "shipped"):
        return st
    if st == "parked":
        return None

    dep = str(item.get("depopulateWhen") or "")
    if dep.startswith("human_backlog:"):
        parts = dep.split(":")
        if len(parts) >= 3 and parts[1] in human_done:
            return "shipped"

    chapter_id = str(item.get("chapterId") or "")
    if not chapter_id and iid.startswith("chapter:"):
        chapter_id = iid.split(":", 1)[1]
    if chapter_id:
        qst = queue_states.get(chapter_id, "")
        if qst == "DONE":
            return "shipped"
        if qst in ("READY", "PLANNED"):
            return "in_queue"

    return None


def _module_is_live(repo: Path, module_id: str) -> bool:
    for mod in _parse_module_registry_modules(repo):
        if mod["module_id"] != module_id:
            continue
        status = mod["status"].upper()
        return "LIVE" in status and "PARTIAL" not in status
    return False


def should_depopulate_item(repo: Path, item: dict[str, Any], queue_states: dict[str, str], human_done: set[str]) -> str | None:
    reason = _should_depopulate(item, queue_states=queue_states, human_done=human_done)
    if reason:
        return reason

    iid = str(item.get("id") or "")
    if iid.startswith("module:") and ":advance" not in iid:
        mid = iid.split(":", 1)[1]
        if _module_is_live(repo, mid):
            return "shipped"

    if iid == "usage:validation_sessions":
        try:
            from scripts.ppe_tracking_hub import collect_tracking_snapshot

            factory = (collect_tracking_snapshot(repo).get("factory") or {})
            if int(factory.get("validation_sessions") or 0) >= 1:
                return "shipped"
        except Exception:
            pass

    if iid == "usage:evidence_clock":
        try:
            from scripts.ppe_tracking_hub import collect_tracking_snapshot

            trader = (collect_tracking_snapshot(repo).get("trader") or {})
            frozen = int(trader.get("frozen_total") or 0)
            reviewed = int(trader.get("completed_reviews") or 0)
            if frozen >= 1 or reviewed >= 1:
                return "shipped"
        except Exception:
            pass

    return None


def merge_vapor_items(repo: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (open_items, closed_items) after discover + manual merge + depopulate."""
    repo = repo.resolve()
    data = load_registry(repo)
    manual = [dict(i) for i in (data.get("manual") or []) if isinstance(i, dict)]
    discovered = discover_vapor(repo)
    queue_states = _queue_chapter_states(repo)
    human_done = _human_backlog_done_ids(repo)

    by_id: dict[str, dict[str, Any]] = {}
    for item in discovered:
        by_id[str(item["id"])] = item
    for item in manual:
        iid = str(item.get("id") or "")
        if not iid:
            continue
        base = by_id.get(iid, {})
        merged = {**base, **item}
        merged["id"] = iid
        if item.get("pin"):
            merged["auto"] = False
        by_id[iid] = merged

    open_items: list[dict[str, Any]] = []
    closed_items: list[dict[str, Any]] = []
    rank = {"high": 0, "medium": 1, "low": 2}
    type_rank = {"usage": 0, "ui": 1, "engine": 2, "vision": 3, "doc": 4}

    for iid, item in by_id.items():
        closed = should_depopulate_item(repo, item, queue_states, human_done)
        row = dict(item)
        row["id"] = iid
        if closed:
            row["status"] = closed
            closed_items.append(row)
            continue
        st = str(row.get("status") or "open").strip().lower()
        if st in CLOSED_STATUSES:
            closed_items.append(row)
            continue
        if st not in OPEN_STATUSES:
            row["status"] = "open"
        open_items.append(row)

    open_items.sort(
        key=lambda i: (
            rank.get(str(i.get("priority") or "medium").lower(), 9),
            type_rank.get(str(i.get("vaporType") or "doc").lower(), 9),
            str(i.get("id") or ""),
        )
    )
    closed_items.sort(key=lambda i: str(i.get("id") or ""))
    return open_items, closed_items


def open_vapor_items(repo: Path) -> list[dict[str, Any]]:
    open_items, _ = merge_vapor_items(repo)
    return open_items


def sync_registry(repo: Path, *, render_md: bool = True, patch_compass: bool = True) -> dict[str, Any]:
    repo = repo.resolve()
    data = load_registry(repo)
    open_items, closed_items = merge_vapor_items(repo)
    data["last_sync_utc"] = _utc_now()
    data["open_count"] = len(open_items)
    data["closed_count"] = len(closed_items)
    data["items"] = open_items
    data["closed_items"] = closed_items
    save_registry(repo, data)
    if render_md:
        md_path = repo / REGISTRY_MD_REL
        md_path.write_text(render_markdown(repo, data), encoding="utf-8")
    if patch_compass:
        try:
            from scripts.ppe_operator_compass import sync_compass

            sync_compass(repo, patch_map=True)
        except Exception:
            pass
    return data


def render_markdown(repo: Path, data: dict[str, Any] | None = None) -> str:
    if data is None:
        data = load_registry(repo)
    notes = str(data.get("notes") or "").strip()
    lines = [
        "# Product vapor registry",
        "",
        "**Purpose:** Capability that reads as real in docs/UI but is **not built or not in active relay**. "
        "Auto-synced — not a BUILD queue. Promote via steward SELECTION → `PHASE_QUEUE.json`.",
        "",
        "| When | Action |",
        "|------|--------|",
        "| **On operator status refresh** | Auto-populate + depopulate (`ppe_vapor_registry.py --sync`) |",
        "| **Monthly** | Triage open rows — `parked`, `wont`, or charter |",
        "| **Pin steward notes** | Edit `manual[]` in JSON (`pin: true`) |",
        "",
        f"**Machine source:** [`PRODUCT_VAPOR_REGISTRY.json`](PRODUCT_VAPOR_REGISTRY.json) · "
        f"**Last sync:** {data.get('last_sync_utc') or '—'} · "
        f"**Open:** {data.get('open_count', len(data.get('items') or []))}",
        "",
        "**Dashboard:** [`assets/msos_module_map.html`](assets/msos_module_map.html) — *Product vapor* panel",
        "",
    ]
    if notes:
        lines.extend([f"> {notes}", ""])

    items = [i for i in (data.get("items") or []) if isinstance(i, dict)]
    if items:
        lines.append("## Open (not in active relay)")
        lines.append("")
        lines.append("| Priority | Type | Item | Why |")
        lines.append("|----------|------|------|-----|")
        for item in items:
            pri = str(item.get("priority") or "medium")
            vtype = str(item.get("vaporType") or "doc")
            title = str(item.get("title") or item.get("id") or "?")
            why = str(item.get("why") or "").replace("|", "/")
            auto = "auto" if item.get("auto") else "manual"
            lines.append(f"| {pri} | {vtype} | {title} `{auto}` | {why} |")
        lines.append("")

    closed = [i for i in (data.get("closed_items") or []) if isinstance(i, dict)]
    if closed:
        lines.append("## Recently depopulated (auto)")
        lines.append("")
        for item in closed[:20]:
            lines.append(
                f"- `{item.get('id')}` → **{item.get('status')}** — {item.get('title') or ''}"
            )
        if len(closed) > 20:
            lines.append(f"- _+{len(closed) - 20} more_")
        lines.append("")

    lines.append("## Changelog")
    lines.append("")
    lines.append(f"| {datetime.now(UTC).date().isoformat()} | Auto-sync from discover + manual pins |")
    lines.append("")
    return "\n".join(lines)


def compass_panel_items(repo: Path, *, max_items: int = 12) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in open_vapor_items(repo)[:max_items]:
        out.append(
            {
                "id": str(item.get("id") or ""),
                "title": str(item.get("title") or ""),
                "why": str(item.get("why") or ""),
                "source": f"vapor:{item.get('vaporType') or 'doc'}",
            }
        )
    return out


def cmd_status(repo: Path) -> int:
    open_items, closed = merge_vapor_items(repo)
    print(f"Product vapor registry: {len(open_items)} open, {len(closed)} depopulated this sync")
    for item in open_items:
        pri = str(item.get("priority") or "medium").upper()
        vtype = str(item.get("vaporType") or "doc")
        auto = "auto" if item.get("auto") else "pin"
        print(f"  [{pri}/{vtype}/{auto}] {item.get('title') or item.get('id')}")
    print(f"\nFull list: {REGISTRY_MD_REL}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Product vapor registry (auto-populate / depopulate)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--sync", action="store_true", help="Discover, merge, depopulate, write JSON + MD + compass")
    ap.add_argument("--status", action="store_true", help="Print open vapor items")
    ap.add_argument("--render-md", action="store_true", help="Render markdown only")
    ap.add_argument("--no-compass", action="store_true", help="Skip compass/map patch on sync")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.sync:
        data = sync_registry(repo, render_md=True, patch_compass=not args.no_compass)
        print(
            f"ppe_vapor_registry: synced {data.get('open_count', 0)} open, "
            f"{data.get('closed_count', 0)} depopulated -> {REGISTRY_REL}"
        )
        return 0
    if args.render_md:
        data = load_registry(repo)
        open_items, closed = merge_vapor_items(repo)
        data["items"] = open_items
        data["closed_items"] = closed
        (repo / REGISTRY_MD_REL).write_text(render_markdown(repo, data), encoding="utf-8")
        print(f"ppe_vapor_registry: wrote {REGISTRY_MD_REL}")
        return 0
    if args.status:
        return cmd_status(repo)
    return cmd_status(repo)


if __name__ == "__main__":
    raise SystemExit(main())
