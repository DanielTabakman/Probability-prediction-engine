# Multi-agent roadmap v1

**Plane:** CONTROL-PLANE · **Purpose:** persistence — insights, tiers, CBA, revisit checklist  
**Canon:** [`MULTI_AGENT_WORKER_INTERFACE_V1.md`](MULTI_AGENT_WORKER_INTERFACE_V1.md) · [`WORKER_LANE_POLICY_V1.md`](WORKER_LANE_POLICY_V1.md)

---

## Tier status

| Tier | Scope | Status |
|------|--------|--------|
| **Tier 1** | Leases, lane policy, `ppe_worker_lease.py`, burst `resolve_lease` | **Shipped** |
| **Tier 2a** | `prefer_build_lane`, `WORKER_EVENTS.json` | **Shipped** |
| **Tier 2b** | `DESKTOP_BUILD` auto-acquire + dispatch | **Shipped** |
| **Tier 2c** | Auto-release lease on `mark_ide_product_ready` | **Shipped** |
| **Tier 3** | Codex SDK, hard cost caps, OSS extract, ARCP UI | **Deferred** |

---

## Lifecycle (closed loop)

```
DESKTOP_BUILD → acquire lease + WORK_DISPATCH
    → Cursor or Codex BUILD
    → run_pushable_gate.py
    → mark_ide_product_ready  → auto-release lease (slice + branch match)
    → DESKTOP_CONTINUE (VM finish)
```

Manual fallback: `python scripts/ppe_worker_lease.py --ship --release` if you shipped without mark-ready.

---

## Revisit Tier 3 when (any twice)

1. Codex + Cursor corrupted same files without a lease.
2. Stale lease blocked closeout repeatedly after mark-ready should have cleared it.
3. Publishing the lease pattern externally.
4. Unattended Codex cloud tasks become core workflow.

---

## Cost–benefit (decision record)

**Worth it (shipped):** leases, lane docs, cost preference, DESKTOP_BUILD wiring, mark-ready auto-release.

**Skip for now:** Codex SDK sync, hard cost caps, OSS product, extra orchestration layers.

---

## Revisit checklist

1. Read this doc + `OPERATOR_STATUS` worker lane line.
2. `python scripts/ppe_worker_lease.py --assess --json`
3. Check `artifacts/control_plane/DESKTOP_BUILD_HANDOFF.json` if BUILD felt wrong.
4. Scan Tier 3 triggers — if none, **stop building ARCP**.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-01 | Tier 1–2b shipped; Tier 3 deferred |
| 2026-07-01 | Tier 2c: auto-release on `mark_ide_product_ready` |
