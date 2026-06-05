# Repo housekeeping v1 — relay sprint spec

**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) · [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)  
**SELECTION:** [`POST_REPO_HOUSEKEEPING_V1_SELECTION.md`](POST_REPO_HOUSEKEEPING_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Bounded control-plane maintenance after MSOS P4 closeout: operator hygiene, queue/consistency witness, optional SOP trim. **No product features.**

## Sprint-level acceptance

1. `python scripts/ppe_queue_health.py --repo-root . --apply` — zero remaining issues (or documented exceptions in evidence doc).
2. Worktree prune: dry run then `-Keep 3 -Force` only when candidates exist ([`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)).
3. `control_plane_consistency_check` — **passed** (artifact under `artifacts/health/`).
4. [`REPO_HOUSEKEEPING_V1_EVIDENCE_STATUS.md`](REPO_HOUSEKEEPING_V1_EVIDENCE_STATUS.md) — **COMPLETE**.
5. `python -m pytest -q` green if `scripts/` or `tests/` touched.

## Not now

- `src/**`, `apps/msos-web/**` (separate product chapter required).
- `artifacts/**` bulk deletion without retention note in evidence doc.
- Cross-module refactors or relay runtime upgrades.

---

## Slice map

### RepoHousekeeping-Control-Slice001 — charter (CONTROL)

**Goal:** Accept sprint spec + phase plan; one-line HANDOFF / frontier note if drift found.

**Allowed:** `docs/SOP/**` only.

---

### RepoHousekeeping-Evidence-Slice002 — housekeeping (EVIDENCE)

**Goal:** Run maintenance commands; record exact output in evidence doc.

**Commands (run in order; paste results into evidence):**

```bat
python scripts/ppe_queue_health.py --repo-root . --apply
powershell -File scripts/cleanup_orchestrator_worktrees.ps1 -Keep 3
powershell -File scripts/cleanup_orchestrator_worktrees.ps1 -Keep 3 -Force
```

Optional when trivial fixes only:

```bat
python -m ruff check scripts tests
python scripts/run_pushable_gate.py
```

**Allowed paths:** `scripts/`, `docs/SOP/`, `tests/`, `.cursor/rules/` (context trim only if named in SELECTION trigger).

---

### RepoHousekeeping-Witness-Slice003 — witness (EVIDENCE)

**Goal:** Relay stage `control_plane_consistency_check`; confirm queue health clean.

**Acceptance:** `artifacts/health/*/control_plane_consistency_report.json` with `passed: true`.

---

### RepoHousekeeping-Closeout-Slice004 — chapter close (CONTROL)

**Goal:** Evidence doc **COMPLETE**; update SELECTION outcome with close date; chapter marked done in backlog via `post_relay_continue`.

---

## Sprint status

**Repo housekeeping v1:** **NOT STARTED** (blocked until MSOS P4 **COMPLETE**).
