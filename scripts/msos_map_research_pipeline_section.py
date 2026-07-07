"""Inject research pipeline (collect → test → strategy) section into msos_module_map.html."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "docs" / "SOP" / "assets" / "msos_module_map.html"
MARKER = 'id="research-pipeline"'

RESEARCH_PIPELINE_CSS = """
      .rp-intro { font-size: 0.82rem; color: var(--muted); max-width: 52rem; margin: -4px 0 12px; }
      .rp-layers {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        max-width: 52rem;
        margin-bottom: 16px;
      }
      .rp-layer {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 12px 14px;
      }
      .rp-layer.collect { border-left: 3px solid var(--leg); }
      .rp-layer.test { border-left: 3px solid var(--edge); }
      .rp-layer.strategy { border-left: 3px solid var(--muted); opacity: 0.92; }
      .rp-layer h3 { margin: 0 0 6px; font-size: 0.88rem; }
      .rp-layer p { margin: 0; font-size: 0.78rem; color: var(--muted); }
      .rp-layer .status { display: inline-block; margin-top: 8px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
      .rp-layer .status.live { color: var(--green); }
      .rp-layer .status.defer { color: var(--muted); }
      .rp-flow {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 14px 16px;
        max-width: 52rem;
        margin-bottom: 16px;
        overflow-x: auto;
      }
      .rp-flow pre {
        margin: 0;
        font-family: ui-monospace, "Cascadia Code", monospace;
        font-size: 0.74rem;
        line-height: 1.55;
        color: var(--muted);
      }
      .rp-flow .hl-col { color: var(--leg); }
      .rp-flow .hl-test { color: var(--edge); }
      .rp-flow .hl-str { color: var(--muted); }
      .rp-panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 14px;
        max-width: 52rem;
        margin-bottom: 16px;
        overflow-x: auto;
      }
      .rp-panel h3 { margin: 0 0 10px; font-size: 0.82rem; color: var(--muted); font-weight: 700; }
      .rp-template {
        background: var(--panel2);
        border: 1px solid rgba(242, 182, 87, 0.35);
        border-radius: 10px;
        padding: 12px 14px;
        max-width: 52rem;
        margin-bottom: 16px;
        font-size: 0.78rem;
      }
      .rp-template strong { color: var(--edge); }
      .rp-template ol { margin: 8px 0 0; padding-left: 1.2rem; color: var(--muted); }
      .rp-template li { margin-bottom: 4px; }
      .rp-template code { font-size: 0.7rem; }
"""

RESEARCH_PIPELINE_SECTION = """
    <h2 id="research-pipeline">Research pipeline — collect, test, trade (later)</h2>
    <p class="rp-intro">
      Edge research is three plug-in layers: <strong>collectors</strong>, <strong>tests</strong>, <strong>strategies</strong> (future).
      SSOT: <code>config/research_pipeline_registry.json</code>
      · Canon: <a href="../RESEARCH_PIPELINE_V1.md">RESEARCH_PIPELINE_V1.md</a>
      · Daily: <code>run_research_daily.cmd</code>
    </p>

    <div class="rp-layers">
      <div class="rp-layer collect">
        <h3>1 · Collectors</h3>
        <p>Scheduled snapshots → <code>artifacts/</code>. Health: <code>research_archive_health.py --write</code></p>
        <span class="status live">Live — 3 collectors</span>
      </div>
      <div class="rp-layer test">
        <h3>2 · Tests</h3>
        <p>Scan · backtest · tradeability — registry picks eligible tests by archive depth.</p>
        <span class="status live">Live — 3 tests on cross-venue</span>
      </div>
      <div class="rp-layer strategy">
        <h3>3 · Strategies</h3>
        <p>Consume test JSON when <code>strategy_ready</code> — execution deferred.</p>
        <span class="status defer">Deferred</span>
      </div>
    </div>

    <div class="rp-flow">
      <pre>
<span class="hl-col">run_research_daily</span> ──► collectors ──► artifacts/
                              │
                              ├──► <span class="hl-test">scan</span> (≥1d) · <span class="hl-test">backtest</span> (≥14d) · <span class="hl-test">tradeability</span> (≥1d)
                              │
                              └──► <span class="hl-str">strategy (future)</span>
      </pre>
    </div>

    <div class="rp-template">
      <strong>Template — cross-venue PM ↔ Deribit options</strong>
      <ol>
        <li><code>collect_cross_venue_snapshot.cmd</code></li>
        <li><code>run_cross_venue_scan.cmd --latest-snapshot</code></li>
        <li><code>run_cross_venue_backtest.cmd</code></li>
        <li><code>run_cross_venue_tradeability.cmd</code></li>
        <li>Dev smoke: <code>run_cross_venue_collector_dev.cmd --interval 300 --count 12</code></li>
      </ol>
    </div>

    <div class="rp-panel">
      <h3>Collector ↔ test matrix</h3>
      <table>
        <thead>
          <tr>
            <th>Collector</th>
            <th>Archive</th>
            <th>Tests</th>
            <th>VM install</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>cross_venue_event_gap</code></td>
            <td><code>artifacts/cross_venue_snapshots/</code></td>
            <td>scan · backtest · tradeability</td>
            <td><code>install_cross_venue_collector_task.cmd</code></td>
          </tr>
          <tr>
            <td><code>options_horizon_surface</code></td>
            <td><code>artifacts/horizon_surface_archive/</code></td>
            <td>replay scrubber (~30d)</td>
            <td><code>install_horizon_surface_collector_task.cmd</code></td>
          </tr>
          <tr>
            <td><code>implied_distribution_ts</code></td>
            <td><code>artifacts/distribution_snapshots/</code></td>
            <td>dist charts (planned)</td>
            <td><code>install_distribution_stats_collector_task.cmd</code></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="note" style="margin-bottom: 24px">
      <strong>Health artifacts:</strong>
      <code>artifacts/control_plane/RESEARCH_ARCHIVE_HEALTH.json</code>
      · <code>RESEARCH_DAILY_LAST.json</code>
      · also in <code>OPERATOR_STATUS.md</code> Research archives lines.
    </div>
"""


def inject(html: str) -> str:
    if MARKER not in html:
        html = html.replace(
            "    <h2>MSOS pillars</h2>",
            RESEARCH_PIPELINE_SECTION + "\n    <h2>MSOS pillars</h2>",
            1,
        )
    if ".rp-layers {" not in html:
        html = html.replace(
            "      .phase-tag.err { background: rgba(255,100,120,0.12); color: var(--red); }\n    </style>",
            "      .phase-tag.err { background: rgba(255,100,120,0.12); color: var(--red); }"
            + RESEARCH_PIPELINE_CSS
            + "    </style>",
            1,
        )
    if 'href="#research-pipeline"' not in html:
        html = re.sub(
            r'(href="#autobuilder">Autobuilder</a>\n)',
            r'\1        · <a href="#research-pipeline">Research pipeline</a>\n',
            html,
            count=1,
        )
    return html


def main() -> int:
    html = MAP.read_text(encoding="utf-8")
    html = inject(html)
    MAP.write_text(html, encoding="utf-8")
    if MARKER not in html:
        raise SystemExit("inject failed")
    print(f"injected research pipeline section into {MAP.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
