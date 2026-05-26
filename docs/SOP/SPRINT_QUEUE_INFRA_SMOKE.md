# Queue infra smoke — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md).  
**SELECTION:** [`QUEUE_INFRA_SMOKE_SELECTION.md`](QUEUE_INFRA_SMOKE_SELECTION.md).  
**Relay baseline:** **`build/msos-live-mirror-title`** (local; includes queue runner + viz discipline automation).

---

## Sprint intent

End-to-end validation of **chapter-level queue** + **`run_queue_cycle`** + **`run_ppe.cmd`** on the current feature branch. No product semantics changes.

## Sprint-level acceptance

1. **`python -m pytest -q tests/test_queue_cycle_contract.py tests/test_queue_cycle_stops_on_blocked.py`** green after witness slice.
2. **`python scripts/run_queue_cycle.py --dry-run`** exits 0 from repo root.
3. Chapter closeout updates evidence + steering pointers per closeout block.
4. Queue item `Q-INFRA-0001` ends **`DONE`** when manifest reaches **`COMPLETE`**.

## Not now

- Full dual implied-lab smoke (optional steward pass before merge to `main`).
- Parsing `MVP1_FRONTIER.md` for auto-queuer (deferred).
- Product slices under `src/viz/` beyond what witness requires.

---

## Slice map

### QueueInfra-Charter-Slice001 — charter (CONTROL)

**Scope:** Confirm `SLICE_QUEUE_V1.json` item `Q-INFRA-0001`, sprint spec links, and evidence template. Run `python scripts/resolve_active_phase.py` after manifest is set (relay worker or steward witness).

**Closeout gate:** Evidence doc charter section started.

---

### QueueInfra-Witness-Slice002 — queue tests (EVIDENCE)

**Scope:** Keep targeted queue-cycle tests green; no `src/` product edits unless a test fix is required.

**Commands (witness):**

```bash
python -m pytest -q tests/test_queue_cycle_contract.py tests/test_queue_cycle_stops_on_blocked.py
python scripts/run_queue_cycle.py --dry-run --repo-root .
```

**Touch set:** `tests/test_queue_cycle_*.py`, `scripts/queue_cycle.py`, `scripts/run_queue_cycle.py` only.

---

### QueueInfra-Closeout-Slice003 — chapter close (CONTROL)

**Scope:** Close chapter in evidence; ensure `MVP1_FRONTIER` / `HANDOFF` pointers mention queue cycle operator path if closeout job updates them.

**Evidence:** [`QUEUE_INFRA_SMOKE_EVIDENCE_STATUS.md`](QUEUE_INFRA_SMOKE_EVIDENCE_STATUS.md).

---

## Sprint status

**Queue infra smoke:** **IN PROGRESS** (queued 2026-05-26).
