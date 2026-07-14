# Founder portfolio commands examples v1

**Plane:** CONTROL-PLANE
**Status:** Read-only implementation examples for PPE #5357
**Canon:** `docs/SOP/FOUNDER_PIPELINE_COMMANDS_V1.md`

This chapter adds examples for the v1 read-only command adapter. It does not
authorize build dispatch, continuous refill, scheduled tasks, queue writes, or
Autobuilder runtime changes.

## Commands

```powershell
python scripts/founder_portfolio.py commands
python scripts/founder_portfolio.py whats-next
python scripts/founder_portfolio.py whats-running
python scripts/founder_portfolio.py whats-next --json
```

## Evidence labels

The founder view labels state as:

- `native_runtime` when a pipeline-owned runtime artifact is present and fresh;
- `manual` or `canonical` when the source is a maintained GitHub control-plane file;
- `external` when the adapter is reading a configured cross-repository source root;
- `inferred` when the adapter derives a founder state from non-runtime evidence;
- `missing` when an expected source is absent;
- `stale` when the source exists but is older than the adapter freshness window.

Pipeline-native state remains authoritative. The adapter's normalized states are
for founder visibility only.

## Read-only boundary

`scripts/founder_portfolio.py` only reads files. It does not call the existing
operator collectors that can repair queue state or write status artifacts, and it
does not invoke any msos-autobuilder runtime command.

## State semantics

Native `READY` frontier rows are reported as `READY_TO_BUILD`. They are not
reported as `QUEUED` unless a future dispatch adapter has accepted and submitted
the work to an actual worker queue. A missing or stale Autobuilder external
source is scoped to the Autobuilder pipeline and does not block unrelated safe
PPE `READY_TO_BUILD` work.

## Cross-repository source

The Autobuilder adapter is explicitly external. It reads from
`MSOS_AUTOBUILDER_STATUS_ROOT` when that environment variable points at a
read-only checkout or exported runtime-status root for
`DanielTabakman/msos-autobuilder`. PPE is not a fallback location for those
runtime artifacts.

## Selection policy

The read-only recommendation ranks safe `READY_TO_BUILD` work by accepted
founder priority, external deadline, dependency-unblock value, evidence
freshness, portfolio fairness, age within the priority class, and deterministic
tie-breakers. The selection report explains the winning rank. This is
recommendation-only; it does not dispatch.
