"""Patch MSOS operator module map — idempotent operator dashboard sections."""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "docs" / "SOP" / "assets" / "msos_module_map.html"

MARKER_RIGHT_NOW = 'id="map-right-now"'
MARKER_GATHER_CARD = 'class="gather"'


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:00Z")


def _stamp_display() -> tuple[str, str]:
    now = datetime.now(UTC)
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M UTC")


def _operator_header() -> str:
    date_s, time_s = _stamp_display()
    iso = _stamp()
    return f"""    <p class="sub">
      Living operator chart — modules, data, tiers, priorities.
      Canon markdown: <a href="../PPE_MODULE_REGISTRY_V1.md">PPE_MODULE_REGISTRY_V1.md</a>
      · Forward consistency: <a href="../FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md">program doc</a>
      <span class="last-updated" id="map-last-updated" data-last-updated="{iso}">
        Last updated: {date_s} <time datetime="{iso}">{time_s}</time>
      </span>
    </p>

    <div class="maint-note">
      <strong>Refresh workflow:</strong> If you <code>git pull</code> often, browser refresh is usually enough.
      This file tracks your current branch — it does not poll relay or VM live.
      Agents bump <code>#map-last-updated</code> (date <em>and</em> UTC time) at steward closeout.
    </div>

    <div class="right-now" id="map-right-now">
      <strong>Right now</strong>
      <ul>
        <li><strong>Milestone:</strong> <a href="../MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md">Trader Workflow Integration v1</a></li>
        <li><strong>Last closed:</strong> Options Horizon region workflow v1 (2026-06-29)</li>
        <li><strong>Relay queue hint:</strong> <code>mvp1_bl_density_smoothing_v1</code> first · forward consistency after supply refresh</li>
      </ul>
      <span class="right-now-links">
        <a href="../PPE_INTEGRATED_STATUS.md">Integrated status</a>
        · <a href="../AGENT_CONTINUITY_BRIEF.md">Continuity brief</a>
        · <a href="../HUMAN_STEWARD_BACKLOG.md">Steward backlog</a>
      </span>
    </div>

    <div class="quick-links" id="map-quick-links">
      <a href="https://app.marketstructureos.com/options-horizon">/options-horizon</a>
      <a href="https://app.marketstructureos.com/strategy-lab">/strategy-lab</a>
      <a href="https://app.marketstructureos.com/strategy-lab/expression">/strategy-lab/expression</a>
      <a class="planned" href="../EXPOSURE_MENU_PROGRAM_V1.md">/exposure (chartered)</a>
      <a class="planned" href="../FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md">/forward-consistency (planned)</a>
    </div>

    <h2>Your attention — human to-do</h2>
    <div class="op-section todo-panel">
      <h3>Bottlenecks — needs you to keep it moving</h3>
      <ol>
        <li>
          <strong>Exposure menu v0 — approve READY → relay</strong>
          <span class="why">Chartered front door for “I want X exposure” · NVDA + BTC paths.</span>
        </li>
        <li>
          <strong>VM collectors — confirm tasks on ppeloop</strong>
          <span class="why"><code>install_horizon_surface_collector_task.cmd</code> + <code>install_cross_venue_collector_task.cmd</code> after pull.</span>
        </li>
        <li>
          <strong>Next asset batch — pick the group</strong>
          <span class="why">Sign off trust caveats after witness before Live pill on new symbols.</span>
        </li>
      </ol>
    </div>

    <h2>Waiting on time / data</h2>
    <p class="flow-intro">
      Blocked by clock or archive depth — not a human decision today. VM daily collectors must keep running.
    </p>
    <div class="op-section time-panel">
      <h3>Needs more days of snapshots</h3>
      <ul>
        <li>
          <strong>Horizon replay scrubber</strong>
          <span class="when">Chartered · <span class="archive-hint">~8 / 30</span> daily surface snapshots (steward est.)</span>
        </li>
        <li>
          <strong>Cross-venue backtest scoring</strong>
          <span class="when"><span class="archive-hint">~6 / 14</span> daily PM ↔ Deribit snapshots (steward est.)</span>
        </li>
        <li>
          <strong>Forward consistency T3 archive</strong>
          <span class="when">After radar dashboard (T1–T2) ships</span>
        </li>
        <li>
          <strong>Horizon surface replay UX</strong>
          <span class="when">Daily <code>collect_horizon_surface_snapshot</code> on VM</span>
        </li>
      </ul>
    </div>

    <h2>Recently shipped</h2>
    <div class="op-section shipped-panel">
      <h3>Last closeouts — what landed on main</h3>
      <ul>
        <li>
          <strong>Forward consistency radar ch.1–2</strong>
          <span class="when">2026-06-29 · SELECTION approved</span>
        </li>
        <li>
          <strong>Options Horizon region workflow v1</strong>
          <span class="when">2026-06-29</span>
        </li>
      </ul>
    </div>

    <h2>When you have bandwidth — backlog</h2>
    <p class="flow-intro">Secondary — pick when bottlenecks above are clear.</p>
    <div class="backlog-grid">
      <div class="backlog-panel">
        <h3>Product depth</h3>
        <ul>
          <li>Self-serve onboarding polish<span class="tag-line">Trader Workflow · P1</span></li>
        </ul>
      </div>
    </div>

    <h2>MSOS pillars</h2>"""


def _ensure_base_from_commit() -> None:
    if "Your attention" in MAP.read_text(encoding="utf-8"):
        return
    subprocess.run(
        ["git", "checkout", "89ca70be", "--", str(MAP.relative_to(REPO))],
        cwd=REPO,
        check=True,
    )


def _inject_css(html: str) -> str:
    if ".maint-note {" in html and ".right-now {" in html:
        return html
    dashboard_css = """
      .maint-note {
        background: var(--panel2);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 0.78rem;
        color: var(--muted);
        max-width: 52rem;
        margin-bottom: 16px;
      }
      .maint-note strong { color: var(--teal); }
      .maint-note code { font-size: 0.72rem; }
      .flow-intro {
        font-size: 0.84rem;
        color: var(--muted);
        max-width: 52rem;
        margin: -4px 0 14px;
      }
      .op-section { max-width: 52rem; margin-bottom: 8px; }
      .shipped-panel, .time-panel, .todo-panel {
        background: var(--panel);
        border-radius: 10px;
        padding: 14px 16px;
      }
      .shipped-panel { border: 1px solid rgba(110, 231, 168, 0.35); }
      .time-panel { border: 1px solid var(--violet); }
      .todo-panel { border: 1px solid var(--amber); }
      .shipped-panel h3 { margin: 0 0 10px; font-size: 0.95rem; color: var(--green); }
      .time-panel h3 { margin: 0 0 10px; font-size: 0.95rem; color: var(--violet); }
      .todo-panel h3 { margin: 0 0 10px; font-size: 0.95rem; color: var(--amber); }
      .shipped-panel ul, .time-panel ul, .todo-panel ol {
        margin: 0;
        padding-left: 1.2rem;
        font-size: 0.84rem;
      }
      .shipped-panel li, .time-panel li, .todo-panel li { margin-bottom: 8px; }
      .shipped-panel .when, .time-panel .when, .todo-panel .why {
        display: block;
        font-size: 0.76rem;
        color: var(--muted);
        margin-top: 2px;
      }
      .backlog-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 12px;
        margin-bottom: 8px;
        max-width: 52rem;
      }
      .backlog-panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 12px 14px;
      }
      .backlog-panel h3 { margin: 0 0 8px; font-size: 0.82rem; color: var(--muted); font-weight: 700; }
      .backlog-panel ul { margin: 0; padding-left: 1.1rem; font-size: 0.78rem; }
      .backlog-panel .tag-line { display: block; font-size: 0.68rem; color: var(--muted); margin-top: 2px; }
      .backlog-panel.defer { border-style: dashed; opacity: 0.85; }
      .right-now {
        background: var(--panel);
        border: 1px solid var(--line);
        border-left: 3px solid var(--teal);
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 0.82rem;
        max-width: 52rem;
        margin-bottom: 12px;
      }
      .right-now > strong { color: var(--teal); display: block; margin-bottom: 8px; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; }
      .right-now ul { margin: 0 0 8px; padding-left: 1.2rem; }
      .right-now-links { font-size: 0.76rem; color: var(--muted); }
      .right-now-links a { color: var(--teal); }
      .quick-links { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; max-width: 52rem; }
      .quick-links a {
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid var(--line);
        background: var(--panel2);
        color: var(--teal);
        text-decoration: none;
      }
      .quick-links a.planned { color: var(--muted); border-style: dashed; }
      .flow-desc { font-size: 0.82rem; color: var(--muted); max-width: 52rem; margin: -4px 0 12px; }
      .archive-hint { color: var(--violet); font-weight: 600; }
      .last-updated { display: inline-block; font-size: 0.78rem; color: var(--green); background: rgba(110, 231, 168, 0.1); border: 1px solid rgba(110, 231, 168, 0.25); border-radius: 6px; padding: 2px 8px; margin-left: 6px; font-weight: 600; }
      .last-updated time { font-weight: 600; }
"""
    if ".maint-note {" not in html:
        html = html.replace("      footer { margin-top: 32px;", dashboard_css + "      footer { margin-top: 32px;")
    elif ".right-now {" not in html:
        html = html.replace(
            "      .backlog-panel.defer { border-style: dashed; opacity: 0.85; }",
            "      .backlog-panel.defer { border-style: dashed; opacity: 0.85; }" + dashboard_css,
        )
    return html


def _inject_card_css(html: str) -> str:
    if ".card .gather" in html:
        return html
    return html.replace(
        "      .card .next strong { color: var(--amber); }\n",
        "      .card .next strong { color: var(--amber); }\n"
        "      .card .gather, .card .action, .card .bottleneck { font-size: 0.78rem; margin: 0 0 6px; "
        "padding-left: 10px; border-left: 2px solid var(--line); }\n"
        "      .card .gather { border-left-color: var(--leg); }\n"
        "      .card .action { border-left-color: var(--teal); }\n"
        "      .card .bottleneck { border-left-color: var(--amber); margin-bottom: 0; }\n"
        "      .card .gather strong, .card .action strong, .card .bottleneck strong { display: block; "
        "font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }\n"
        "      .card .gather strong { color: var(--leg); }\n"
        "      .card .action strong { color: var(--teal); }\n"
        "      .card .bottleneck strong { color: var(--amber); }\n"
        "      .card-ongoing { border-color: var(--teal); box-shadow: 0 0 0 1px rgba(67,231,211,0.12); }\n",
    )


def main() -> None:
    _ensure_base_from_commit()
    html = MAP.read_text(encoding="utf-8")
    html = _inject_css(html)
    html = _inject_card_css(html)

    from scripts.msos_map_autobuilder_section import inject as inject_autobuilder_section

    html = inject_autobuilder_section(html)

    if MARKER_RIGHT_NOW not in html:
        header_match = re.search(
            r"    <p class=\"sub\">.*?</div>\n\n    <h2>MSOS pillars</h2>",
            html,
            re.S,
        )
        if not header_match:
            sys.exit("could not find header anchor for operator dashboard")
        html = html[: header_match.start()] + _operator_header() + html[header_match.end() :]

    html = html.replace(
        "<h2>Module cards — where we left off</h2>",
        '<h2>Module cards — gather, act, bottleneck</h2>\n'
        '    <p class="flow-intro">Per module: what you learn, what you can do, what is stuck waiting on you.</p>',
    )

    if "Universe expansion" not in html:
        html = html.replace(
            "        <tr>\n          <td>—</td>\n          <td><strong>Workflow</strong> (thesis, confirm, monitor, history)</td>",
            "        <tr>\n          <td>7</td>\n"
            "          <td><strong>Universe expansion</strong><br><code>tradeable_universe</code><br>meta infra · rolling</td>\n"
            '          <td><span class="tag tag-infra">INFRA</span></td>\n'
            "          <td>OPERATOR</td>\n"
            '          <td class="tier">ongoing</td>\n'
            '          <td class="prio-p0">P0</td>\n'
            '          <td class="status-live">LIVE (rolling)</td>\n'
            "          <td>Next asset group witness</td>\n"
            "        </tr>\n"
            "        <tr>\n          <td>—</td>\n"
            "          <td><strong>Workflow</strong> (thesis, confirm, monitor, history)</td>",
        )

    html = re.sub(
        r"    <footer>.*?</footer>",
        "    <footer>\n"
        "      Open locally: <code>docs/SOP/assets/msos_module_map.html</code>\n"
        "      · <code>git pull</code> then refresh · Gate: "
        "<code>tests/test_msos_module_map_operator_sections.py</code>\n"
        "      · Sync: <code>python scripts/ppe_operator_compass.py --sync-map</code>\n"
        "      · Cards patch: <code>python scripts/patch_msos_module_map.py</code>\n"
        "      · noindex\n"
        "    </footer>",
        html,
        flags=re.S,
    )

    MAP.write_text(html, encoding="utf-8")
    html = MAP.read_text(encoding="utf-8")
    assert html.index("Your attention") < html.index("Waiting on time")
    assert MARKER_RIGHT_NOW in html
    print("patched ok")


if __name__ == "__main__":
    main()
