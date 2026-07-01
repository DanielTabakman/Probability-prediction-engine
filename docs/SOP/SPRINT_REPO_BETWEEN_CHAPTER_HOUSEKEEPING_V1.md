# Repo between-chapter housekeeping v1

**Plane:** CONTROL-PLANE · **Layer:** `CONTROL`  
**Trigger:** auto-scheduled by `post_relay_continue` after each product chapter closeout (`scripts/ppe_between_chapter_housekeeping.py`).

---

## Sprint intent

Recurring control-plane hygiene between product chapters: queue health, structural health witness, worktree prune when needed. **No product features.**

## Commands (Evidence slice)

```bat
python scripts/run_between_chapter_housekeeping.py --repo-root .
python scripts/ppe_queue_health.py --repo-root . --apply
python scripts/run_codebase_health_gate.py --repo-root .
```

Optional when worktrees exist:

```bat
powershell -File scripts/cleanup_orchestrator_worktrees.ps1 -Keep 3
powershell -File scripts/cleanup_orchestrator_worktrees.ps1 -Keep 3 -Force
```

## Acceptance

1. `ppe_queue_health --apply` — zero remaining issues (or documented in evidence).
2. `run_codebase_health_gate.py` — OK (structural warnings logged only).
3. Evidence doc updated with run timestamp.
4. Closeout slice marks this cycle **COMPLETE**; `recurring: true` allows re-run after next product chapter.

## Not in scope

- `src/**`, `apps/msos-web/**`
- Cross-module refactors
