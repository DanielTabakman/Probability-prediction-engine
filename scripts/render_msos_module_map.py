"""Render MSOS module map HTML from PPE_MODULE_REGISTRY.json (SSOT)."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = Path("docs/SOP/PPE_MODULE_REGISTRY.json")
DEFAULT_OUTPUT = Path("docs/SOP/assets/msos_module_map.html")

PILLAR_TAG_CLASS = {
    "WORKFLOW": "tag-wf",
    "EDGE": "tag-edge",
    "LEGIBILITY": "tag-leg",
    "INFRA": "tag-infra",
}

STATUS_CLASS = {
    "LIVE": "status-live",
    "PARTIAL": "status-partial",
    "PLANNED": "status-planned",
}

PRIO_CLASS = {
    "P0": "prio-p0",
    "P1": "prio-p1",
    "P2": "prio-p2",
    "side": "prio-side",
}


def _repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "docs" / "SOP").is_dir():
            return parent
    return Path.cwd()


def load_registry(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _pillar_tags(pillars: list[str]) -> str:
    parts: list[str] = []
    for pillar in pillars:
        css = PILLAR_TAG_CLASS.get(pillar, "tag-infra")
        parts.append(f'<span class="tag {css}">{_esc(pillar)}</span>')
    return " ".join(parts)


def _status_cell(status: str, suffix: str = "") -> str:
    css = STATUS_CLASS.get(status, "status-planned")
    return f'<td class="{css}">{_esc(status + suffix)}</td>'


def _prio_cell(priority: str) -> str:
    css = PRIO_CLASS.get(priority, "prio-side")
    return f'<td class="{css}">{_esc(priority)}</td>'


def render_html(data: dict[str, Any], *, repo_root: Path) -> str:
    as_of = _esc(data.get("as_of", ""))
    html_abs = repo_root / str(data.get("html_output", DEFAULT_OUTPUT.as_posix()))

    pillars_html = []
    for pillar in data.get("pillars", []):
        css = pillar.get("css_class", "")
        cls = f'pillar {css}'.strip()
        pillars_html.append(
            f'      <div class="{_esc(cls)}">\n'
            f'        <strong>{_esc(pillar["label"])}</strong>\n'
            f'        <span>{_esc(pillar["summary"])}</span>\n'
            f"      </div>"
        )

    def flow_items(items: list[dict[str, Any]]) -> str:
        rows = []
        for item in items:
            detail = item.get("detail", "")
            small = f"<small>{_esc(detail)}</small>" if detail else ""
            rows.append(f'        <div class="flow-item">{_esc(item["label"])}{small}</div>')
        return "\n".join(rows)

    flow = data.get("data_flow", {})
    module_rows: list[str] = []
    for mod in data.get("modules", []):
        ordinal = mod.get("ordinal", "")
        name = mod["display_name"]
        mid = mod["module_id"]
        route = mod.get("route", "")
        tier = f'{mod.get("tier_current", "?")} → {mod.get("tier_target", "?")}'
        advance = mod.get("advance", "")
        advance_cls = ' class="advance-yes"' if mod.get("advance_highlight") else ""
        module_rows.append(
            "        <tr>\n"
            f"          <td>{_esc(ordinal)}</td>\n"
            f"          <td><strong>{_esc(name)}</strong><br><code>{_esc(mid)}</code><br>{_esc(route)}</td>\n"
            f"          <td>{_pillar_tags(mod.get('pillars', []))}</td>\n"
            f"          <td>{_esc(mod.get('ship_to', ''))}</td>\n"
            f'          <td class="tier">{_esc(tier)}</td>\n'
            f"          {_prio_cell(mod.get('priority', 'side'))}\n"
            f"          {_status_cell(mod.get('status', 'PLANNED'), mod.get('status_suffix', ''))}\n"
            f"          <td{advance_cls}>{_esc(advance)}</td>\n"
            "        </tr>"
        )

    wf = data.get("workflow_surface", {})
    module_rows.append(
        "        <tr>\n"
        "          <td>—</td>\n"
        f"          <td><strong>{_esc(wf.get('display_name', 'Workflow'))}</strong> ({_esc(wf.get('detail', ''))})</td>\n"
        f"          <td>{_pillar_tags(wf.get('pillars', ['WORKFLOW']))}</td>\n"
        f"          <td>{_esc(wf.get('ship_to', ''))}</td>\n"
        '          <td class="tier">—</td>\n'
        f"          {_prio_cell(wf.get('priority', 'P0'))}\n"
        f"          {_status_cell(wf.get('status', 'LIVE'))}\n"
        f"          <td>{_esc(wf.get('advance', ''))}</td>\n"
        "        </tr>"
    )

    tier_rows = []
    for tier in data.get("integration_tiers", []):
        q = tier.get("charter_question", "")
        if tier["id"] == "T3":
            q = f"<strong>Why</strong> collect? What subset? How often?"
        tier_rows.append(
            f'        <tr><td class="tier">{_esc(tier["id"])}</td>'
            f"<td>{_esc(tier['delivers'])}</td><td>{q}</td></tr>"
        )

    cards: list[str] = []
    for mod in data.get("modules", []):
        advance_badge = ' · <span class="advance-yes">ADVANCE</span>' if mod.get("advance_highlight") else ""
        cards.append(
            '      <div class="card">\n'
            f'        <h3>{_esc(mod["display_name"])}</h3>\n'
            f'        <div class="meta">{_esc(mod.get("class", ""))} · '
            f'{_esc(mod.get("tier_current", ""))} · {_esc(mod.get("priority", ""))}{advance_badge}</div>\n'
            f'        <p>{_esc(mod.get("card_summary", ""))}</p>\n'
            f'        <div class="next"><strong>Next:</strong> {_esc(mod.get("advance", ""))}</div>\n'
            "      </div>"
        )

    meta = data.get("meta_infra_card", {})
    cards.append(
        '      <div class="card">\n'
        f'        <h3>{_esc(meta.get("display_name", "Meta infra"))}</h3>\n'
        f'        <div class="meta">{_esc(meta.get("detail", ""))}</div>\n'
        f'        <p>{_esc(meta.get("card_summary", ""))}</p>\n'
        f'        <div class="next"><strong>Next:</strong> {_esc(meta.get("advance", ""))}</div>\n'
        "      </div>"
    )

    open_path = html_abs.resolve()
    file_url = open_path.as_uri()

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="noindex, nofollow" />
    <meta name="theme-color" content="#05090f" />
    <title>MSOS module map — operator</title>
    <style>
      :root {{
        --bg: #05090f;
        --panel: #0e1c2d;
        --panel2: #122438;
        --line: #1e3145;
        --text: #edf5ff;
        --muted: #8ea4bd;
        --teal: #43e7d3;
        --amber: #f2b657;
        --violet: #a78bfa;
        --green: #6ee7a8;
        --wf: #43e7d3;
        --edge: #f2b657;
        --leg: #a78bfa;
        --infra: #8ea4bd;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        background: var(--bg);
        color: var(--text);
        line-height: 1.45;
        padding: 16px 18px 48px;
      }}
      h1 {{ font-size: 1.35rem; margin: 0 0 6px; }}
      .sub {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 12px; max-width: 56rem; }}
      .sub a {{ color: var(--teal); }}
      .open-box {{
        background: var(--panel2);
        border: 1px solid var(--teal);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 20px;
        font-size: 0.82rem;
        max-width: 56rem;
      }}
      .open-box code {{ color: var(--teal); word-break: break-all; }}
      h2 {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: var(--teal);
        margin: 28px 0 12px;
        font-weight: 700;
      }}
      .pillars {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
      }}
      .pillar {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 12px 14px;
        border-left: 3px solid var(--teal);
      }}
      .pillar.edge {{ border-left-color: var(--edge); }}
      .pillar.leg {{ border-left-color: var(--leg); }}
      .pillar strong {{ display: block; font-size: 0.95rem; margin-bottom: 4px; }}
      .pillar span {{ font-size: 0.8rem; color: var(--muted); }}
      .legend {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px 16px;
        font-size: 0.75rem;
        color: var(--muted);
        margin: 12px 0 16px;
      }}
      .legend i {{
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 2px;
        margin-right: 4px;
        vertical-align: middle;
      }}
      .flow {{
        display: grid;
        grid-template-columns: 1fr auto 1fr auto 1fr;
        gap: 8px;
        align-items: stretch;
        margin-bottom: 24px;
        overflow-x: auto;
      }}
      @media (max-width: 900px) {{
        .flow {{ grid-template-columns: 1fr; }}
        .flow-arrow {{ display: none; }}
      }}
      .flow-col {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 12px;
        min-width: 160px;
      }}
      .flow-col h3 {{
        margin: 0 0 10px;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--muted);
      }}
      .flow-item {{
        font-size: 0.82rem;
        padding: 6px 8px;
        margin-bottom: 6px;
        background: var(--panel2);
        border-radius: 6px;
        border: 1px solid var(--line);
      }}
      .flow-item small {{ display: block; color: var(--muted); font-size: 0.72rem; margin-top: 2px; }}
      .flow-arrow {{
        display: flex;
        align-items: center;
        color: var(--muted);
        font-size: 1.4rem;
        padding: 0 4px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.78rem;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
      }}
      th, td {{
        padding: 8px 10px;
        text-align: left;
        border-bottom: 1px solid var(--line);
        vertical-align: top;
      }}
      th {{
        background: var(--panel2);
        color: var(--muted);
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }}
      tr:last-child td {{ border-bottom: none; }}
      tr:hover td {{ background: rgba(67, 231, 211, 0.04); }}
      .tag {{
        display: inline-block;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 600;
        margin: 1px 2px 1px 0;
      }}
      .tag-wf {{ background: rgba(67,231,211,0.15); color: var(--wf); }}
      .tag-edge {{ background: rgba(242,182,87,0.15); color: var(--edge); }}
      .tag-leg {{ background: rgba(167,139,250,0.15); color: var(--leg); }}
      .tag-infra {{ background: rgba(142,164,189,0.15); color: var(--infra); }}
      .status-live {{ color: var(--green); }}
      .status-partial {{ color: var(--amber); }}
      .status-planned {{ color: var(--muted); }}
      .tier {{ font-family: ui-monospace, monospace; font-size: 0.72rem; color: var(--teal); }}
      .prio-p0 {{ color: var(--green); font-weight: 700; }}
      .prio-p1 {{ color: var(--teal); }}
      .prio-p2 {{ color: var(--amber); }}
      .prio-side {{ color: var(--muted); }}
      .advance-yes {{ color: var(--green); font-weight: 600; }}
      .cards {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 12px;
      }}
      .card {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 14px;
      }}
      .card h3 {{ margin: 0 0 8px; font-size: 0.95rem; }}
      .card .meta {{ font-size: 0.72rem; color: var(--muted); margin-bottom: 10px; }}
      .card p {{ margin: 0 0 8px; font-size: 0.82rem; color: var(--muted); }}
      .card .next {{ font-size: 0.78rem; border-top: 1px solid var(--line); padding-top: 8px; margin-top: 8px; }}
      .card .next strong {{ color: var(--amber); }}
      .note {{
        background: var(--panel);
        border: 1px dashed var(--line);
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 0.82rem;
        color: var(--muted);
        max-width: 56rem;
      }}
      .note strong {{ color: var(--text); }}
      .loop-diagram {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 16px;
        font-size: 0.8rem;
        overflow-x: auto;
      }}
      .loop-diagram pre {{
        margin: 0;
        color: var(--muted);
        font-family: ui-monospace, "Cascadia Code", monospace;
        line-height: 1.5;
      }}
      footer {{ margin-top: 32px; font-size: 0.72rem; color: var(--muted); }}
    </style>
  </head>
  <body>
    <h1>MSOS module map</h1>
    <p class="sub">
      Auto-generated from <a href="../PPE_MODULE_REGISTRY.json">PPE_MODULE_REGISTRY.json</a>
      · Markdown: <a href="../PPE_MODULE_REGISTRY_V1.md">PPE_MODULE_REGISTRY_V1.md</a>
      · As-of {as_of}
    </p>

    <div class="open-box">
      <strong>How to open (local file on your PC)</strong><br />
      Path: <code>{_esc(open_path)}</code><br />
      Double-click the file in File Explorer, or paste into your browser address bar:<br />
      <code>{_esc(file_url)}</code><br />
      Regenerate after editing JSON: <code>python scripts/render_msos_module_map.py</code>
    </div>

    <h2>MSOS pillars</h2>
    <div class="pillars">
{chr(10).join(pillars_html)}
    </div>

    <div class="legend">
      <span><i style="background:var(--wf)"></i> Workflow</span>
      <span><i style="background:var(--edge)"></i> Edge</span>
      <span><i style="background:var(--leg)"></i> Legibility</span>
      <span>T0 → T4 integration tiers</span>
    </div>

    <h2>Data → processing → output</h2>
    <div class="flow">
      <div class="flow-col">
        <h3>Sources</h3>
{flow_items(flow.get("sources", []))}
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-col">
        <h3>Processing (Python)</h3>
{flow_items(flow.get("processing", []))}
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-col">
        <h3>Outputs</h3>
{flow_items(flow.get("outputs", []))}
      </div>
    </div>

    <h2>Registered modules</h2>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Module</th>
          <th>Pillar</th>
          <th>Ship-to</th>
          <th>Tier</th>
          <th>Prio</th>
          <th>Status</th>
          <th>Advance?</th>
        </tr>
      </thead>
      <tbody>
{chr(10).join(module_rows)}
      </tbody>
    </table>

    <h2>Integration tiers (charter depth)</h2>
    <table>
      <thead>
        <tr>
          <th>Tier</th>
          <th>Delivers</th>
          <th>Charter question</th>
        </tr>
      </thead>
      <tbody>
{chr(10).join(tier_rows)}
      </tbody>
    </table>

    <div class="note" style="margin-top:12px">
      <strong>T3 rule:</strong> No collector slice without archive charter (hypothesis, consumer, granularity, retention, non-goals).
    </div>

    <h2>Trader loop (simplified)</h2>
    <div class="loop-diagram">
      <pre>
  LEGIBILITY                    WORKFLOW                         EDGE
  ──────────                    ────────                         ────
  Implied distribution ──┐
  Options Horizon ───────┼──► Market relationship ──► Thesis ──► Expression planner ──► Monitor
                         │    (disagreement today;              (sim only)              ▲
  Forward consistency ───┘     more modes later)                                        │
       (trust signal) ────────────────────────────────────────────────────────────────────┘
      </pre>
    </div>

    <h2>Module cards — where we left off</h2>
    <div class="cards">
{chr(10).join(cards)}
    </div>

    <h2>Active BUILD priorities</h2>
    <div class="note">
      <strong>Milestone:</strong> {_esc(data.get("milestone_note", ""))}
    </div>

    <footer>
      Generated by scripts/render_msos_module_map.py · SSOT: docs/SOP/PPE_MODULE_REGISTRY.json · noindex
    </footer>
  </body>
</html>
"""


def write_html(
    *,
    registry_path: Path,
    output_path: Path,
    repo_root: Path,
) -> None:
    data = load_registry(registry_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(data, repo_root=repo_root), encoding="utf-8", newline="\n")


def check_html_fresh(*, registry_path: Path, output_path: Path, repo_root: Path) -> bool:
    if not output_path.is_file():
        return False
    expected = render_html(load_registry(registry_path), repo_root=repo_root)
    return output_path.read_text(encoding="utf-8") == expected


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render MSOS module map HTML from registry JSON.")
    ap.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--repo-root", type=Path, default=None)
    ap.add_argument("--write", action="store_true", help="Write HTML (default when neither --check nor --write)")
    ap.add_argument("--check", action="store_true", help="Exit 1 if HTML is stale vs JSON")
    args = ap.parse_args(argv)

    repo = (args.repo_root or _repo_root()).resolve()
    registry = (repo / args.registry).resolve()
    output = (repo / args.output).resolve()

    if not registry.is_file():
        print(f"registry missing: {registry}", file=sys.stderr)
        return 2

    if args.check:
        if check_html_fresh(registry_path=registry, output_path=output, repo_root=repo):
            print("msos module map HTML is up to date")
            return 0
        print(
            "msos module map HTML is stale — run: python scripts/render_msos_module_map.py --write",
            file=sys.stderr,
        )
        return 1

    write_html(registry_path=registry, output_path=output, repo_root=repo)
    print(f"wrote {output.relative_to(repo)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
