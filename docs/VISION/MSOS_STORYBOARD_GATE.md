# MSOS storyboard gate (P2+)

**Purpose:** Block visible MSOS UI BUILD until approved visual reference exists in-repo.

## Requirement (from PPE Master waterfall)

Before **P2 — Design system + public MSOS homepage** or any user-facing visual implementation:

1. Place **Market Structure OS Website Storyboard v0.6** assets in-repo (PDF, montage, or equivalent screen exports).
2. Preferred path: `docs/VISION/MSOS/storyboard-v0.6/` (create when assets arrive).
3. Record asset manifest in this file (filename list + import date).

## Current status

| Field | Value |
|-------|--------|
| **Gate** | **CLOSED** (assets not in-repo) |
| **Blocks** | P2–P8 MSOS UI chapters in [`PHASE_CHAPTER_BACKLOG.json`](../SOP/PHASE_CHAPTER_BACKLOG.json) |
| **Does not block** | P0 (queue install), P1 (stack/routing ADR) |

## Unblock procedure

1. Operator drops storyboard files under `docs/VISION/MSOS/storyboard-v0.6/`.
2. Update this file: set gate **OPEN**, list files, date.
3. Steward SELECTION: move `msos_p2_homepage` from `blocked` → `queued` after P1 ADR merged.

## Screenshot witness (ongoing)

For each major finished visual surface after P2+, include screenshot witness in chapter evidence doc and note material deviations in closeout.
