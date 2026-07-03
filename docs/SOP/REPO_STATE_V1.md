# Repo state SSOT v1

**Plane:** CONTROL-PLANE · **Artifact:** `artifacts/control_plane/REPO_STATE.json`

Single source of truth for dirty-tree classification, severity, and recovery routing. Replaces scattered mixed-plane heuristics across preflight, delegation, and coordination.

## Severity ladder

| Level | Label | Gate | Burst | Relay | Typical cause |
|-------|-------|------|-------|-------|----------------|
| 0 | `CLEAN` | pass | yes | yes | Clean tree |
| 1 | `CAUTION` | pass | yes | yes | Single-plane dirty on feature branch |
| 2 | `STEWARD` | warn | **no** | **no** | Mixed-plane, steward_packet, branch blocks relay |
| 3 | `BLOCKED` | fail | no | no | human_only, detached HEAD, untracked SOP |

## Plane map (unified)

| Prefix | Plane |
|--------|-------|
| `docs/SOP/` | CONTROL |
| `src/`, `apps/` | PRODUCT |
| `tests/`, `scripts/` | EVIDENCE |
| `docs/VISION/`, `docs/RELEASES/` | CANON |
| `.github/`, `docs/DEPLOY/` | PLATFORM |

**Mixed-plane:** ≥2 core planes dirty. Exception: `src/` + companion `tests/` only → not mixed.

## Commands

```bat
python scripts/ppe_repo_state.py --write --json
python scripts/ppe_branch_recovery.py --plan-only --json
python scripts/ppe_branch_recovery.py --ship-all
python scripts/ppe_branch_recovery.py --verify
python scripts/ppe_operator_dispatch.py --from-burst-plan --force
python scripts/ppe_parked_work.py --write --reason mixed_plane
```

## Related artifacts

| File | Role |
|------|------|
| `REPO_STATE.json` | Live assessment (refreshed on operator status) |
| `RECOVERY_REPORT.json` | Post-recovery transaction log |
| `PARKED_WORK.json` | Charter/closeout park queue for operator |
| `COORDINATION_CHECK.json` | Burst/relay gate (reads repo state) |

## Related

- [`RECOVERY_PROTOCOL.md`](RECOVERY_PROTOCOL.md)
- [`DELEGATION_ENVELOPE_V1.md`](DELEGATION_ENVELOPE_V1.md)
- [`DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md`](DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md)
