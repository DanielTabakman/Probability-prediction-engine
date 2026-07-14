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
- `manual` when the source is a maintained GitHub control-plane file;
- `inferred` when the adapter derives a founder state from non-runtime evidence;
- `missing` when an expected source is absent;
- `stale` when the source exists but is older than the adapter freshness window.

Pipeline-native state remains authoritative. The adapter's normalized states are
for founder visibility only.

## Read-only boundary

`scripts/founder_portfolio.py` only reads files. It does not call the existing
operator collectors that can repair queue state or write status artifacts, and it
does not invoke any msos-autobuilder runtime command.
