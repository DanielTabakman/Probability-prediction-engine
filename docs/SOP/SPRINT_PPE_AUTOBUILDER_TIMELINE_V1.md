# PPE autobuilder timeline v1 — relay sprint spec

**SELECTION:** [`POST_PPE_AUTOBUILDER_FACTORY_SELECTION.md`](POST_PPE_AUTOBUILDER_FACTORY_SELECTION.md)

## Intent

`artifacts/orchestrator/AUTOBUILDER_TIMELINE.md` — human-readable 24h pipeline timeline from status JSON, relay runs, git commits.

## Acceptance

1. `write_autobuilder_timeline(repo)` called from `ppe_autobuilder diagnose` and `status --write`.
2. Evidence doc **COMPLETE**; tests for timeline sections.
