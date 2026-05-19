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
