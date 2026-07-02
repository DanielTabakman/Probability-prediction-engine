# Pipeline health v1 — founder diagnostics

**Plane:** CONTROL-PLANE · **Audience:** founder, operator agents  
**Purpose:** One glance at **root cause**, **fix class**, and **milestone slip** — avoid a day of runaround.

**Related:** [`CHAPTER_COORDINATION_V1.md`](CHAPTER_COORDINATION_V1.md) · [`FACTORY_THROUGHPUT_V1.md`](FACTORY_THROUGHPUT_V1.md) · [`FOUNDER_OPERATOR_SURFACE_V1.md`](FOUNDER_OPERATOR_SURFACE_V1.md) · [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md)

---

## Unified report (pipeline + factory)

`ppe_pipeline_health.cmd` now includes:

- **ROOT CAUSE** — bookkeeping deadlocks (coordination)
- **FACTORY** — throughput verdict (`moving` / `stuck` / `stack_down`)
- **SUPPLY** — queue READY / blocked / queued

One JSON: `PIPELINE_HEALTH.json` (factory section embedded). Detail throughput: `FACTORY_THROUGHPUT.json`.

---

## When something feels wrong (~2 minutes)

```bat
ppe_pipeline_health.cmd
type artifacts\control_plane\PIPELINE_HEALTH.json
```

Or full infra + pipeline:

```bat
ppe_doctor.cmd
```

Read **`ROOT CAUSE`** at the top of `artifacts/orchestrator/OPERATOR_STATUS.md` (regenerated on every status write).

---

## Fix classes

| Class | Meaning | Typical action |
|-------|---------|----------------|
| `proceed` | Pipeline OK | Continue relay / BUILD |
| `repair` | Safe auto-repair (markers, registry) | `ppe_chapter_coordination.py --repair` |
| `recovery` | Branch/git/mixed-plane | `ppe_branch_recovery.py --plane control --ship` |
| `park` | Canon/doc conflict | Align evidence/frontier honestly; founder judgment |

---

## Contradiction codes

| Code | Meaning |
|------|---------|
| `DEADLOCK_IDE_BUILD_CLOSEOUT` | Verdict says BUILD but product is on `main` — marker deadlock |
| `BRANCH_BLOCKS_RELAY` | Wrong branch blocks relay |
| `VM_VERDICT_MISMATCH` | Desktop vs VM disagree — trust VM |
| `FRONTIER_AHEAD_OF_EVIDENCE` | Frontier COMPLETE before evidence |
| `MILESTONE_BLOCKED` | Next BUILD candidate blocked ≥1 day |

Full coordination codes: [`CHAPTER_COORDINATION_V1.md`](CHAPTER_COORDINATION_V1.md) § Issue codes.

---

## Artifacts

| File | Role |
|------|------|
| `artifacts/control_plane/PIPELINE_HEALTH.json` | Machine-readable snapshot |
| `artifacts/control_plane/PIPELINE_HEALTH_STATE.json` | Regression alert dedupe |
| `artifacts/control_plane/COORDINATION_CHECK.json` | Coordination synthesizer |
| `artifacts/orchestrator/OPERATOR_STATUS.md` | Human status + ROOT CAUSE block |

---

## Alerts (ntfy)

Pipeline health sends mobile push when:

- OK → not OK (regression)
- Root cause code changes
- Milestone blocked ≥1 day (daily dedupe)

Enable: `ppe_operator_notify.local.cmd` + `PPE_NTFY_TOPIC`. Run with `--notify` or via operator status refresh.

---

## Gate and burst

- **Burst:** blocked when `PIPELINE_HEALTH.json` has `blocks_burst: true` (recovery/park/deadlock).
- **Pre-push gate:** fails when `blocks_gate: true` **on `main`** (recovery/park).
- **Main + coordination-sensitive paths:** commit blocked when pipeline is recovery/park.
- **Override:** `PPE_PIPELINE_GATE=0` (not recommended).

Feature-branch recovery PRs are not blocked by the sensitive-path rule.

---

## Commands

```bat
python scripts/ppe_pipeline_health.py --write --json
python scripts/ppe_pipeline_health.py --write --notify
python scripts/ppe_coordination_check.py --write --json
python scripts/ppe_chapter_coordination.py
ppe_doctor.cmd
```
