# PPE workflow cost accounting v1

**Plane:** CONTROL-PLANE · **Layer:** `dev-factory`

Track **attention and API cost** via worker-lane tags on closed slices. Advisory only — pairs with workflow radar and context closeout for burnout signals.

Cross-refs: [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

---

## Worker lanes

| Lane | When |
|------|------|
| `deterministic-local` | VM relay control / witness / closeout |
| `cursor-cli` | Headless Cursor CLI BUILD |
| `codex-cli` | Headless Codex CLI BUILD |
| `manual` | Desktop handoff / Cursor Agent |
| `acp` | ACP orchestrator slice |
| `local-agent` | Generic local agent CLI |

---

## Ledger

- **Path:** `artifacts/workflow_metrics/slices.jsonl` (gitignored)
- **Auto-record:** relay closeout (`post_relay_continue`), IDE mark ready (`mark_ide_product_ready`)
- **Dedup:** one row per `slice_id`

### Manual

```bat
workflow_metrics.cmd slice close --slice-id MySlice --size M --roundtrips 2 --worker-lane manual
workflow_metrics.cmd summary --days 7 --by-lane
```

### Weekly (Monday)

1. `workflow_metrics.cmd summary --days 7 --by-lane`
2. `workflow_radar.cmd generate` — includes lane line

---

## Burnout guardrails (advisory)

| Signal | Threshold | Response |
|--------|-----------|----------|
| Context closeouts / week | >=3, zero slices | Shorter threads; run relay between planning |
| Avg roundtrips / slice | >2.5 for 2 weeks | Thinner starters; split slices |
| Manual lane share | >60% | Check autobuilder happy path |

---

## Implementation

[`scripts/ppe_workflow_cost.py`](../../scripts/ppe_workflow_cost.py)
