# Delegation envelope v1

**Plane:** CONTROL-PLANE · **SSOT:** [`DELEGATION_ENVELOPE_V1.json`](DELEGATION_ENVELOPE_V1.json)

**Decision (2026-06-30):** **Balanced smart delegation** — agents and control-plane own routine shipping; operator only for pivots, secrets, billing, and production access.

---

## Tiers

| Tier | Meaning |
|------|---------|
| **auto** | Gate pass → commit → push → PR per [`COMMIT_POLICY.md`](COMMIT_POLICY.md). No ask. |
| **auto_notify** | Same as auto; mention in digest/ntfy when configured. |
| **steward_packet** | Agent drafts decision in [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) — no steering merge until ack. |
| **human_only** | Stop; operator must explicitly authorize. |

---

## Smart behavior

1. **Path rules** — each changed file matched to a tier (most restrictive wins).
2. **Escalators** — mixed-plane → steward_packet (unless `RECOVERY` pass); 25+ files → auto_notify; force-push → human_only; direct `main` → steward_packet.
3. **Gate integration** — `run_pushable_gate.py` blocks only on **human_only** (override: `PPE_DELEGATION_OVERRIDE=1` for recovery).

---

## Commands

```bat
ppe_delegation_envelope.cmd
ppe_delegation_envelope.cmd --json docs/SOP/PHASE_QUEUE.json
ppe_delegation_envelope.cmd --gate-check
ppe_delegation_envelope.cmd --pass-type RECOVERY
```

---

## Delegated (auto) — agents own these

- Queue/backlog hygiene (`PHASE_QUEUE`, `TRIGGERED_IDEAS`, `UX_EXECUTION_BACKLOG`)
- Evidence closeout docs after witness
- Layer registry path additions for new tests
- Chartered product slices after gate
- VM recovery (stash + reset) — **auto_notify**
- Context window closeout auto-ship

## Steward packet — draft first

- `docs/VISION/PPE_MASTER*` edits (strategic canon)
- Mixed-plane diffs outside RECOVERY
- Direct commits to `main`

## Human only — never auto

- Secrets / `.env` / credentials
- `ACTIVE_PRODUCT_DIRECTION.json` pivot fields (`pivotId`, `northStar`, `primaryFocus`, `currentStage`) — other field syncs are **auto**
- Stripe / billing chapters
- Production Access / deploy runbooks (policy changes)

---

## Related

- [`FOUNDER_COLLABORATION_CHARTER_V1.md`](FOUNDER_COLLABORATION_CHARTER_V1.md) — founder decision defaults vs agent technical defaults
- [`OPERATING_RULES.md`](OPERATING_RULES.md) — plane discipline
- [`COMMIT_POLICY.md`](COMMIT_POLICY.md) — auto-ship path
- [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — standing queue delegation (envelope narrows hard stops)
