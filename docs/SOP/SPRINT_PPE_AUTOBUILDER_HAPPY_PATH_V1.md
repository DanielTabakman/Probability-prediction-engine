# PPE autobuilder happy path v1 — relay sprint spec

**SELECTION:** [`POST_PPE_AUTOBUILDER_FACTORY_SELECTION.md`](POST_PPE_AUTOBUILDER_FACTORY_SELECTION.md)  
**Baseline:** `main` · **Layer:** `dev-factory` / `CONTROL`

## Intent

Zero-click product slice pipeline: loop/watch call `ppe_autobuilder advance` on `AWAITING_BUILD`, `CLOSEOUT_PENDING`, `RUN_LOCAL_PENDING`, and `STACK_DOWN` without phone ping or `ppe_go.cmd` on the happy path.

## Acceptance

1. `autobuilder.happyPath: true` in [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) (default off until slice ships).
2. `happy_path_enabled()` + `try_autobuilder_happy_path()` in `scripts/ppe_autobuilder.py`.
3. Wired from `ppe_headless_auto_loop_entry.py`, `ppe_operator_loop_pass.py`, `ppe_watch_operator_mobile.py`.
4. On successful happy-path handoff, suppress urgent ntfy (informational only or skip).
5. Tests in `tests/test_ppe_autobuilder.py`.
6. [`PPE_AUTOBUILDER_HAPPY_PATH_V1_EVIDENCE_STATUS.md`](PPE_AUTOBUILDER_HAPPY_PATH_V1_EVIDENCE_STATUS.md) **COMPLETE**.

## Not now

- MSOS / `apps/msos-web/**` / `src/engine/**`
- Full commercial onboarding template

## Slices

| sliceId | Plane | Goal |
|---------|-------|------|
| `PPE-AutobuilderHappyPath-Control-Slice001` | CONTROL | Charter + update `PPE_AUTOBUILDER_V1.md` |
| `PPE-AutobuilderHappyPath-Factory-Slice002` | EVIDENCE | Implement happy path wiring + config (`scripts/`, tests) |
| `PPE-AutobuilderHappyPath-Witness-Slice003` | EVIDENCE | Evidence doc + pytest |
| `PPE-AutobuilderHappyPath-Closeout-Slice004` | CONTROL | Relay closeout |
