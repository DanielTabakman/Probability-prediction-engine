"""Product vapor registry — documented/implied capability not yet real (outside active relay).

Auto-populates from module registry, vision docs, UI fixtures, and usage signals.
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
PHASE_QUEUE_REL = "docs/SOP/PHASE_QUEUE.json"
INTERACTION_MODES_REL = "docs/VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md"

ACTIVE_QUEUE_STATUSES = frozenset({"READY", "IN_PROGRESS", "BUILD_IN_FLIGHT", "RUNNING"})
DONE_QUEUE_STATUSES = frozenset({"DONE", "COMPLETE"})

# MSOS routes that ship demo/fixture payloads when live fetch fails.
UI_FIXTURE_RULES: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "ui_fixture_forward_consistency",
        "Forward consistency — demo payload fallback",
        "Route may serve DEMO_FORWARD_CONSISTENCY when live API unavailable",
        "ui_fixture",
        "apps/msos-web/src/lib/forwardConsistency.ts",
    ),
    (
        "ui_fixture_strategy_lab_demo",
        "Strategy Lab — sample mode banner",
        "StrategyLabClientShell falls back to demo/sample pill when live PPE fetch fails",
        "ui_fixture",
        "apps/msos-web/src/components/StrategyLabClientShell.tsx",
    ),
)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def registry_path(repo: Path) -> Path:
    return repo.resolve() / REGISTRY_REL


def load_registry(repo: Path) -> dict[str, Any]:
    p = registry_path(repo)
    if not p.is_file():
        return {
            "version": 1,
            "notes": "",
            "manual": [],
            "last_sync_utc": None,
            "open_count": 0,
            "closed_count": 0,
            "items": [],
            "closed_items": [],
        }
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _load_phase_queue(repo: Path) -> list[dict[str, Any]]:
    path = repo / PHASE_QUEUE_REL
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return [i for i in (data.get("items") or []) if isinstance(i, dict)]


def _active_plan_paths(queue: list[dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for item in queue:
        st = str(item.get("status") or "").strip().upper()
        if st in ACTIVE_QUEUE_STATUSES:
            rel = str(item.get("planPath") or "").replace("\\", "/")
            if rel:
                out.add(rel)
    return out


def _done_plan_paths(queue: list[dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for item in queue:
        st = str(item.get("status") or "").strip().upper()
        if st in DONE_QUEUE_STATUSES:
            rel = str(item.get("planPath") or "").replace("\\", "/")
            if rel:
                out.add(rel)
    return out


def _parse_module_registry(repo: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return (planned_classes, registered_modules)."""
    path = repo / MODULE_REGISTRY_REL
    if not path.is_file():
        return [], []
    text = path.read_text(encoding="utf-8")
    planned_classes: list[dict[str, str]] = []
    modules: list[dict[str, str]] = []

    in_class_table = False
    for line in text.splitlines():
        if line.startswith("| Class ID |"):
            in_class_table = True
            continue
        if in_class_table:
            if not line.startswith("|"):
                in_class_table = False
                continue
            if line.startswith("|---"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 5:
                continue
            class_id = parts[1].strip("`")
            modules_col = parts[3] if len(parts) > 3 else ""
            if "planned" in modules_col.lower():
                planned_classes.append(
                    {
                        "class_id": class_id,
                        "question": parts[2],
                        "modules": modules_col,
                    }
                )

    in_module_table = False
    for line in text.splitlines():
        if line.startswith("| # | Module ID"):
            in_module_table = True
            continue
        if not in_module_table or not line.startswith("|"):
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
        module_id = parts[2].strip("`")
        modules.append(
            {
                "num": num,
                "module_id": module_id,
                "display_name": parts[3],
                "route": parts[7],
                "status": parts[11].replace("**", "").strip(),
                "advance": parts[12],
            }
        )
    return planned_classes, modules


def _discover_interaction_modes(repo: Path) -> list[dict[str, str]]:
    path = repo / INTERACTION_MODES_REL
    if not path.is_file():
        return []
    out: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*\*\*([^*|]+)\*\*\s*\|", line)
        if not m:
            continue
        num = int(m.group(1))
        if num < 2:
            continue
        if "**Planned**" not in line and "Planned" not in line:
            continue
        mode = m.group(2).strip()
        out.append({"mode_num": str(num), "mode_name": mode})
    return out


def _discover_usage_vapor(repo: Path) -> list[dict[str, str]]:
    try:
        from scripts.ppe_tracking_hub import collect_trader_outcomes
    except ImportError:
        return []
    outcomes = collect_trader_outcomes(repo)
    if not outcomes.get("available"):
        return []
    frozen = int(outcomes.get("frozen_total") or 0)
    completed = int(outcomes.get("completed_reviews") or 0)
    out: list[dict[str, str]] = []
    if frozen == 0:
        out.append(
            {
                "signal": "zero_frozen",
                "detail": "No frozen evaluations saved — save→review loop not exercised in production yet",
            }
        )
    elif completed == 0:
        out.append(
            {
                "signal": "zero_reviews",
                "detail": f"{frozen} frozen evaluation(s) but 0 completed reviews — review loop unused",
            }
        )
    return out


def _module_queue_hints(module_id: str) -> list[str]:
    """Plan path substrings that indicate active relay work for a module."""
    hints: dict[str, list[str]] = {
        "forward_consistency": ["forward_consistency"],
        "options_horizon": ["options_horizon", "horizon_"],
        "implied_distribution": ["disagreement", "strategy_lab", "distribution"],
        "expression_planner": ["expression"],
        "cross_venue_event_gap": ["cross_venue"],
        "exposure_menu": ["exposure_menu", "exposure_path"],
    }
    return hints.get(module_id, [module_id.replace("_", "")])


def _queue_covers_module(module_id: str, active_plans: set[str]) -> bool:
    hints = _module_queue_hints(module_id)
    for plan in active_plans:
        low = plan.lower()
        if any(h in low for h in hints):
            return True
    return False


def discover_items(repo: Path) -> list[dict[str, Any]]:
    repo = repo.resolve()
    queue = _load_phase_queue(repo)
    active_plans = _active_plan_paths(queue)
    planned_classes, modules = _parse_module_registry(repo)
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(item: dict[str, Any]) -> None:
        iid = str(item.get("id") or "")
        if not iid or iid in seen:
            return
        seen.add(iid)
        items.append(item)

    for row in planned_classes:
        cid = row["class_id"].lower()
        add(
            {
                "id": f"module_class_{cid}",
                "title": f"Module class — {row['class_id']}",
                "why": f"{row['question']} · registry: {row['modules']}",
                "source": "module_registry",
                "kind": "module_class",
            }
        )

    for mod in modules:
        status = mod["status"].upper()
        mid = mod["module_id"]
        if "LIVE" in status and "PARTIAL" not in status:
            continue
        if _queue_covers_module(mid, active_plans):
            continue
        kind = "module_partial" if "PARTIAL" in status else "module_unshipped"
        add(
            {
                "id": f"module_{mid}",
                "title": f"{mod['display_name']} ({mid})",
                "why": f"Registry status: {mod['status']} · route: {mod['route']} · {mod['advance']}",
                "source": "module_registry",
                "kind": kind,
                "module_id": mid,
            }
        )

    for mode in _discover_interaction_modes(repo):
        add(
            {
                "id": f"vision_mode_{mode['mode_num']}_{mode['mode_name'].lower().replace(' ', '_')[:24]}",
                "title": f"Interaction mode {mode['mode_num']} — {mode['mode_name']}",
                "why": "Vision/ontology only — not current BUILD scope until trader workflow research + SELECTION",
                "source": "interaction_modes_vision",
                "kind": "vision",
            }
        )

    for rule_id, title, why, source, rel_path in UI_FIXTURE_RULES:
        if not (repo / rel_path).is_file():
            continue
        add(
            {
                "id": rule_id,
                "title": title,
                "why": why,
                "source": source,
                "kind": "ui_fixture",
            }
        )

    for sig in _discover_usage_vapor(repo):
        add(
            {
                "id": f"usage_{sig['signal']}",
                "title": "Trader learning spine — usage gap",
                "why": sig["detail"],
                "source": "trader_outcomes",
                "kind": "usage",
            }
        )

    items.sort(key=lambda i: (str(i.get("kind") or ""), str(i.get("title") or "")))
    return items


def _manual_open(manual: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in manual:
        if not isinstance(row, dict):
            continue
        st = str(row.get("status") or "open").strip().lower()
        if st in ("closed", "done", "shipped"):
            continue
        out.append(row)
    return out


def open_items(repo: Path) -> list[dict[str, Any]]:
    reg = load_registry(repo)
    auto = [i for i in (reg.get("items") or []) if isinstance(i, dict)]
    manual = _manual_open(reg.get("manual") or [])
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in manual + auto:
        iid = str(item.get("id") or "")
        if not iid or iid in seen:
            continue
        seen.add(iid)
        merged.append(item)
    return merged


def sync_registry(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    reg = load_registry(repo)
    prior_closed = [i for i in (reg.get("closed_items") or []) if isinstance(i, dict)]
    prior_open_ids = {str(i.get("id") or "") for i in (reg.get("items") or []) if isinstance(i, dict)}
    manual = reg.get("manual") if isinstance(reg.get("manual"), list) else []

    discovered = discover_items(repo)
    discovered_ids = {str(i.get("id") or "") for i in discovered}

    newly_closed: list[dict[str, Any]] = []
    for old in reg.get("items") or []:
        if not isinstance(old, dict):
            continue
        oid = str(old.get("id") or "")
        if oid and oid not in discovered_ids and oid not in {str(m.get("id") or "") for m in manual}:
            closed = dict(old)
            closed["closed_utc"] = _utc_now()
            closed["close_reason"] = "auto_depopulate"
            newly_closed.append(closed)

    closed_items = prior_closed + newly_closed
    # Cap closed history for readability.
    closed_items = closed_items[-80:]

    out = {
        "version": reg.get("version") or 1,
        "notes": str(
            reg.get("notes")
            or "Manual pins persist across sync. items[] regenerated by ppe_vapor_registry.py --sync. "
            "Never auto-BUILD from this file — steward SELECTION only."
        ),
        "manual": manual,
        "last_sync_utc": _utc_now(),
        "open_count": len(discovered) + len(_manual_open(manual)),
        "closed_count": len(closed_items),
        "items": discovered,
        "closed_items": closed_items,
    }

    path = registry_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    render_markdown(repo, data=out)

    if prior_open_ids != discovered_ids:
        print(f"ppe_vapor_registry: open items changed ({len(prior_open_ids)} -> {len(discovered_ids)})")
    print(f"ppe_vapor_registry: synced {out['open_count']} open item(s) -> {REGISTRY_REL}")
    return out


def render_markdown(repo: Path, *, data: dict[str, Any] | None = None) -> str:
    reg = data if data is not None else load_registry(repo)
    lines = [
        "# Product vapor registry",
        "",
        "**Purpose:** Documented or implied capability **not yet real** and **not in active relay**. "
        "Inventory only — steward SELECTION owns BUILD. "
        "See [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md) for chartered modules.",
        "",
        f"**Last sync:** `{reg.get('last_sync_utc') or 'never'}` · "
        f"**Open:** {reg.get('open_count', 0)} · **Closed (history):** {reg.get('closed_count', 0)}",
        "",
        "**Refresh:** `python scripts/ppe_vapor_registry.py --sync` · "
        "**Dashboard:** [`assets/msos_module_map.html`](assets/msos_module_map.html) (Product vapor panel)",
        "",
        "**Machine source:** [`PRODUCT_VAPOR_REGISTRY.json`](PRODUCT_VAPOR_REGISTRY.json)",
        "",
    ]
    notes = str(reg.get("notes") or "").strip()
    if notes:
        lines.extend([f"> {notes}", ""])

    manual = _manual_open(reg.get("manual") or [])
    if manual:
        lines.extend(["## Manual pins", ""])
        for item in manual:
            title = str(item.get("title") or item.get("id") or "?")
            why = str(item.get("why") or item.get("summary") or "").strip()
            lines.append(f"- **{title}** — {why}")
        lines.append("")

    auto = [i for i in (reg.get("items") or []) if isinstance(i, dict)]
    if auto:
        lines.extend(["## Auto-discovered (open)", ""])
        by_kind: dict[str, list[dict[str, Any]]] = {}
        for item in auto:
            by_kind.setdefault(str(item.get("kind") or "other"), []).append(item)
        for kind in sorted(by_kind):
            lines.append(f"### {kind.replace('_', ' ').title()}")
            lines.append("")
            for item in by_kind[kind]:
                title = str(item.get("title") or item.get("id") or "?")
                why = str(item.get("why") or "").strip()
                src = str(item.get("source") or "")
                lines.append(f"- **{title}** — {why} *(source: {src})*")
            lines.append("")

    closed = [i for i in (reg.get("closed_items") or []) if isinstance(i, dict)]
    if closed:
        lines.extend(["## Recently closed (auto-depopulated)", ""])
        for item in closed[-15:]:
            title = str(item.get("title") or item.get("id") or "?")
            reason = str(item.get("close_reason") or item.get("closed_utc") or "")
            lines.append(f"- ~~{title}~~ — {reason}")
        lines.append("")

    text = "\n".join(lines) + "\n"
    out_path = repo.resolve() / REGISTRY_MD_REL
    out_path.write_text(text, encoding="utf-8")
    return text


def compass_items(repo: Path, *, limit: int = 12) -> list[dict[str, str]]:
    """Dashboard rows for operator compass."""
    rows: list[dict[str, str]] = []
    for item in open_items(repo)[:limit]:
        rows.append(
            {
                "id": str(item.get("id") or ""),
                "title": str(item.get("title") or "?"),
                "why": str(item.get("why") or "").strip(),
                "source": str(item.get("source") or item.get("kind") or "vapor_registry"),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Product vapor registry sync")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--sync", action="store_true", help="Discover + write JSON and MD")
    ap.add_argument("--render-md", action="store_true", help="Render MD from existing JSON")
    ap.add_argument("--json", action="store_true", help="Print open items JSON")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.sync:
        sync_registry(repo)
    elif args.render_md:
        render_markdown(repo)
        print(f"ppe_vapor_registry: rendered {REGISTRY_MD_REL}")
    elif args.json:
        print(json.dumps(open_items(repo), indent=2))
    else:
        sync_registry(repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
