# Multi-agent roadmap v1

**Plane:** CONTROL-PLANE · **Purpose:** persistence — insights, tiers, CBA, revisit checklist  
**Status as-of:** 2026-07-01

**Canon:** [`MULTI_AGENT_WORKER_INTERFACE_V1.md`](MULTI_AGENT_WORKER_INTERFACE_V1.md) · [`WORKER_LANE_POLICY_V1.md`](WORKER_LANE_POLICY_V1.md) · [`WORKER_REGISTRY_V1.json`](WORKER_REGISTRY_V1.json)

---

## Why this exists

PPE runs **Cursor + Codex + VM relay** on one repo. We built a thin **Agent Relay Control Plane (ARCP)** so agents do not fight over branches/paths. This doc captures **what we decided, what shipped, what we deferred, and when to revisit** — so future-you does not re-derive the same CBA from scratch.

---

## Mental model (one paragraph)

**PPE orchestrator** owns verdicts (`OPERATOR_STATUS`). **Cursor / Codex / VM** are **workers**, not stacked products. ARCP adds **leases** (who may edit which paths on which branch), **lanes** (which worker for which work), and **dispatch envelopes** (`WORK_DISPATCH.json`). Cost metrics nudge lane choice; they do not replace human/verdict SSOT.

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

## What shipped (operator cheatsheet)

| Action | Command / surface |
|--------|-------------------|
| Double-click BUILD | `DESKTOP_BUILD.cmd` → auto lane + lease + autobuilder handoff |
| Check lane / lease | `python scripts/ppe_worker_lease.py --assess` · `OPERATOR_STATUS.md` |
| Manual acquire | `ppe_worker_lease.py --acquire --worker codex-app --branch … --paths …` |
| Dispatch package | `ppe_worker_lease.py --write-dispatch` → `artifacts/control_plane/WORK_DISPATCH.json` |
| Ship lease paths | `ppe_worker_lease.py --ship --release` (gate → commit → push → PR) |
| Release only | `ppe_worker_lease.py --release` |

Artifacts (gitignored under `artifacts/`):

- `ACTIVE_LEASE.json` — exclusive lock
- `WORK_DISPATCH.json` — handoff envelope
- `WORKER_EVENTS.json` — synthetic progress (git/markers)
- `DESKTOP_BUILD_HANDOFF.json` — last BUILD lane decision

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

## Lane routing (quick reference)

| Situation | Preferred lane |
|-----------|----------------|
| Product slice / `src/**` | `cursor-desktop` |
| `control-plane/*` branch | `codex-app` (unless cost cap flips) |
| `CLOSEOUT_ONLY` / finish | `vm-relay` — **no** DESKTOP_BUILD lease |
| UX / charter threads | **no dispatch** (relay off) |

Full table: [`WORKER_LANE_POLICY_V1.md`](WORKER_LANE_POLICY_V1.md).

---

## Architecture snapshot

```
OPERATOR_STATUS (verdict SSOT)
    → BURST_PLAN (resolve_lease)
    → DESKTOP_BUILD.cmd
         → prepare_desktop_build_handoff()
         → ppe_autobuilder handoff
         → ppe_build_worker print-handoff (reads DESKTOP_BUILD_HANDOFF.json)
    → worker executes (Cursor or Codex)
    → run_pushable_gate.py
    → mark_ide_product_ready (auto-release lease)
    → DESKTOP_CONTINUE.cmd (VM finish)
```

---

## Cost–benefit (decision record)

**Worth it (shipped):** leases, lane docs, cost preference, DESKTOP_BUILD wiring, mark-ready auto-release.

**Skip for now:** Codex SDK sync, hard cost caps, OSS product, extra orchestration layers.

### Revisit Tier 3 when (any twice)

1. Codex + Cursor corrupted same files without a lease.
2. Stale lease blocked closeout repeatedly after mark-ready should have cleared it.
3. Publishing the lease pattern externally.
4. Unattended Codex cloud tasks become core workflow.

---

## Revisit checklist

When opening a thread tagged **multi-agent** or **ARCP**:

1. Read this doc + `OPERATOR_STATUS` worker lane line.
2. `python scripts/ppe_worker_lease.py --assess --json`
3. Check `artifacts/control_plane/DESKTOP_BUILD_HANDOFF.json` if BUILD felt wrong.
4. Scan Tier 3 triggers — if none, **stop building ARCP**.

---

## Sharing externally (optional)

Minimum extract without PPE VM stack:

1. [`WORKER_LANE_POLICY_V1.md`](WORKER_LANE_POLICY_V1.md)
2. [`templates/ACTIVE_LEASE.template.json`](templates/ACTIVE_LEASE.template.json)
3. [`templates/WORK_DISPATCH.template.json`](templates/WORK_DISPATCH.template.json)
4. `scripts/ppe_worker_lease.py` (trim ship/VM-specific helpers if forked)

Pitch: **multi-agent repo discipline** — leases + lanes, not another chat UI.

---

## Related PRs / chapters

- Initial ARCP: PR #1057 (`control-plane/multi-agent-leases-clean`)
- Auto-release on mark-ready: PR #1081
- DESKTOP_BUILD wiring: `control-plane/desktop-build-handoff-v1`

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-01 | Tier 1–2b shipped; Tier 3 deferred |
| 2026-07-01 | Tier 2c: auto-release on `mark_ide_product_ready` |
| 2026-07-01 | Tier 2b: `DESKTOP_BUILD.cmd` + `prepare_desktop_build_handoff` |
