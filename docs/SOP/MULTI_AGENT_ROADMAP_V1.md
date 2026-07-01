# Multi-agent roadmap v1

**Plane:** CONTROL-PLANE · **Purpose:** persistence doc — insights, tiers, CBA, revisit checklist  
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
| **Tier 1** | Lease schema, lane policy, `ppe_worker_lease.py`, burst `resolve_lease`, status lines | **Shipped** |
| **Tier 2a** | `prefer_build_lane` (branch + 7d cost + USD est), `WORKER_EVENTS.json` inference | **Shipped** |
| **Tier 2b** | `DESKTOP_BUILD` → auto-acquire + dispatch; handoff reads `DESKTOP_BUILD_HANDOFF.json` | **Shipped** (this slice) |
| **Tier 3** | Codex SDK sync, hard cost caps, OSS extract, ARCP product UI | **Deferred** |

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

## Cost–benefit (2026-07 decision record)

### Done — worth it

| Item | Benefit | Cost paid |
|------|---------|-----------|
| Leases + `resolve_lease` | Prevents Codex/Cursor branch/path fights | Small CLI + status noise |
| Lane policy doc | Shareable grammar; agents know who owns what | One SOP to maintain |
| Cost-aware `prefer_build_lane` | Suggests cheaper worker on control-plane | Tuning in one function |
| Synthetic events | Audit without Codex API | Inference gaps on app-only flows |
| `DESKTOP_BUILD` integration | No manual `--acquire` before each BUILD | ~1 cmd + handoff path |

### Deferred — negative ROI for solo PPE (for now)

| Item | Why skip |
|------|----------|
| **Codex SDK / app event sync** | High fragility; git + gate + markers cover ~90% |
| **Hard cost caps** (block expensive lane) | Soft preference enough; risk wrong agent for UI/product |
| **OSS repo extract** | Only if publishing; templates + lane doc are 80% of share value |
| **ARCP product UI** | PPE is the reference impl, not a startup |

### Revisit Tier 3 when (any twice)

1. Codex + Cursor corrupted the same files **without** a lease in play.
2. You forgot acquire/release and `resolve_lease` blocked closeout repeatedly.
3. You want to **publish** the lease pattern externally.
4. Unattended **Codex cloud tasks** become core workflow (SDK sync becomes worth it).

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
    → ppe_worker_lease.py --ship --release  (optional)
    → DESKTOP_CONTINUE.cmd (VM finish)
```

---

## Future revisit checklist

When opening a thread tagged **multi-agent** or **ARCP**:

1. Read this doc + `OPERATOR_STATUS` worker lane line.
2. `python scripts/ppe_worker_lease.py --assess --json`
3. Check `artifacts/control_plane/DESKTOP_BUILD_HANDOFF.json` if BUILD felt wrong.
4. Scan Tier 3 triggers above — if none, **do not** add orchestration layers.
5. If implementing Tier 3 item, update **Tier status** table in this doc.

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
- DESKTOP_BUILD wiring: same control-plane series

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-01 | Tier 1+2a shipped; CBA recorded; Tier 3 deferred |
| 2026-07-01 | Tier 2b: `DESKTOP_BUILD.cmd` + `prepare_desktop_build_handoff` |
