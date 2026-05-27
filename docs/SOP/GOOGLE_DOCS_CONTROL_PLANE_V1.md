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

When the steward says **“refresh Google Docs”**, Cursor should do **maintenance + synchronization**, not a product BUILD.

### Required actions

1. **Repo state**
   - Branch
   - HEAD
   - Working tree status (clean/dirty)
2. **Generate a mirror snapshot** from repo truth (local artifact)
   - Run `python scripts/sync_msos_repo_truth.py`
   - This produces:
     - `artifacts/msos_repo_truth_snapshot.md`
     - `artifacts/control_plane/msos_sync_report.json`
3. **Write the mirror (Google Doc)**
   - Replace only the marker block in **PPE / MSOS Repo Truth — Live Mirror** with the generated snapshot.
   - Use google-docs MCP write tools (`replaceRangeWithMarkdown` or equivalent).
4. **Do not write PPE Master**
   - If mismatch/drift is found, **report it** and request a steward decision (update Master vs update repo vs defer).
5. **Produce a REFRESH REPORT**
   - Branch / HEAD:
   - Working tree:
   - Freshness verdict:
   - Snapshot generated: path + timestamp:
   - Mirror updated (Google Doc): yes/no:
   - Drift found:
   - Recommended next move:
   - Confidence:

### Boundary rule

Refresh is control-plane maintenance only. It may fix small inconsistencies in reporting, naming, or mirror generation. It must not introduce new product behavior, UI changes, trading logic, or commercial claims unless separately selected as a BUILD slice.

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

### What it does

1. Generates a fresh local mirror snapshot:
   - `python scripts/sync_msos_repo_truth.py`
2. Syncs PPE Master → repo and repo → mirror:
   - `python scripts/google_docs_sync.py --sync-master-to-repo --sync-repo-to-mirror`
3. Commits any resulting repo changes.

### Safety / role split

- PPE Master remains **written by the steward**; automation only **reads** it.
- The MSOS mirror is updated from repo truth, using marker boundaries.

