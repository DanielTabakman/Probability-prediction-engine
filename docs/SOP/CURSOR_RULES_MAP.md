# Cursor rules map v1

**Plane:** CONTROL-PLANE  
**Purpose:** Which Cursor rules load when — reduces duplicate instructions for agents.

**Division canon:** [`AI_HUMAN_DIVISION_V1.md`](AI_HUMAN_DIVISION_V1.md)

---

## Always applied (workspace)

| Rule | Role |
|------|------|
| [`ppe-core-agent.mdc`](../../.cursor/rules/ppe-core-agent.mdc) | Verdict auto-run, layers, commit policy, AI/human split pointer |
| [`ppe-desktop-vm-layout.mdc`](../../.cursor/rules/ppe-desktop-vm-layout.mdc) | Desktop vs VM relay guard |
| [`product-direction.mdc`](../../.cursor/rules/product-direction.mdc) | Direction pivot SSOT |
| [`auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc) | Gate + commit + PR |

Legacy rules (`agent-continuity.mdc`, `ppe-unified-run.mdc`, `repo-layers.mdc`) remain for compatibility; **`ppe-core-agent.mdc` is the merged summary** — prefer it for new threads.

---

## On demand (agent_requestable)

| Rule | When to load |
|------|----------------|
| [`context-budget.mdc`](../../.cursor/rules/context-budget.mdc) | Before large BUILD; WATCH/ESCALATE bands |
| [`product-focus.mdc`](../../.cursor/rules/product-focus.mdc) | SELECTION, scope fights |
| [`context-window-closeout.mdc`](../../.cursor/rules/context-window-closeout.mdc) | Thread closeout triggers |

---

## Subagents (`.cursor/agents/`)

| Agent | Role |
|-------|------|
| `ppe-director` | Operator routing |
| `ppe-build-worker` | IDE BUILD slice |
| `ppe-finish-worker` | RUN_LOCAL finish |
| `ppe-triage-worker` | ERROR / FIX_PLAN |

---

## BUILD minimal load (prefer over all rules)

1. `python scripts/ppe_context_preflight.py --phase-plan … --slice-id …`
2. [`agent_index/`](agent_index/) for layer
3. `IDE_BUILD_STARTER_*.md`

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-27 | v1 — rules map + ppe-core-agent consolidation pointer |
