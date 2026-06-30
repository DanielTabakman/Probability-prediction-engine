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
      Edge research is three plug-in layers: <strong>collectors</strong> save comparable snapshots,
      <strong>tests</strong> score archives, <strong>strategies</strong> (future) turn proven reports into trade rules.
      Canon: <a href="../RESEARCH_PIPELINE_V1.md">RESEARCH_PIPELINE_V1.md</a>
      · Cross-venue ops: <a href="../CROSS_VENUE_COLLECTOR_OPS_V1.md">collector runbook</a>
    </p>

    <div class="rp-layers">
      <div class="rp-layer collect">
        <h3>1 · Collectors</h3>
        <p>Scheduled snapshots → <code>artifacts/</code>. Each has an archive contract (columns, cadence, why).</p>
        <span class="status live">Live — 3 collectors</span>
      </div>
      <div class="rp-layer test">
        <h3>2 · Tests</h3>
        <p>Read matching archives only. Screen gaps, backtest accuracy, replay UX — reports out, not orders.</p>
        <span class="status live">Live — cross-venue scan + backtest</span>
      </div>
      <div class="rp-layer strategy">
        <h3>3 · Strategies</h3>
        <p>Consume test reports after tradeability proof. Execution bots — separate milestone, not MVP1.</p>
        <span class="status defer">Deferred</span>
      </div>
    </div>

    <div class="rp-flow">
      <pre>
<span class="hl-col">collect_cross_venue_snapshot</span> ──► artifacts/cross_venue_snapshots/*.csv
                                              │
                                              ├──► <span class="hl-test">run_cross_venue_scan</span> ──► latest gap report (today)
                                              │
                                              └──► <span class="hl-test">run_cross_venue_backtest</span> ──► Brier scores (after resolve)
                                                        │
                                                        └──► <span class="hl-str">strategy spec (future)</span> ──► autotrader (out of scope)
      </pre>
    </div>

    <div class="rp-template">
      <strong>Template — cross-venue PM ↔ Deribit options</strong>
      <ol>
        <li><strong>Collect:</strong> <code>collect_cross_venue_snapshot.cmd</code> — PM Yes% vs options P(BTC &gt; K)</li>
        <li><strong>Screen:</strong> <code>run_cross_venue_scan.cmd</code> — rank largest gaps today</li>
        <li><strong>Test:</strong> <code>run_cross_venue_backtest.cmd</code> — who was right after events resolve</li>
        <li><strong>Trade:</strong> not wired — prove edge + tradeability first</li>
      </ol>
    </div>

    <div class="rp-panel">
      <h3>Collector ↔ test matrix</h3>
      <table>
        <thead>
          <tr>
            <th>Collector</th>
            <th>Archive</th>
            <th>Tests that consume it</th>
            <th>Strategy</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>cross_venue_event_gap</code><br><small>collect_cross_venue_snapshot.py</small></td>
            <td><code>artifacts/cross_venue_snapshots/</code></td>
            <td>scan v1 · backtest v1</td>
            <td class="status-planned">Future</td>
          </tr>
          <tr>
            <td><code>options_horizon_surface</code><br><small>collect_horizon_surface_snapshot.py</small></td>
            <td><code>artifacts/horizon_surface_archive/</code></td>
            <td>horizon replay scrubber (needs ~30d)</td>
            <td class="status-planned">N/A</td>
          </tr>
          <tr>
            <td><code>implied_distribution_ts</code><br><small>collect_distribution_stats_snapshot.py</small></td>
            <td><code>artifacts/distribution_snapshots/</code></td>
            <td>dist timeseries charts (planned)</td>
            <td class="status-planned">N/A</td>
          </tr>
          <tr>
            <td><code>forward_consistency_ts</code><br><small>planned T3</small></td>
            <td><code>artifacts/forward_consistency/</code> (TBD)</td>
            <td>consistency radar + archive tests</td>
            <td class="status-planned">Future</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="note" style="margin-bottom: 24px">
      <strong>Mix-and-match rule:</strong> add a new test only when it declares which archive contract it reads.
      Add a new collector only with a charter (why · what · how often · who consumes).
      See registry § Research pipeline in <a href="../PPE_MODULE_REGISTRY_V1.md">PPE_MODULE_REGISTRY_V1.md</a>.
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
