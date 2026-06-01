# MSOS Website Program P0 — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) · [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md)  
**SELECTION:** [`POST_MSOS_WEBSITE_PROGRAM_P0_SELECTION.md`](POST_MSOS_WEBSITE_PROGRAM_P0_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Install the MSOS Website Program (waterfall P0–P8) into repo canon and the automated relay queue. Control-plane / evidence only — **no `src/` changes**.

## Touch set (allowed)

- `docs/SOP/MSOS_*.md`, `docs/SOP/POST_MSOS_*.md`, `docs/SOP/SPRINT_MSOS_*.md`
- `docs/SOP/PHASE_PLANS/msos_*.json`
- `docs/SOP/PHASE_QUEUE.json`, `PHASE_SELECTION_ROADMAP.json`, `PHASE_CHAPTER_BACKLOG.json`
- `docs/SOP/MVP1_FRONTIER.md` (parallel-track pointer only)
- `docs/SOP/PPE_INTEGRATED_STATUS.md`, `docs/README.md`, `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`
- `docs/SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md` (refresh vs master-sync callout)
- `docs/VISION/MSOS_STORYBOARD_GATE.md`
- `docs/VISION/PPE_MASTER_MVP1.md` (via `google_docs_sync.py --sync-master-to-repo` only)
- `tests/test_msos_p0_charter_witness.py`

## Acceptance

1. `PPE_MASTER_MVP1.md` contains `MSOS WEBSITE PROGRAM — SELECTED WATERFALL QUEUE — 2026-05-31`.
2. `MSOS_WEBSITE_PROGRAM.md` and `MSOS_FRONTIER.md` exist with hierarchy + non-widening rule.
3. `PHASE_QUEUE.json` has `msos_website_program_p0_relay.json` as first **READY** (or **DONE** after closeout).
4. `PHASE_CHAPTER_BACKLOG.json`: P1 **queued**, P2–P8 **blocked**.
5. `MVP1_FRONTIER.md` points to MSOS track; MVP1 relay idle.
6. `python -m pytest -q tests/test_msos_p0_charter_witness.py` green.
7. Queue health audit clean (`audit_queue`).

## Not now

- Product UI, deploy config changes, PPE math changes
- Unblocking P2+ without storyboard assets

---

## Slice map

### MSOS-P0-Control-Slice001 — charter

Sync master; create/update MSOS docs; wire queue/backlog/roadmap; steering index updates.

### MSOS-P0-Witness-Slice002 — charter witness

Run `tests/test_msos_p0_charter_witness.py`; queue health.

### MSOS-P0-Closeout-Slice003 — chapter close

Control closeout; manifest COMPLETE; queue item DONE; MSOS frontier updated; P1 propagated.
