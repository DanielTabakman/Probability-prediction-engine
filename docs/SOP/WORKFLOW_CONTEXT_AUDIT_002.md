# Workflow Context Audit 002 — token economy monitor

**Status:** canonical. **Plane:** CONTROL-PLANE.  
**Cross-refs:** [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) · [`PPE_TOKEN_ECONOMY_MONITOR_V1.md`](PPE_TOKEN_ECONOMY_MONITOR_V1.md)

## Finding

Cursor token burn was dominated by (1) six always-on rules ~4.7k tok/turn, (2) fat IDE starters ~150+ lines with duplicated context, (3) no automated monitoring loop.

## Shipped

- Minimal starter generator (touchSet-first, ≤65/80 line budgets)
- `ppe-operator-core.mdc` + demoted load-on-demand rules
- `token_audit.cmd` + `token_economy_history.jsonl` trend log
- Weekly Monday pipeline integration + workflow radar token section
- `regenerate_ide_starters.cmd` for bulk refresh

## Perpetual monitor

See [`PPE_TOKEN_ECONOMY_MONITOR_V1.md`](PPE_TOKEN_ECONOMY_MONITOR_V1.md) for schedule, verdicts, and agent ownership.
