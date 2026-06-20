# Context Rules

## First-principles rule
Create a new context when the optimization target changes.

Do NOT create a new context for every tiny action.

## Use a new Cursor thread when:
- moving from bug fix -> feature work
- moving from feature work -> refactor
- moving from UI/layout -> quant logic
- moving from implementation -> planning
- the old thread has stale assumptions
- the old thread keeps proposing ruled-out ideas

## Stay in the same Cursor thread when:
- still in the same sprint
- fixing a direct bug from that sprint
- doing acceptance fixes for that sprint
- constraints and goal are unchanged

## Relay / run_ppe.cmd

- **`run_ppe.cmd`** runs a full phase via orchestrator; each **slice** gets a **fresh ACP worker** (not your Cursor chat history).
- **Steward thread:** SELECTION, manifest, read `LAST_RUN_REPORT.md` — keep separate from BUILD.
- **After phase exit:** new Cursor thread; load only `docs/SOP/AGENT_CONTINUITY_BRIEF.md`.

## Conversation mode (META vs EXECUTE)

Agents classify each turn — see [`.cursor/rules/conversation-mode.mdc`](../.cursor/rules/conversation-mode.mdc).

| Mode | When | Operator loop |
|------|------|----------------|
| **META** | Pipeline, orchestrator, rules, process design | Do not auto-run verdict |
| **EXECUTE** | Ship slice, what's next, IDE BUILD | Auto-run per `ppe-unified-run.mdc` |

**Override anytime:** say `meta` or `execute` (one word). Agent states **Mode: …** at the top of replies; correct if wrong.

## Operator layout (2026-06)

**Policy:** [`docs/SOP/PPE_OPERATOR_LAYOUT_ADR.md`](SOP/PPE_OPERATOR_LAYOUT_ADR.md) · **Process:** [`docs/SOP/PPE_OPERATOR_PROCESS_V1.md`](SOP/PPE_OPERATOR_PROCESS_V1.md)

- **VM** runs the 24/7 loop; **desktop** runs IDE BUILD only.
- New operator threads: load [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](SOP/PPE_VM_DESKTOP_OPERATOR_HANDOFF.md) + continuity brief — not laptop chat history.

## Good thread unit
One thread per sprint or sub-sprint.

Examples:
- Sprint 1A — state ownership
- Sprint 1B — layout
- Sprint 1C — scope compression
- Sprint 2A — user belief overlay
- Sprint 2A.1 — belief summary polish

## New chat with ChatGPT when:
- the role changes substantially
- the optimization target changes substantially
- you want a fresh high-level planning conversation
- the current chat has become cognitively noisy

## Stay in the same chat with ChatGPT when:
- still on the same product arc
- continuity of tradeoffs matters
- current sprint depends on earlier architectural decisions

## Safety rule
If unsure whether to open a new context, ask:
“What are we optimizing for right now?”
If the answer changed, start a new context.

## Ending a context (closeout)

Before retiring a long or noisy thread, run **context window closeout** — not the same as relay chapter closeout.

1. `python scripts/ppe_context_window_closeout.py --render`
2. Complete the draft at `artifacts/control_plane/CONTEXT_WINDOW_CLOSEOUT_DRAFT.md`
3. Ship small items, push branches, triage the rest into build vs human backlog

Full ritual: [`docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md`](SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md)

**Trigger phrases:** `close out thread` · `closeout thread` · `context closeout` · `wrap this chat` (see SOP for full list)

**Next thread after closeout:** ask **what's next?** in **EXECUTE** mode — agent auto-runs the operator verdict. META threads skip auto-run unless you switch mode. See `.cursor/rules/conversation-mode.mdc`.
