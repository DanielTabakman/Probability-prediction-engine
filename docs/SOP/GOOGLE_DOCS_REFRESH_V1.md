# Google Docs refresh v1 (GOOGLE_DOCS_REFRESH)

**Canonical human command:** `refresh Google Docs` (or run [`refresh_google_docs.cmd`](../../refresh_google_docs.cmd) from repo root).

**Purpose:** Keep the control plane aligned when a cycle ends, a new cycle starts, or repo/deploy/naming reality changes. This is **maintenance**, not a product BUILD.

**Authority:** PPE Master (Google) defines the full protocol; this file is the **repo mirror** for Cursor, relay, and operators without MCP.

---

## When to run

| Trigger | When | How |
|---------|------|-----|
| **cycle-end** | After chapter **closeout** (`apply_control_closeout_v1` patches steering docs) | Automatic: [`post_relay_continue.py`](../../scripts/post_relay_continue.py) |
| **cycle-start** | After steward **SELECTION** (`ACTIVE_PHASE_MANIFEST` → `READY`) and before `run_ppe.cmd` | Automatic: [`ppe_run.py`](../../scripts/ppe_run.py) (best-effort) |
| **manual** | Anytime steering feels stale; after deploy; after renaming docs | `refresh_google_docs.cmd` or agent: *refresh Google Docs* |

**Operator habit:** at **SELECTION** and after **chapter close**, say *refresh Google Docs* (or rely on automation above).

---

## What the job does

1. Inspect git branch, HEAD, working tree, upstream ahead/behind.
2. Scan `docs/`, `scripts/`, `.cursor/rules/` for stale control-plane naming.
3. Run lightweight control-plane validation (`py_compile` + MSOS/refresh pytest).
4. Regenerate **PPE / MSOS Repo Truth — Live Mirror** via `sync_msos_repo_truth_v1` (unless `--dry-run` / `--skip-msos-push`).
5. Record freshness, delta vs last report, witness summary, warnings, recommended next move.
6. Write artifacts (gitignored): `artifacts/control_plane/google_docs_refresh_report.json` and `.md`.

**Hard rules (unchanged):**

- Cursor **never writes** PPE Master (Google).
- Live Mirror is updated **only** by `sync_msos_repo_truth_v1` inside this refresh job.
- Pushed repo + `MVP1_FRONTIER.md` win disputes; report mismatches to steward / ChatGPT.

---

## Commands

```powershell
# Full refresh (default trigger: manual)
refresh_google_docs.cmd

# Snapshot only (no Google API push)
refresh_google_docs.cmd --dry-run

# Explicit trigger label in report
python scripts/google_docs_refresh.py --repo-root . --trigger cycle-start
python scripts/google_docs_refresh.py --repo-root . --trigger cycle-end
```

---

## Report format (for founder / ChatGPT)

After each run, open `artifacts/control_plane/google_docs_refresh_report.md` or ask the agent for the **GOOGLE_DOCS_REFRESH report**. Fields:

- Branch / HEAD
- Working tree
- Freshness verdict
- What changed since last refresh
- Validation run
- Website / deployment witness
- Live Mirror regenerated (yes/no, timestamp)
- Naming / control-plane drift
- Master Doc import needed (repo `PPE_MASTER_MVP1.md` missing protocol text)
- Recommended next move
- Confidence

---

## Boundary and escalation

- **Not** a product BUILD by default; no new UI, trading logic, or scope unless explicitly chartered.
- If repo truth and PPE Master canon disagree, **report** — do not silently fix Master or widen MVP1 scope.
- MSOS marker missing with OAuth configured → exit `2` (operator visibility); skip without credentials → exit `0`.

---

## Related

- [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md) — roles, markers, MSOS setup
- [`JOB_REGISTRY_V1.md`](JOB_REGISTRY_V1.md) — §3.7 `google_docs_refresh_v1`
- [`ACTIVE_PHASE_MANIFEST.md`](ACTIVE_PHASE_MANIFEST.md) — SELECTION checklist
- [`MCP_GOOGLE_DOCS_SETUP.md`](MCP_GOOGLE_DOCS_SETUP.md) — OAuth once

## Last updated

2026-05-25 — v1: cycle-start/cycle-end automation + `refresh_google_docs.cmd` + repo protocol mirror.
