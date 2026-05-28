# MVP1 deploy witness refresh — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md).  
**SELECTION:** [`DEPLOY_WITNESS_REFRESH_SELECTION.md`](DEPLOY_WITNESS_REFRESH_SELECTION.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Refresh [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) and the chapter evidence doc against current `main` without product-plane changes. Runs under **deterministic** worker mode (`PPE_WORKER_MODE=deterministic` / `PPE_SKIP_ACP=1`).

## Sprint-level acceptance

1. Charter slice aligns roadmap, queue, sprint spec, and evidence status.
2. Smoke slice runs `python -m pytest -q` (witness count recorded in evidence doc).
3. Closeout marks chapter **COMPLETE**, manifest idle, queue **DONE**, roadmap advances.

## Not now

- VPS deploy or production config changes.
- New product surfaces or classification math.

---

## Slice map

### MVP1-DeployWitness-Control-Slice001 — charter (EVIDENCE-PLANE)

Align phase plan, queue, roadmap row, and [`MVP1_DEPLOY_WITNESS_REFRESH_EVIDENCE_STATUS.md`](MVP1_DEPLOY_WITNESS_REFRESH_EVIDENCE_STATUS.md).

### MVP1-DeployWitness-Smoke-Slice002 — pytest witness (EVIDENCE)

Run full pytest; record pass line in evidence doc.

### MVP1-DeployWitness-Closeout-Slice003 — chapter close (CONTROL)

Control closeout — steering note, manifest **COMPLETE**, queue **DONE**, roadmap next pending.
