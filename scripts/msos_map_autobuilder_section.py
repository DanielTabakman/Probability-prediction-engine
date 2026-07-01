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
          <li><code>DESKTOP_BUILD.cmd</code> → starter + IDE_BUILD_NOW.md → Agent</li>
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


def inject(html: str) -> str:
    if MARKER not in html:
        html = html.replace(
            "    <h2>MSOS pillars</h2>",
            AUTOBUILDER_SECTION + "\n    <h2>MSOS pillars</h2>",
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
        "Living operator chart — modules, data, tiers, priorities, and autobuilder pipeline.",
    )
    if 'href="#autobuilder"' not in html:
        html = re.sub(
            r'(Operator status</a>\n)(        · <a href="../HUMAN_STEWARD_BACKLOG.md">)',
            r'\1        · <a href="#autobuilder">Autobuilder</a>\n\2',
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
    print(f"injected autobuilder section into {MAP.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
