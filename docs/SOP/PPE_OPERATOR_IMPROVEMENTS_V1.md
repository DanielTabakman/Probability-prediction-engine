# PPE operator improvements v1 — tracker

**Plane:** CONTROL-PLANE. **Purpose:** trace Paperclip-inspired follow-ups (backlog + ship status).

Cross-refs: [`PPE_OPERATOR_MAP_V1.md`](PPE_OPERATOR_MAP_V1.md) · [`SPRINT_PPE_OPERATOR_VISIBILITY_V1.md`](SPRINT_PPE_OPERATOR_VISIBILITY_V1.md)

---

## Status

| # | Improvement | Status | Where |
|---|-------------|--------|-------|
| 1 | `BLOCKERS.md` auto-generator | **Shipped** (Slice002) | `scripts/ppe_operator_blockers.py` |
| 2 | Phone inbox line in ntfy | **Shipped** (Slice002) | `ppe_operator_status.py` → notify payload |
| 3 | Skip pre-closed Slice001 | **Shipped** (Slice002) | `preCompletedSliceIds` in phase plan |
| 4 | Merge + desktop pull | **Ops** | `git pull` / loop `gitSync`; merge PR when CI green |
| 5 | Cost/lane tags in workflow metrics | **Shipped** (Slice002) | `workflow_metrics_cli.py slice close --worker-lane` |
| 6 | Static operator dashboard (HTML vs MD) | **Backlog** | [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) → `ppe_operator_html_dashboard_eval` |
| 7 | Priority-aware auto-select | **Shipped** (Slice002) | `ppe_auto_select.choose_next_plan` |
| 8 | Stale `ACTIVE_IDE_SLICE` guard | **Shipped** (Slice002) | inbox warning + ntfy `stale_checkout` |

---

## Usage (new)

```bat
python scripts/ppe_operator_status.py
type artifacts\orchestrator\BLOCKERS.md

python scripts/workflow_metrics_cli.py slice close --slice-id MySlice --size S --roundtrips 2 --worker-lane IDE
```

Stale checkout threshold: `PPE_ACTIVE_SLICE_STALE_HOURS` (default 24).

---

## Item 6 — HTML dashboard (deferred)

See backlog row `ppe_operator_html_dashboard_eval`. Evaluate only if markdown inbox + `BLOCKERS.md` prove insufficient on phone/desktop.
