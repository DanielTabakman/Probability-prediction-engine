# GOOGLE_DOCS_CONTROL_PLANE_V1

Purpose: make “refresh Google Docs” repeatable and low-friction, without violating the control-plane role split.

This SOP defines:

- **Which doc is authoritative for what**
- **What an update/refresh means**
- **How to regenerate the MSOS mirror from repo truth**
- **What must never be edited via MCP**

## Documents and roles (hard rules)

### PPE Master (Google Doc)

- **Job**: strategy + canon + MVP contracts + audit framing.
- **Writer**: **ChatGPT / founder steward**.
- **Cursor**: **read-only** (Cursor may read for guidance; must not silently rewrite canon).
- **MCP rule**: **do not write PPE Master via google-docs MCP**.

### PPE / MSOS Repo Truth — Live Mirror (Google Doc)

- **Job**: repo-grounded status mirror for steering (freshness, HEAD, what changed, gates, deployment witness, next action).
- **Writer**: **Cursor automation / agents**.
- **ChatGPT / founder**: read-only (treat as report, not canon).
- **Write boundary**: only update the content between:
  - `MSOS_REPO_TRUTH_AUTO_START`
  - `MSOS_REPO_TRUTH_AUTO_END`
  (the rest of the doc is human intro / framing and should not be rewritten by automation).

## Refresh protocol (GOOGLE_DOCS_REFRESH)

GOOGLE_DOCS_REFRESH keeps the Google Docs control plane aligned with **repo truth**, **deployment truth** (when applicable), and **current Cursor execution state**.

This is a control-plane maintenance action. Treat it like “re-generate and publish the latest truth,” not “start a build.”

### Purpose

GOOGLE_DOCS_REFRESH keeps the Google Docs control plane aligned with repo truth, deployment truth, and current Cursor execution state.

### Triggers

- **Manual**: founder says “refresh Google Docs”.
- **Daily scheduled refresh** (GitHub Actions).
- **After closeout** (best-effort mirror refresh chained from closeout).
- **After deployment changes** (domain / hosting / pipeline changes; redeploys; env changes).
- **After naming / control-plane changes** (doc ids, marker names, SOP names, control-plane file paths).
- **After queue / selection changes** (new SELECTION outcome; phase manifest updates; continuity brief updates).

### Inputs (evidence sources)

- **Active PPE Master / Copy** (Google Doc; steward-owned canon).
- **PPE / MSOS Repo Truth — Live Mirror** (Google Doc; automation-owned mirror).
- **Repo docs** (especially `docs/SOP/*` and `docs/VISION/*`).
- **Current repo state**: branch / HEAD / working tree, plus relevant diffs since last refresh.
- **Validation evidence**: test/smoke/deploy artifacts and/or linked run reports when applicable.

### Required outputs

At the end of refresh, the following must be captured (in the mirror and in the refresh report):

- **Regenerated Live Mirror** (marker block updated from repo truth).
- **Current timestamp** (UTC) on the mirror.
- **Branch / HEAD / working tree** status.
- **Selected or active chapter** (best-effort from continuity + manifest).
- **Latest delta** since previous refresh (best-effort; at minimum “repo changed / did not change”).
- **Fresh vs historical validation evidence** (explicitly label what was run now vs older evidence).
- **Website / deployment witness** (when applicable; include what you observed and when).
- **Known blockers / drift** (including naming/control-plane drift).
- **Recommended next move** (e.g., “run SELECTION,” “run gate,” “steward decision needed,” “deploy witness pending”).
- **Whether Master needs update** (yes/no/unknown; never silently write Master).

### Success criteria (must all hold)

- **Google Doc visibly updates** (mirror marker block changes are observable).
- **Regenerated timestamp is current** (UTC now, not stale).
- **HEAD matches current repo state** (mirror HEAD == local `git rev-parse HEAD`).
- **Stale naming check completed** (doc ids / markers / file paths referenced here are still correct).
- **Refresh report emitted** (see Report format below).
- **No product behavior changed** unless explicitly authorized (refresh is sync/maintenance only).

### Failure criteria (any of these is a failure)

- **Live Mirror not updated** (marker block unchanged when it should be updated).
- **Timestamp stale**.
- **HEAD missing or mismatched**.
- **Sync script errors** (`sync_msos_repo_truth.py` or `google_docs_sync.py` failures).
- **Google Docs write failure** (MCP/API write fails or marker block not found).
- **Unclear active chapter / selection state** (cannot infer and did not report uncertainty).

### Escalation (hard rule)

If repo truth and PPE Master canon disagree, **do not silently resolve**.

- Report the mismatch.
- Ask founder / ChatGPT steward to decide: update Master, update repo, or defer with an explicit reason.

### Boundaries (hard rule)

Refresh is **maintenance/synchronization**, not a product build.

- Do **not** change UI, trading logic, roadmap, pricing, or product behavior unless explicitly selected as a BUILD chapter.
- Allowed changes during refresh: reporting accuracy, mirror generation, naming drift fixes within control-plane docs/scripts, and clarifying SOP text.

### Canonical procedure (local Cursor run)

1. **Capture repo state** (for the report)
   - Branch / HEAD / working tree status.
2. **Regenerate the Live Mirror snapshot artifacts** (repo truth → local artifacts)
   - Run `python scripts/sync_msos_repo_truth.py`
   - Outputs:
     - `artifacts/msos_repo_truth_snapshot.md`
     - `artifacts/control_plane/msos_sync_report.json`
3. **Update the Live Mirror Google Doc marker block**
   - Preferred: run `python scripts/google_docs_sync.py --sync-repo-to-mirror --write-report`
     - This uses Google APIs directly (CI-friendly) and replaces the marker block range.
   - Alternative: use google-docs MCP to replace only the marker block
     - Never write outside `MSOS_REPO_TRUTH_AUTO_START` / `MSOS_REPO_TRUTH_AUTO_END`.
4. **Do not write PPE Master**
   - If drift is found, report it and escalate to steward decision.
5. **Import PPE Master into repo when steward edits canon** (separate step — not part of mirror refresh)
   - Run `python scripts/google_docs_sync.py --sync-master-to-repo`
   - Updates `docs/VISION/PPE_MASTER_MVP1.md` from the Google Doc.
   - **`ppe_google_docs_refresh.py` and closeout mirror refresh do not run this step.** Agents that grep repo canon need master-to-repo after steward edits.
6. **Confirm the Drive doc shows the new regenerated timestamp**
   - Verify the mirror doc text contains the current “Generated (UTC)” timestamp from the latest run.

### Report format (required)

Return a **GOOGLE_DOCS_REFRESH REPORT**:

- **Branch / HEAD**
- **Working tree**
- **Freshness verdict**
- **What changed since last refresh**
- **Validation run** (fresh vs historical)
- **Website / deployment witness** (if applicable)
- **Live Mirror regenerated**: yes/no + timestamp
- **Naming/control-plane drift found**
- **Master update needed**: yes/no/unknown
- **Recommended next move**
- **Confidence**

## Automation path (closeout)

After relay **CONTINUE** with a phase-plan `closeout`, repo closeout runs:

- `apply_control_closeout_v1` (updates repo `docs/SOP/*` steering docs)
- then **best-effort** MSOS mirror refresh

See `docs/SOP/RELAY_ORCHESTRATOR_RUNBOOK_V1.md` for the closeout chain and expected artifacts.

## Automatic sync (GitHub Actions)

If you want this to run automatically (not just in Cursor), use the workflow:

- `.github/workflows/google-docs-sync.yml`

### Required GitHub secrets

- `PPE_MASTER_DOC_ID`
- `PPE_MSOS_MIRROR_DOC_ID`
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REFRESH_TOKEN`

**OAuth scopes (CI):** GitHub Actions uses the minimal sync scopes in [`scripts/google_oauth_scopes.py`](../../scripts/google_oauth_scopes.py) (`documents` + `drive.readonly`). The refresh token must include at least those scopes. If sync fails with `insufficientPermissions` after a scope change, re-run OAuth consent (see [`MCP_GOOGLE_DOCS_SETUP.md`](MCP_GOOGLE_DOCS_SETUP.md)) and update `GOOGLE_OAUTH_REFRESH_TOKEN` in GitHub secrets. Local Cursor MCP may still use broader MCP scopes; that is separate from CI.

### What it does

1. Generates a fresh local mirror snapshot:
   - `python scripts/sync_msos_repo_truth.py`
2. Syncs PPE Master → repo and repo → mirror:
   - `python scripts/google_docs_sync.py --sync-master-to-repo --sync-repo-to-mirror`
3. Commits any resulting repo changes.

### Safety / role split

- PPE Master remains **written by the steward**; automation only **reads** it.
- The MSOS mirror is updated from repo truth, using marker boundaries.

