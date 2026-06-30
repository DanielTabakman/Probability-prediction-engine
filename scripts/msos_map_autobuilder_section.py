"""Inject autobuilder reference section into msos_module_map.html (idempotent)."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "docs" / "SOP" / "assets" / "msos_module_map.html"
MARKER = 'id="autobuilder"'

AUTOBUILDER_CSS = """
      .ab-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
        max-width: 52rem;
        margin-bottom: 16px;
      }
      .ab-machine {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 12px 14px;
      }
      .ab-machine.vm { border-left: 3px solid var(--violet); }
      .ab-machine.desktop { border-left: 3px solid var(--teal); }
      .ab-machine.phone { border-left: 3px solid var(--amber); }
      .ab-machine h3 { margin: 0 0 6px; font-size: 0.88rem; }
      .ab-machine p, .ab-machine ul { margin: 0; font-size: 0.78rem; color: var(--muted); }
      .ab-machine ul { padding-left: 1.1rem; margin-top: 6px; }
      .ab-machine li { margin-bottom: 4px; }
      .ab-machine code { font-size: 0.7rem; }
      .ab-flow {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 14px 16px;
        max-width: 52rem;
        margin-bottom: 16px;
        overflow-x: auto;
      }
      .ab-flow pre {
        margin: 0;
        font-family: ui-monospace, "Cascadia Code", monospace;
        font-size: 0.74rem;
        line-height: 1.55;
        color: var(--muted);
      }
      .ab-flow .hl-vm { color: var(--violet); }
      .ab-flow .hl-dt { color: var(--teal); }
      .ab-flow .hl-ph { color: var(--amber); font-weight: 600; }
      .ab-panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 14px;
        max-width: 52rem;
        margin-bottom: 16px;
        overflow-x: auto;
      }
      .ab-panel h3 { margin: 0 0 10px; font-size: 0.82rem; color: var(--muted); font-weight: 700; }
      .ab-agents {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        max-width: 52rem;
        margin-bottom: 8px;
      }
      .ab-agent {
        background: var(--panel2);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 0.78rem;
      }
      .ab-agent strong { display: block; color: var(--teal); font-size: 0.72rem; margin-bottom: 4px; }
      .ab-agent span { color: var(--muted); }
      .phase-tag {
        display: inline-block;
        font-family: ui-monospace, monospace;
        font-size: 0.68rem;
        padding: 1px 5px;
        border-radius: 4px;
        background: rgba(167,139,250,0.12);
        color: var(--violet);
      }
      .phase-tag.idle { background: rgba(110,231,168,0.12); color: var(--green); }
      .phase-tag.wait { background: rgba(242,182,87,0.12); color: var(--amber); }
      .phase-tag.err { background: rgba(255,100,120,0.12); color: var(--red); }
"""

AUTOBUILDER_SECTION = """
    <h2 id="autobuilder">Autobuilder — how the factory runs</h2>
    <p class="flow-desc">
      The autobuilder is the control-plane pipeline: VM relay loop, IDE BUILD dispatch, closeout, and ntfy.
      Canon: <a href="../PPE_AUTOBUILDER_V1.md">PPE_AUTOBUILDER_V1.md</a>
      · <a href="../OPERATOR_BUTTON_MAP.md">Button map</a>
      · <a href="../PPE_OPERATOR_LAYOUT_ADR.md">VM + desktop layout ADR</a>
      · Entry: <code>ppe_autobuilder.cmd</code> · Agent: <code>@ppe-autobuilder-operator</code>
    </p>

    <div class="ab-grid">
      <div class="ab-machine vm">
        <h3>Hyper-V VM (loop host)</h3>
        <p>24/7 headless stack — relay, guards, ntfy watch. Never IDE BUILD product code here.</p>
        <ul>
          <li><code>run_ppe_auto_local_loop.cmd</code> — relay slices</li>
          <li><code>watch_operator_mobile.cmd</code> — ntfy + auto-dispatch</li>
          <li><code>ppe_autobuilder.cmd advance</code> — fix stuck phase</li>
          <li><code>VM_RESTART.cmd</code> when <span class="phase-tag err">STACK_DOWN</span></li>
        </ul>
      </div>
      <div class="ab-machine desktop">
        <h3>Daily desktop (IDE BUILD)</h3>
        <p>Cursor / Codex only when verdict is <code>IDE_BUILD</code>. No loop, no <code>run_ppe_local</code>.</p>
        <ul>
          <li><code>DESKTOP_BUILD.cmd</code> → clipboard prompt → Agent</li>
          <li>Gate → commit → PR → merge</li>
          <li><code>DESKTOP_CONTINUE.cmd</code> → SSH finish on VM</li>
        </ul>
      </div>
      <div class="ab-machine phone">
        <h3>Phone (optional)</h3>
        <p>ntfy alerts + SSH triage — not required when auto-dispatch is on.</p>
        <ul>
          <li>ntfy: <code>build</code> / <code>fix</code> / <code>status</code></li>
          <li>SSH: <code>VM_RESTART.cmd</code>, <code>fix_vm_operator.cmd</code></li>
        </ul>
      </div>
    </div>

    <div class="ab-flow">
      <pre>
<span class="hl-vm">VM loop</span> polls verdict ──► <span class="hl-ph">RUN_AUTO</span> ──► control slice (relay advances on main)
                         │
                         ├──► <span class="hl-ph">SUPPLY_LOW</span> ──► idle (queue empty — charter more work)
                         │
                         ├──► <span class="hl-ph">IDE_BUILD</span> ──► dispatch ──► <span class="hl-dt">DESKTOP BUILD</span> (Cursor/Codex implements product)
                         │                                    │
                         │                                    ▼ gate · commit · PR · merge
                         │                              <span class="hl-dt">DESKTOP CONTINUE</span> (SSH finish)
                         │                                    │
                         │                                    ▼ mark_ide_product_ready
                         └──► <span class="hl-ph">RUN_LOCAL</span> ◄────────────────┘
                                   │
                                   ▼ run_ppe_local (closeout chapter on VM)
                                   └──► back to <span class="hl-ph">RUN_AUTO</span>
      </pre>
    </div>

    <div class="ab-panel">
      <h3>Autobuilder phases (machine snapshot)</h3>
      <table>
        <thead>
          <tr>
            <th>Phase</th>
            <th>Meaning</th>
            <th>Typical fix</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><span class="phase-tag err">STACK_DOWN</span></td>
            <td>Loop or watch not running</td>
            <td><code>ppe_autobuilder.cmd ensure</code> or <code>VM_RESTART.cmd</code></td>
          </tr>
          <tr>
            <td><span class="phase-tag idle">HEALTHY_IDLE</span></td>
            <td><code>RUN_AUTO</code> / <code>SUPPLY_LOW</code>, stack OK</td>
            <td>None — loop is working</td>
          </tr>
          <tr>
            <td><span class="phase-tag wait">AWAITING_BUILD</span></td>
            <td>Product slice needs IDE BUILD</td>
            <td><code>DESKTOP_BUILD.cmd</code> or <code>ppe_autobuilder.cmd advance</code></td>
          </tr>
          <tr>
            <td><span class="phase-tag wait">BUILD_IN_FLIGHT</span></td>
            <td>Remote build lock active</td>
            <td>Wait for agent to finish</td>
          </tr>
          <tr>
            <td><span class="phase-tag wait">CLOSEOUT_PENDING</span></td>
            <td>Commits on branch, no ready marker</td>
            <td><code>ppe_autobuilder.cmd finish-pending</code></td>
          </tr>
          <tr>
            <td><span class="phase-tag wait">RUN_LOCAL_PENDING</span></td>
            <td>Marker present, relay not advanced</td>
            <td><code>DESKTOP_CONTINUE.cmd</code> or <code>run-local</code> on VM</td>
          </tr>
          <tr>
            <td><span class="phase-tag err">FIX_PLAN</span> / <span class="phase-tag err">ERROR</span></td>
            <td>Relay or plan blocker</td>
            <td><code>@ppe-triage-worker</code> · <code>ppe_autobuilder.cmd diagnose</code></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="ab-panel">
      <h3>Verdict → what you do (by machine)</h3>
      <table>
        <thead>
          <tr>
            <th>Verdict</th>
            <th>Desktop</th>
            <th>VM loop</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>IDE_BUILD</code></td>
            <td><strong>DESKTOP BUILD</strong> → Agent → gate → PR</td>
            <td>Waits (or auto-dispatches to desktop)</td>
          </tr>
          <tr>
            <td><code>RUN_LOCAL</code></td>
            <td><strong>DESKTOP CONTINUE</strong> after merge</td>
            <td><code>run_ppe_local.cmd</code> (closeout)</td>
          </tr>
          <tr>
            <td><code>RUN_AUTO</code></td>
            <td>Nothing — do not run relay locally</td>
            <td>Loop advances automatically</td>
          </tr>
          <tr>
            <td><code>SUPPLY_LOW</code></td>
            <td>Charter / queue work on main</td>
            <td>Idle until supply returns</td>
          </tr>
          <tr>
            <td><code>ERROR</code> / <code>STALE_STATE</code></td>
            <td>Steward triage in Cursor</td>
            <td><code>fix_vm_operator.cmd</code></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="ab-agents">
      <div class="ab-agent">
        <strong>@ppe-autobuilder-operator</strong>
        <span>Pipeline health, dispatch, closeout recovery — not product code</span>
      </div>
      <div class="ab-agent">
        <strong>@ppe-build-worker</strong>
        <span>One product slice — loads <code>IDE_BUILD_STARTER_*.md</code></span>
      </div>
      <div class="ab-agent">
        <strong>@ppe-finish-worker</strong>
        <span><code>RUN_LOCAL</code> only — <code>run_ppe_local</code> closeout</span>
      </div>
      <div class="ab-agent">
        <strong>@ppe-director</strong>
        <span>Burst mode — routes verdicts to workers via <code>ppe_go.cmd</code></span>
      </div>
      <div class="ab-agent">
        <strong>@ppe-triage-worker</strong>
        <span><code>FIX_PLAN</code> / <code>ERROR</code> diagnosis</span>
      </div>
    </div>

    <div class="note" style="margin-bottom: 24px">
      <strong>Status artifacts:</strong>
      <code>CONTROL_PLANE_STATUS.json</code> (human read — <code>ppe_autobuilder.cmd reconcile</code>)
      · <code>AUTOBUILDER_STATUS.json</code> (machine phase)
      · <code>OPERATOR_STATUS.md</code> (verdict summary)
      · <code>IDE_PRODUCT_READY.json</code> (build-complete marker for guards)
    </div>
"""

EXTRA_SECTIONS = """
    <h2 id="burst-mode">Burst mode — adaptive director</h2>
    <p class="flow-desc">
      Default for <code>what's next?</code> — preflight sizes work, then <code>@ppe-director</code> spawns workers until band cap or stop.
      Canon: <a href="../WORKFLOW_EFFICIENCY_OPERATOR_V1.md">workflow efficiency</a>
      · Entry: <code>ppe_go.cmd</code> (burst) · <code>ppe_go.cmd --single</code> (one-shot)
    </p>

    <div class="ab-flow">
      <pre>
<span class="hl-ph">what's next?</span> ──► <span class="hl-dt">ppe_burst_plan.py --write</span> ──► BURST_PLAN.json
                         │
                         ├── burst_allowed=false ──► single verdict only (split slice first)
                         │
                         └── use_director=true ──► <span class="hl-dt">@ppe-director</span>
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            IDE_BUILD         RUN_LOCAL      FIX_PLAN/ERROR
         build-worker      finish-worker    triage-worker (max 1)
                    │               │               │
                    └───────────────┴───────────────┘
                                    ▼
                         re-read OPERATOR_STATUS · re-plan if cycles remain
                                    ▼
                         stop: cap · RUN_AUTO · stuck · WATCH band · guard block
      </pre>
    </div>

    <div class="ab-panel">
      <h3>BURST_PLAN.json — key fields</h3>
      <table>
        <thead>
          <tr><th>Field</th><th>Meaning</th></tr>
        </thead>
        <tbody>
          <tr><td><code>max_cycles</code></td><td>Workers this burst — NORMAL→3, WATCH→1, ESCALATE→0</td></tr>
          <tr><td><code>use_director</code></td><td><strong>true</strong> for IDE_BUILD / RUN_LOCAL — steward thread must not implement product</td></tr>
          <tr><td><code>burst_allowed</code></td><td><strong>false</strong> → one verdict only; trim spec or split slice</td></tr>
          <tr><td><code>overall_band</code></td><td>NORMAL / WATCH / ESCALATE from context audit</td></tr>
        </tbody>
      </table>
    </div>

    <div class="note" style="margin-bottom: 24px">
      <strong>Forbidden in burst:</strong> implementing <code>IDE_BUILD</code> in the steward thread ·
      <code>run_ppe_auto_local_loop</code> on desktop · pasting full sprint specs.
      After stop: <code>context_window_closeout.cmd --record</code> → fresh thread.
    </div>

    <h2 id="asset-batch">Asset batch enablement</h2>
    <p class="flow-desc">
      One operator phrase → agent runs a manifest chunk end-to-end (discover, witness, enable, gate, PR).
      Canon: <a href="../ASSET_BATCH_EXPANSION_POLICY_V1.md">ASSET_BATCH_EXPANSION_POLICY_V1.md</a>
      · Manifest: <code>config/assets_tier1_manifest.yaml</code>
    </p>

    <div class="ab-panel">
      <h3>Operator triggers</h3>
      <table>
        <thead>
          <tr><th>Say this</th><th>Wave</th><th>Agent does</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><code>asset batch wave 1</code> / <code>finish tier-1</code></td>
            <td>Tier-1 (~25–30)</td>
            <td>Next uncomplete manifest chapter · 3–5 ids · one chunk per thread</td>
          </tr>
          <tr>
            <td><code>asset batch wave 2</code> / <code>tier-2 batch</code></td>
            <td>Tier-2 (~100)</td>
            <td>Next tier-2 chunk (10 ids) after tier-1 closeout</td>
          </tr>
          <tr>
            <td><code>asset batch wave N until blocked</code></td>
            <td>Any</td>
            <td>Consecutive chunks until witness/gate/prerequisite fail</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="ab-flow">
      <pre>
Pick chunk ──► <span class="hl-dt">discover_asset_data_source.py --asset ID --json</span> (each id)
            │     execute next_action — never ask operator which exchange
            ▼
Witness ──► probe_asset_data_source · witness_asset_catalog --live
            ▼
Enable ──► enable_asset_batch.py --apply --live-witness
            ▼
Gate ──► run_pushable_gate.py · commit · PR
            ▼
Ops ──► warm_display_payload_cache · prod multi-asset witness when ready
            ▼
Close chunk ──► manifest status complete · evidence doc · trust sign-off for Live pill
      </pre>
    </div>

    <div class="ab-panel">
      <h3>Discovery next_action → agent</h3>
      <table>
        <thead>
          <tr><th>next_action</th><th>Agent</th></tr>
        </thead>
        <tbody>
          <tr><td><code>enable_existing_row</code></td><td>Witness + enable</td></tr>
          <tr><td><code>merge_registry_and_enable</code></td><td>Merge manifest row + venue from discovery</td></tr>
          <tr><td><code>switch_venue_and_enable</code></td><td>Fix venue (e.g. deribit → bybit)</td></tr>
          <tr><td><code>build_adapter</code></td><td>Implement adapter slice first</td></tr>
          <tr><td><code>blocked_no_live_options</code></td><td>Log skip — <strong>do not enable</strong></td></tr>
          <tr><td><code>already_enabled</code></td><td>Skip · optional prod witness</td></tr>
        </tbody>
      </table>
    </div>

    <h2 id="closeout-lifecycle">Chapter closeout lifecycle</h2>
    <p class="flow-desc">
      Product BUILD and chapter closeout are separate steps. <code>run_ppe_local</code> does <strong>not</strong> implement product code — it advances relay and runs control closeout.
      Canon: <a href="../RELAY_ORCHESTRATOR_RUNBOOK_V1.md">relay runbook</a>
      · <a href="../PPE_IDE_NATIVE_OPERATOR_V1.md">IDE native operator</a>
    </p>

    <div class="ab-flow">
      <pre>
<span class="hl-ph">IDE_BUILD</span> slice ──► Agent implements product · gate · commit · PR · merge
                │
                ▼ <span class="hl-dt">mark_ide_product_ready</span> (IDE_PRODUCT_READY.json marker)
                │
                ▼ verdict becomes <span class="hl-ph">RUN_LOCAL</span>
                │
    Desktop ──► <span class="hl-dt">DESKTOP_CONTINUE.cmd</span> (SSH finish on VM)
    VM ───────► <span class="hl-dt">run_ppe_local.cmd</span>
                │
                ▼ relay slice: control closeout + propagate queue
                │
                ▼ <span class="hl-dt">apply_control_closeout_v1</span>
                   updates MVP1_FRONTIER · HANDOFF · PPE_INTEGRATED_STATUS · AGENT_CONTINUITY_BRIEF
                │
                ▼ verdict returns to <span class="hl-ph">RUN_AUTO</span> (next slice)
      </pre>
    </div>

    <div class="ab-panel">
      <h3>Who runs what</h3>
      <table>
        <thead>
          <tr><th>Step</th><th>Machine</th><th>Script / agent</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>Implement product slice</td>
            <td>Desktop</td>
            <td><code>DESKTOP_BUILD.cmd</code> → <code>@ppe-build-worker</code></td>
          </tr>
          <tr>
            <td>Mark build complete</td>
            <td>Desktop (agent) or VM watcher</td>
            <td><code>mark_ide_product_ready.cmd</code> · <code>finish_ide_build.cmd</code></td>
          </tr>
          <tr>
            <td>Advance relay closeout</td>
            <td><strong>VM only</strong></td>
            <td><code>run_ppe_local.cmd</code> · <code>@ppe-finish-worker</code></td>
          </tr>
          <tr>
            <td>Desktop handoff after merge</td>
            <td>Desktop</td>
            <td><code>DESKTOP_CONTINUE.cmd</code> — not the same as <code>run_ppe_local</code></td>
          </tr>
          <tr>
            <td>Context window end (chat)</td>
            <td>Either</td>
            <td><code>context_window_closeout.cmd</code> — <em>not</em> chapter closeout</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="note" style="margin-bottom: 24px">
      <strong>Chapter not closed until:</strong> <code>apply_control_closeout_v1</code> PASS,
      steering alignment green, evidence doc updated, and changes on <code>main</code>.
      Post-build watcher auto-runs mark + <code>run_ppe_local</code> when agent stops after commit.
    </div>
"""

MARKER_BURST = 'id="burst-mode"'
MARKER_ASSET = 'id="asset-batch"'
MARKER_CLOSEOUT = 'id="closeout-lifecycle"'


def inject(html: str) -> str:
    if MARKER not in html:
        html = html.replace(
            "    <h2>MSOS pillars</h2>",
            AUTOBUILDER_SECTION + EXTRA_SECTIONS + "\n    <h2>MSOS pillars</h2>",
            1,
        )
    elif MARKER_BURST not in html:
        html = html.replace(
            "    <h2>MSOS pillars</h2>",
            EXTRA_SECTIONS + "\n    <h2>MSOS pillars</h2>",
            1,
        )
    if ".ab-grid {" not in html:
        html = html.replace(
            "      .status-partial { color: var(--amber); font-weight: 600; }\n    </style>",
            "      .status-partial { color: var(--amber); font-weight: 600; }" + AUTOBUILDER_CSS + "    </style>",
            1,
        )
    html = html.replace(
        "Living operator chart — modules, data, tiers, priorities.",
        "Living operator chart — modules, data, tiers, priorities, and operator factory.",
    )
    html = html.replace(
        "Living operator chart — modules, data, tiers, priorities, and autobuilder pipeline.",
        "Living operator chart — modules, data, tiers, priorities, and operator factory.",
    )
    if 'href="#autobuilder"' not in html:
        html = re.sub(
            r'(Operator status</a>\n)(        · <a href="../HUMAN_STEWARD_BACKLOG.md">)',
            r'\1        · <a href="#autobuilder">Autobuilder</a>\n\2',
            html,
            count=1,
        )
    if 'href="#burst-mode"' not in html and 'href="#autobuilder"' in html:
        html = html.replace(
            '        · <a href="#autobuilder">Autobuilder</a>\n',
            '        · <a href="#autobuilder">Autobuilder</a>\n'
            '        · <a href="#burst-mode">Burst</a>\n'
            '        · <a href="#asset-batch">Assets</a>\n'
            '        · <a href="#closeout-lifecycle">Closeout</a>\n',
            1,
        )
    return html


def main() -> int:
    html = MAP.read_text(encoding="utf-8")
    html = inject(html)
    MAP.write_text(html, encoding="utf-8")
    for marker in (MARKER, MARKER_BURST, MARKER_ASSET, MARKER_CLOSEOUT):
        if marker not in html:
            raise SystemExit(f"inject failed: missing {marker}")
    print(f"injected operator reference sections into {MAP.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
