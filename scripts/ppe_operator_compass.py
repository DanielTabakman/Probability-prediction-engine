"""Operator compass — auto-sync human dashboard panels from live operator sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.ppe_human_backlog import open_items
from scripts.ppe_loop_host_guard import loop_host_start_allowed

COMPASS_REL = "artifacts/control_plane/OPERATOR_COMPASS.json"
MAP_REL = "docs/SOP/assets/msos_module_map.html"
REGISTRY_REL = "docs/SOP/PPE_MODULE_REGISTRY_V1.md"
TIER1_MANIFEST_REL = "config/assets_tier1_manifest.yaml"
DIRECTION_REL = "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json"
ET = ZoneInfo("America/New_York")

DO_NOW_BACKLOG_CATEGORIES = frozenset({"ops"})
CRACK_CATCHER_BACKLOG_CATEGORIES = frozenset({"operator", "architecture", "governance", "control-plane"})

MARKER_DO_NOW = 'id="map-do-now"'
MARKER_CRACK = 'id="map-crack-catcher"'
MARKER_VAPOR = 'id="map-vapor-backlog"'
MARKER_PROGRESS = 'id="map-module-progress"'
MARKER_WAITING = 'id="map-waiting-on-time"'
MARKER_RIGHT_NOW = 'id="map-right-now"'
MARKER_LAST_UPDATED = 'id="map-last-updated"'


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _et_display(iso_utc: str | None = None) -> tuple[str, str, str]:
    if iso_utc:
        now_utc = datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
    else:
        now_utc = datetime.now(UTC)
    now_et = now_utc.astimezone(ET)
    iso = now_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return now_et.strftime("%Y-%m-%d"), f"{now_et.strftime('%H:%M')} {now_et.strftime('%Z')}", iso


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _load_yaml_chapters(repo: Path) -> list[dict[str, Any]]:
    path = repo / TIER1_MANIFEST_REL
    if not path.is_file():
        return []
    try:
        import yaml
    except ImportError:
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    chapters = data.get("chapters") or {}
    out: list[dict[str, Any]] = []
    if isinstance(chapters, dict):
        for chapter_id, row in chapters.items():
            if not isinstance(row, dict):
                continue
            out.append({"chapter_id": chapter_id, **row})
    return out


def _horizon_archive_hint(repo: Path) -> tuple[int, int]:
    try:
        from src.data.horizon_surface_archive import archive_meta, default_archive_root

        meta = archive_meta(default_archive_root())
        return int(meta.get("available_days") or 0), int(meta.get("replay_threshold_days") or 30)
    except Exception:
        root = repo / "artifacts" / "horizon_surface_archive"
        if not root.is_dir():
            return 0, 30
        days = sum(1 for p in root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name))
        return days, 30


def _cross_venue_snapshot_days(repo: Path) -> tuple[int, int]:
    try:
        from src.viz.cross_venue_backtest import DEFAULT_MIN_SNAPSHOTS, discover_snapshot_csvs

        root = repo / "artifacts" / "cross_venue_snapshots"
        paths = discover_snapshot_csvs(root)
        days: set[str] = set()
        for path in paths:
            for part in path.parts:
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", part):
                    days.add(part)
                    break
        return len(days), DEFAULT_MIN_SNAPSHOTS
    except Exception:
        return 0, 14


def _archive_crack_catcher_items(repo: Path) -> list[dict[str, str]]:
    try:
        from scripts.research_archive_health import build_archive_health
    except ImportError:
        return []

    titles = {
        "cross_venue_event_gap": "Cross-venue backtest scoring",
        "options_horizon_surface": "Horizon replay scrubber",
        "implied_distribution_ts": "Distribution timeseries archive",
    }
    tails = {
        "cross_venue_event_gap": "scan OK; backtest thin until history deepens",
        "options_horizon_surface": "promote when archive_meta.replay_ready",
        "implied_distribution_ts": "feeds dist timeseries charts when collector task live",
    }
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in build_archive_health(repo).get("collectors") or []:
        if not isinstance(item, dict):
            continue
        cid = str(item.get("id") or "")
        if item.get("stale"):
            key = f"stale_{cid}"
            if key not in seen:
                seen.add(key)
                out.append(
                    {
                        "id": key,
                        "title": f"Stale collector — {item.get('label') or cid}",
                        "why": f"last snapshot {item.get('last_snapshot_utc') or 'never'} · check VM scheduled task",
                        "source": str(item.get("archive_root") or cid),
                    }
                )
        if item.get("ready"):
            continue
        key = f"archive_{cid}"
        if key in seen:
            continue
        seen.add(key)
        have = int(item.get("calendar_days") or 0)
        need = int(item.get("min_calendar_days") or 0)
        out.append(
            {
                "id": key,
                "title": titles.get(cid, str(item.get("label") or cid)),
                "why": f"{have} / {need} daily snapshots · {tails.get(cid, 'VM collector must keep running')}",
                "source": str(item.get("archive_root") or cid),
            }
        )
    return out


def _parse_module_registry(repo: Path) -> list[dict[str, str]]:
    path = repo / REGISTRY_REL
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
        module_id = parts[2].strip("`")
        modules.append(
            {
                "num": num,
                "module_id": module_id,
                "display_name": parts[3],
                "tier": parts[9],
                "priority": parts[10],
                "status": parts[11].replace("**", "").strip(),
                "advance": parts[12],
            }
        )
    return modules


def _verdict_do_now(repo: Path, status: dict[str, Any]) -> list[dict[str, str]]:
    verdict = str(status.get("verdict") or "")
    chapter = str(status.get("chapter_name") or "").strip()
    blocker = str(status.get("blocker") or "").strip()
    plan = str(status.get("phase_plan_path") or "").strip()
    loop_host, _, _ = loop_host_start_allowed()

    if verdict == "RUN_LOCAL":
        action = "run_ppe_local.cmd" if loop_host else "DESKTOP_CONTINUE.cmd"
        title = f"Finish chapter closeout — {chapter or 'active relay'}"
        why = blocker or "IDE product marker present"
        if plan:
            why = f"{why} · {plan}"
        return [{"id": "verdict_run_local", "title": title, "why": f"{why} · {action}", "source": "operator_status"}]

    if verdict == "IDE_BUILD":
        burst = status.get("burst_plan") if isinstance(status.get("burst_plan"), dict) else {}
        burst_tail = ""
        if burst.get("burst_allowed"):
            burst_tail = (
                f" · burst max_workers={burst.get('max_cycles')} band={burst.get('overall_band')} "
                "→ @ppe-director"
            )
        return [
            {
                "id": "verdict_ide_build",
                "title": "IDE BUILD — implement product slice",
                "why": (blocker or "PRODUCT_BLOCKED · ppe_go.cmd → new Agent") + burst_tail,
                "source": "operator_status",
            }
        ]

    if verdict in ("FIX_PLAN", "STALE_STATE", "ERROR"):
        cmds = status.get("commands") or []
        cmd_hint = str(cmds[0]) if cmds else "ppe_go.cmd"
        return [
            {
                "id": f"verdict_{verdict.lower()}",
                "title": f"Relay blocked — {verdict}",
                "why": f"{blocker or verdict} · {cmd_hint}",
                "source": "operator_status",
            }
        ]

    if verdict == "SUPPLY_LOW":
        return [
            {
                "id": "verdict_supply_low",
                "title": "Supply refresh or charter next chapter",
                "why": blocker or "No READY queue item",
                "source": "operator_status",
            }
        ]

    return []


def _asset_batch_do_now(repo: Path) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for chapter in _load_yaml_chapters(repo):
        st = str(chapter.get("status") or "").strip().lower()
        if st not in ("in_progress", "reopened"):
            continue
        cid = str(chapter.get("chapter_id") or "")
        assets = chapter.get("assets") or []
        asset_txt = ", ".join(str(a) for a in assets) if isinstance(assets, list) else ""
        out.append(
            {
                "id": f"asset_{cid}",
                "title": f"Asset batch — {cid}",
                "why": f"{asset_txt} · witness + trust-caveat sign-off before Live pill · say asset batch wave 1",
                "source": "assets_tier1_manifest",
            }
        )
    return out[:2]


def _backlog_do_now(repo: Path) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in open_items(repo, priority="high"):
        cat = str(item.get("category") or "").strip().lower()
        if cat not in DO_NOW_BACKLOG_CATEGORIES:
            continue
        iid = str(item.get("id") or item.get("title") or "backlog")
        out.append(
            {
                "id": f"backlog_{iid}",
                "title": str(item.get("title") or iid),
                "why": str(item.get("summary") or "").strip(),
                "source": "human_steward_backlog",
            }
        )
    return out


def _crack_catcher_items(repo: Path, status: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = _archive_crack_catcher_items(repo)
    seen: set[str] = {item["id"] for item in out}

    supply = status.get("supply") or {}
    queue_ready = int(supply.get("queue_ready") or 0)
    if queue_ready == 0 and str(status.get("verdict") or "") == "SUPPLY_LOW":
        out.append(
            {
                "id": "supply_queue_idle",
                "title": "Relay queue has no READY item",
                "why": str(status.get("blocker") or "Check PHASE_QUEUE.json and backlog promotion"),
                "source": "operator_status",
            }
        )

    for item in open_items(repo, priority="high"):
        cat = str(item.get("category") or "").strip().lower()
        if cat not in CRACK_CATCHER_BACKLOG_CATEGORIES:
            continue
        iid = str(item.get("id") or item.get("title") or "backlog")
        key = f"backlog_{iid}"
        if key in seen:
            continue
        seen.add(key)
        pq = str(item.get("policyQuestion") or "").strip()
        why = str(item.get("summary") or "").strip()
        if pq:
            why = f"{why} · Policy: {pq}"
        out.append(
            {
                "id": key,
                "title": str(item.get("title") or iid),
                "why": why,
                "source": "human_steward_backlog",
            }
        )

    for chapter in _load_yaml_chapters(repo):
        st = str(chapter.get("status") or "").strip().lower()
        if st != "queued":
            continue
        cid = str(chapter.get("chapter_id") or "")
        assets = chapter.get("assets") or []
        if not isinstance(assets, list) or not assets:
            continue
        out.append(
            {
                "id": f"asset_queued_{cid}",
                "title": f"Asset wave queued — {cid}",
                "why": f"Next group after current batch: {', '.join(str(a) for a in assets[:5])}",
                "source": "assets_tier1_manifest",
            }
        )
        break

    return out


def _right_now(repo: Path, status: dict[str, Any]) -> dict[str, str]:
    milestone = "Trader Workflow Integration v1"
    relay_hint = "mvp1_bl_density_smoothing_v1 · forward consistency after supply refresh"
    direction_path = repo / DIRECTION_REL
    if direction_path.is_file():
        try:
            direction = json.loads(direction_path.read_text(encoding="utf-8"))
            pm = direction.get("productMilestone") or {}
            if pm.get("label"):
                milestone = str(pm["label"])
        except json.JSONDecodeError:
            pass

    chapter = str(status.get("chapter_name") or "").strip()
    verdict = str(status.get("verdict") or "")
    if verdict == "RUN_LOCAL" and chapter:
        relay_hint = f"{relay_hint} · closeout: {chapter}"

    return {
        "milestone": milestone,
        "verdict": verdict,
        "relay_hint": relay_hint,
    }


def build_compass(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    if status is None:
        from scripts.ppe_operator_status import prepare_operator_status

        status = prepare_operator_status(repo)

    iso = str(status.get("as_of") or _utc_now())
    date_et, time_et, iso = _et_display(iso)

    do_now = _verdict_do_now(repo, status) + _asset_batch_do_now(repo) + _backlog_do_now(repo)
    deduped: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for item in do_now:
        iid = item["id"]
        if iid in seen_ids:
            continue
        seen_ids.add(iid)
        deduped.append(item)
    do_now = deduped[:5]

    try:
        from scripts.ppe_vapor_registry import compass_panel_items

        vapor_backlog = compass_panel_items(repo)
    except Exception:
        vapor_backlog = []

    return {
        "version": 1,
        "as_of_utc": iso,
        "as_of_et": f"{date_et} {time_et}",
        "do_now": do_now,
        "crack_catcher": _crack_catcher_items(repo, status)[:12],
        "vapor_backlog": vapor_backlog,
        "module_progress": _parse_module_registry(repo),
        "right_now": _right_now(repo, status),
        "sources": {
            "operator_verdict": str(status.get("verdict") or ""),
            "operator_chapter": str(status.get("chapter_name") or ""),
            "burst_allowed": bool((status.get("burst_plan") or {}).get("burst_allowed")),
            "burst_max_workers": (status.get("burst_plan") or {}).get("max_cycles"),
            "burst_band": (status.get("burst_plan") or {}).get("overall_band"),
        },
    }


def write_compass_json(repo: Path, compass: dict[str, Any]) -> Path:
    out = repo / COMPASS_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(compass, indent=2) + "\n", encoding="utf-8")
    return out


def _render_list_section(items: list[dict[str, str]], *, empty: str, ordered: bool) -> str:
    if not items:
        return f"      <p class=\"flow-intro compass-empty\">{_esc(empty)}</p>\n"
    tag = "ol" if ordered else "ul"
    lines = [f"      <{tag}>"]
    for item in items:
        title = _esc(item.get("title") or "")
        why = _esc(item.get("why") or "")
        source = _esc(item.get("source") or "")
        lines.append("        <li>")
        lines.append(f"          <strong>{title}</strong>")
        lines.append(f'          <span class="why">{why} <em class="compass-src">({source})</em></span>')
        lines.append("        </li>")
    lines.append(f"      </{tag}>")
    return "\n".join(lines) + "\n"


def _render_module_progress(modules: list[dict[str, str]]) -> str:
    if not modules:
        return '      <p class="flow-intro compass-empty">No modules parsed from registry.</p>\n'
    lines = ['      <table class="compass-modules">', "        <thead>", "          <tr>"]
    for col in ("#", "Module", "Tier", "Status", "Next / advance"):
        lines.append(f"            <th>{col}</th>")
    lines.extend(["          </tr>", "        </thead>", "        <tbody>"])
    for mod in modules:
        lines.append("          <tr>")
        lines.append(f"            <td>{_esc(mod.get('num') or '')}</td>")
        lines.append(
            f"            <td><strong>{_esc(mod.get('display_name') or '')}</strong>"
            f"<br><code>{_esc(mod.get('module_id') or '')}</code></td>"
        )
        lines.append(f"            <td>{_esc(mod.get('tier') or '')}</td>")
        status = _esc(mod.get("status") or "")
        if "LIVE" in status.upper():
            lines.append(f'            <td><span class="status-live">{status}</span></td>')
        elif "PARTIAL" in status.upper() or "SELECTED" in status.upper():
            lines.append(f'            <td><span class="status-partial">{status}</span></td>')
        else:
            lines.append(f"            <td>{status}</td>")
        lines.append(f"            <td>{_esc(mod.get('advance') or '')}</td>")
        lines.append("          </tr>")
    lines.extend(["        </tbody>", "      </table>"])
    return "\n".join(lines) + "\n"


def _render_right_now(right_now: dict[str, str]) -> str:
    milestone = _esc(right_now.get("milestone") or "")
    relay = _esc(right_now.get("relay_hint") or "")
    verdict = _esc(right_now.get("verdict") or "")
    return (
        "    <div class=\"right-now\" id=\"map-right-now\">\n"
        "      <strong>Right now</strong>\n"
        "      <ul>\n"
        f"        <li><strong>Milestone:</strong> <a href=\"../MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md\">{milestone}</a></li>\n"
        f"        <li><strong>Relay verdict:</strong> <code>{verdict}</code></li>\n"
        f"        <li><strong>Queue hint:</strong> {relay}</li>\n"
        "      </ul>\n"
        "      <span class=\"right-now-links\">\n"
        "        <a href=\"../PPE_INTEGRATED_STATUS.md\">Integrated status</a>\n"
        "        · <a href=\"../../../artifacts/orchestrator/OPERATOR_STATUS.md\">Operator status</a>\n"
        "        · <a href=\"#autobuilder\">Autobuilder</a>\n"
        "        · <a href=\"../HUMAN_STEWARD_BACKLOG.md\">Steward backlog</a>\n"
        "      </span>\n"
        "    </div>\n"
    )


def _render_last_updated(iso: str, date_et: str, time_et: str) -> str:
    return (
        f'      <span class="last-updated" id="map-last-updated" data-last-updated="{iso}">\n'
        f"        Last updated: {date_et} <time datetime=\"{iso}\">{time_et}</time>\n"
        "      </span>\n"
    )


def _replace_div_inner(html: str, div_id: str, inner: str) -> str:
    pattern = rf'(<div[^>]*id="{re.escape(div_id)}"[^>]*>)(.*?)(\n    </div>)'
    match = re.search(pattern, html, flags=re.S)
    if not match:
        return html
    return html[: match.start()] + match.group(1) + "\n" + inner + match.group(3) + html[match.end() :]


def patch_module_map(repo: Path, compass: dict[str, Any]) -> Path:
    path = repo / MAP_REL
    html = path.read_text(encoding="utf-8")
    iso = str(compass.get("as_of_utc") or _utc_now())
    date_et, time_et, iso = _et_display(iso)

    do_now_inner = _render_list_section(
        compass.get("do_now") or [],
        empty="Nothing blocking you on human actions — agents/relay carry the next BUILD.",
        ordered=True,
    )
    crack_inner = _render_list_section(
        compass.get("crack_catcher") or [],
        empty="No crack-catcher signals right now.",
        ordered=False,
    )
    vapor_inner = _render_list_section(
        compass.get("vapor_backlog") or [],
        empty="No open product vapor — or run ppe_vapor_registry.py --sync.",
        ordered=False,
    )
    progress_inner = _render_module_progress(compass.get("module_progress") or [])

    waiting_items = [
        item
        for item in (compass.get("crack_catcher") or [])
        if str(item.get("source") or "").startswith(("horizon_", "cross_venue"))
    ]
    waiting_inner = (
        "      <h3>Needs more days of snapshots</h3>\n"
        + _render_list_section(
            waiting_items,
            empty="No archive-depth gates active.",
            ordered=False,
        )
    )

    html = _replace_div_inner(html, "map-do-now", do_now_inner.rstrip())
    html = _replace_div_inner(html, "map-crack-catcher", crack_inner.rstrip())
    html = _replace_div_inner(html, "map-vapor-backlog", vapor_inner.rstrip())
    html = _replace_div_inner(html, "map-module-progress", progress_inner.rstrip())
    html = _replace_div_inner(html, "map-waiting-on-time", waiting_inner.rstrip())

    rn = _render_right_now(compass.get("right_now") or {})
    rn_start = html.find('    <div class="right-now" id="map-right-now">')
    if rn_start >= 0:
        rn_end = html.find("    </div>", rn_start)
        if rn_end >= 0:
            rn_end = html.find("\n", rn_end + len("    </div>"))
            html = html[:rn_start] + rn.strip() + "\n\n" + html[rn_end + 1 :]

    lu_idx = html.find(MARKER_LAST_UPDATED)
    if lu_idx >= 0:
        lu_start = html.rfind("<span", 0, lu_idx)
        lu_end = html.find("</span>", lu_idx) + len("</span>")
        if lu_start >= 0 and lu_end > lu_start:
            html = html[:lu_start] + _render_last_updated(iso, date_et, time_et).strip() + html[lu_end:]

    maint_old = "Agents bump <code>#map-last-updated</code> (date <em>and</em> UTC time) at steward closeout."
    maint_new = (
        "Auto-sync: <code>python scripts/ppe_operator_compass.py --sync-map</code> "
        "(runs with <code>ppe_operator_status.py</code>). Module cards below are manual reference."
    )
    html = html.replace(maint_old, maint_new)
    if maint_new not in html:
        html = html.replace(
            "Agents bump <code>#map-last-updated</code>",
            "Panels above auto-sync via <code>ppe_operator_compass.py</code>",
        )

    from scripts.msos_map_autobuilder_section import inject as inject_autobuilder_section

    html = inject_autobuilder_section(html)

    path.write_text(html, encoding="utf-8")
    return path


def sync_compass(repo: Path, *, status: dict[str, Any] | None = None, patch_map: bool = True) -> dict[str, Any]:
    try:
        from scripts.ppe_vapor_registry import sync_registry

        sync_registry(repo, render_md=True, patch_compass=False)
    except Exception:
        pass
    compass = build_compass(repo, status=status)
    write_compass_json(repo, compass)
    if patch_map:
        patch_module_map(repo, compass)
    return compass


def _trim_phone(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(text or "").strip())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def phone_snippet_lines(
    repo: Path,
    *,
    compass: dict[str, Any] | None = None,
    max_do_now: int = 3,
    max_crack: int = 2,
) -> list[str]:
    """Short ntfy lines from compass — Do now + crack catcher (weekly digest + on-demand)."""
    if compass is None:
        compass = build_compass(repo)
    do_now = [i for i in (compass.get("do_now") or []) if isinstance(i, dict)]
    crack = [i for i in (compass.get("crack_catcher") or []) if isinstance(i, dict)]
    if not do_now and not crack:
        verdict = str((compass.get("sources") or {}).get("operator_verdict") or "")
        if verdict:
            return ["Your compass", f"- Relay: {verdict} — nothing else blocking you"]
        return []

    lines = ["Your compass (module map)"]
    for item in do_now[:max_do_now]:
        title = _trim_phone(str(item.get("title") or "?"), 72)
        why = _trim_phone(str(item.get("why") or ""), 96)
        lines.append(f"- Do now: {title}" + (f" — {why}" if why else ""))
    extra_do = len(do_now) - max_do_now
    if extra_do > 0:
        lines.append(f"- +{extra_do} more do-now — open msos_module_map.html")

    for item in crack[:max_crack]:
        title = _trim_phone(str(item.get("title") or "?"), 72)
        why = _trim_phone(str(item.get("why") or ""), 80)
        lines.append(f"- Watch: {title}" + (f" — {why}" if why else ""))
    extra_crack = len(crack) - max_crack
    if extra_crack > 0:
        lines.append(f"- +{extra_crack} crack-catcher items — open msos_module_map.html")
    return lines


def write_notify_snippet(repo: Path, *, compass: dict[str, Any] | None = None) -> Path | None:
    """Write artifacts/control_plane/OPERATOR_COMPASS_NOTIFY.json for ntfy helpers."""
    lines = phone_snippet_lines(repo, compass=compass)
    if not lines:
        return None
    out = repo / "artifacts/control_plane/OPERATOR_COMPASS_NOTIFY.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "as_of_utc": str((compass or {}).get("as_of_utc") or _utc_now()),
        "phone_lines": lines,
        "do_now_count": len((compass or {}).get("do_now") or []),
        "crack_catcher_count": len((compass or {}).get("crack_catcher") or []),
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build operator compass and sync MSOS module map panels")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="Print compass JSON")
    ap.add_argument("--sync-map", action="store_true", help="Patch msos_module_map.html (default when invoked directly)")
    ap.add_argument("--no-map", action="store_true", help="Write JSON only; do not patch HTML")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    patch_map = not args.no_map
    if args.sync_map:
        patch_map = True
    elif argv is None or (len(argv) == 1 and argv[0] in ("-h", "--help")):
        patch_map = True
    elif not args.json and not args.no_map:
        patch_map = True

    compass = sync_compass(repo, patch_map=patch_map)
    if args.json:
        print(json.dumps(compass, indent=2))
    else:
        print(f"ppe_operator_compass: wrote {COMPASS_REL}")
        if patch_map:
            print(f"ppe_operator_compass: patched {MAP_REL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
