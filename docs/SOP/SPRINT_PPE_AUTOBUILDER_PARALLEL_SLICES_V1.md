# PPE autobuilder parallel slices v1 — relay sprint spec

**SELECTION:** [`POST_PPE_AUTOBUILDER_FACTORY_SELECTION.md`](POST_PPE_AUTOBUILDER_FACTORY_SELECTION.md)  
**Ref:** [`PARALLEL_AGENT_CHECKLIST_V1.md`](PARALLEL_AGENT_CHECKLIST_V1.md)

## Intent

Multi-lock `BUILD_IN_FLIGHT` when layer audit confirms disjoint `ALLOWED_PATHS` for concurrent product slices.

## Acceptance

1. `read_build_lock` → `read_build_locks` (list); phase derivation handles multiple locks.
2. Document parallel charter requirements in evidence doc.
3. Tests for non-overlapping slice pair.
