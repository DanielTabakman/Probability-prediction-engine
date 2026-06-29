# Options Horizon replay scrubber v1 — relay sprint spec

**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**SELECTION:** [`POST_OPTIONS_HORIZON_REPLAY_SCRUBBER_V1_SELECTION.md`](POST_OPTIONS_HORIZON_REPLAY_SCRUBBER_V1_SELECTION.md)  
**Prior chapter:** [`SPRINT_OPTIONS_HORIZON_REGION_WORKFLOW_V1.md`](SPRINT_OPTIONS_HORIZON_REGION_WORKFLOW_V1.md) (must be COMPLETE)  
**Baseline:** **`main`**

---

## Sprint intent

Add a **timeline scrubber** on `/options-horizon` so traders can step through **archived** options-implied surfaces (daily snapshots) without live re-fetch on every scrub step.

**Priority:** LOW / P2 — after region workflow + ≥30d archive.

---

## Slice acceptance

### Horizon-ReplayScrub-Control-Slice001 (CONTROL)

- Evidence stub + relay plan reference
- Archive replay gate documented in evidence status

### Horizon-ReplayScrub-Product-Slice002 (MSOS_UI)

- Fetch `archive_meta` (or equivalent) to gate scrubber visibility
- Scrubber control (slider or date list) wired to horizon surface archive API
- Chart implied overlay refreshes from archived snapshot for selected `as_of`
- Preserve region workflow + Strategy Lab deep-link behavior

### Horizon-ReplayScrub-Closeout-Slice003 (CONTROL)

- Evidence COMPLETE
- Milestone H5 replay witness checked

---

## Witness (chapter close)

- [ ] Scrubber steps across ≥2 archive dates when `replay_ready`
- [ ] Implied overlay matches archived snapshot (no client-side PDF math)
- [ ] Scrubber disabled/hidden with honest copy when archive thin
- [ ] Simulation-only copy unchanged
- [ ] Region save/load still works during replay
